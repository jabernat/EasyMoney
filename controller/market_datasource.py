"""Defines `MarketDatasource` and supporting classes."""


__copyright__ = 'Copyright © 2019, Erik Anderson, James Abernathy, and Tyler Gerritsen'
__license__ = 'MIT'


import typing
import datetime
import json
import urllib.request


# TODO: Events:
#           MARKET_DATASOURCE_CAN_CONFIRM_UPDATED,
#           MARKET_DATASOURCE_CONFIRMATION_UPDATED,
#           MARKET_DATASOURCE_LIVE_API_KEY_UPDATED,
#           MARKET_DATASOURCE_MODE_CHANGED,
#           MARKET_DATASOURCE_STOCK_SYMBOL_ADD_ARCHIVE_ERROR,
#           MARKET_DATASOURCE_STOCK_SYMBOL_ADD_LIVE_ERROR,
#           MARKET_DATASOURCE_STOCK_SYMBOL_ADDED
#           MARKET_DATASOURCE_STOCK_SYMBOL_REMOVED

class AlphaVantageApiKeyMissingError(RuntimeError):
    """An exception raised when attempting to access Alpha Vantage
    without specifying an API key.
    """

    callingFunction: str
    """A string representing the function this error was raised from."""

    def __init__(self,
         callingFunction: str
     ) -> None:
        self.callingFunction = callingFunction
        super().__init__('Cannot access Alpha Vantage when no API key '
                         'has been set. Calling function: ' +
                         callingFunction)


class DatasourceConfirmedError(RuntimeError):
    """An exception raised when the datasource has already been
    confirmed and a configuration attempt has been made.
    """

    configuration_type: str
    """A string representing which type of configuration that raised 
    this error.
    """

    def __init__(self,
         configuration_type: str
     ) -> None:
        self.configuration_type = configuration_type
        super().__init__('Cannot perform configuration when '
                         'datasource has been confirmed. '
                         'Attempted configuration: ' +
                         configuration_type)


class DatasourcesMissingError(RuntimeError):
    """An exception raised when using this `MarketDatasource`'s
    `.confirm()` method if no stock symbols have been added yet.
    """

    def __init__(self) -> None:

        super().__init__('Cannot confirm with empty symbol list.')


class WrongModeError(RuntimeError):
    """An exception raised when the module attempts to add stock symbols
    with an invalid method for the current mode.
    """

    wrongMode: str
    """The invalid simulation mode."""

    correctMode: str
    """The mode the simulation should be in."""

    def __init__(self,
        wrong_mode: str,
        correct_mode: str
    ) -> None:
        self.wrongMode = wrong_mode
        self.correctMode = correct_mode
        if wrong_mode is None:
            wrong_mode = 'None'
        super().__init__(
            'Cannot perform add_stock_symbol_{} function in "{}" '
            'mode.'.format(correct_mode, wrong_mode))


class MarketDatasource(object):
    """Depending on the source, this component has the ability to
    collate data and pass it to the SimModel. If the source is live,
    an API key is used to connect to Alpha Vantage to retrieve the
    newest stock information. If the source is offline, data is
    gathered from historical JSON files. Any pertinent datasource
    changes are broadcasted to the Window View module.
    """

    _mode: str
    """A string representing the current mode of the simulation. Can 
    be `LIVE` or `ARCHIVE`.
    """

    _symbols: typing.List[str]
    """A list of all symbols to be monitored in this simulation."""

    _symbol_data: typing.List[typing.Tuple[datetime.datetime,
                                           typing.Dict[str, float]]]
    """A list of data for symbols, added in either mode."""
    _api_key: typing.Optional[str]
    """A string that represents the Alpha Vantage API key."""

    _confirmed: bool
    """A boolean indicating the user has confirmed the datasource."""

    _time: datetime.datetime
    """The current time of the simulation"""

    def __init__(self) -> None:
        """Initialize with no starting stock symbols."""
        self._mode = 'ARCHIVE'
        self._symbols = []
        self._symbol_data = []
        self._api_key = None
        self._confirmed = False


    def add_stock_symbol_archive(self,
        json_filename: str
    ) -> None:
        """Load a JSON file with a name `json_filename` for an
        individual stock symbol. If the file is for a stock symbol
        which has already been added, the data for the previously added
        symbol is replaced.

        May raise the following exceptions for failed preconditions:
        `MarketDatasource.WrongModeError` if this datasource isn't in
        archive mode, and `MarketDatasource.DatasourceConfirmedError` if
        the datasource has already been confirmed.

        If this call succeeds at first, fire one of two events:
        `MARKET_DATASOURCE_STOCK_SYMBOL_ADDED` if successful, or
        `MARKET_DATASOURCE_STOCK_SYMBOL_ADD_ARCHIVE_ERROR` if an
        error occurs.
        """

        if self._mode == 'ARCHIVE':
            if not self.is_confirmed():
                with open(json_filename) as json_file:
                    data = json.load(json_file)
                    stock_symbol: str = data['Meta Data']['2. Symbol']
                    if 'NYSE:' + stock_symbol in self._symbols:
                        self._symbol_data.clear()
                    else:
                        self._symbols.append('NYSE:' + stock_symbol)
                    time: datetime.datetime
                    for p in data['Time Series (5min)']:
                        time = datetime.datetime.strptime(p, '%Y-%m-%d %H:%M:%S')
                        close_price: float = data['Time Series (5min)'][p]['4. close']
                        self._symbol_data.extend([(time, {stock_symbol:
                                                        close_price})])
            else:
                raise DatasourceConfirmedError(
                    'MarketDatasource.add_stock_symbol_archive()')
        else:
            raise WrongModeError(self._mode, 'ARCHIVE')


    def add_stock_symbol_live(self,
        stock_symbol: str
    ) -> None:
        """Query Alpha Vantage to confirm it has data for
        `stock_symbol`. An example of a valid stock symbol is
        "`NYSE:MSFT`", representing Microsoft stock on the New York
        Stock Exchange.

        May raise the following exceptions for failed preconditions:
        `MarketDatasource.AlphaVantageApiKeyMissingError` if an API
        key has not yet been set, `MarketDatasource.WrongModeError`
        if this datasource is not in live mode,
        and `MarketDatasource.DatasourceConfirmedError` if this data
        source is already confirmed.

        If this call succeeds at first, fire one of two main events:
        `MARKET_DATASOURCE_STOCK_SYMBOL_ADDED` if successfully added, or
        `MARKET_DATASOURCE_STOCK_SYMBOL_ADD_LIVE_ERROR` if
        `stock_symbol` could not be found on Alpha Vantage.
        """
        if self._api_key is not None:
            if self._mode == 'LIVE':
                if not self.is_confirmed():
                    if 'NYSE:' + stock_symbol in self._symbols:
                        self._symbol_data.clear()
                    else:
                        self._symbols.append('NYSE:' + stock_symbol)
                    query_url = \
                        "https://www.alphavantage.co/query?function" \
                        "=TIME_SERIES_INTRADAY&symbol={" \
                        "SYMBOL}&interval=1min&outputsize=full&apikey={" \
                        "API_KEY}"
                    with urllib.request.urlopen(query_url.format(
                            SYMBOL=stock_symbol, API_KEY=self._api_key)) \
                            as json_file:
                        data = json.load(json_file)
                        time: datetime.datetime
                        for p in data['Time Series (1min)']:
                            time = datetime.datetime.strptime(p, '%Y-%m-%d %H:%M:%S')
                            close_price: float = \
                            data['Time Series (1min)'][p]['4. close']
                            self._symbol_data.extend([(time, {stock_symbol:
                                                                  close_price})])
                else:
                    raise DatasourceConfirmedError(
                        'MarketDatasource.add_stock_symbol_live()')
            else:
                raise WrongModeError(self._mode, 'LIVE')
        else:
            raise AlphaVantageApiKeyMissingError(
                'add_stock_symbol_live()')


    def can_confirm(self) -> bool:
        """If in archive mode, return `True` if there is at least one
        stock symbol added and there are no pending symbol additions
        from `MarketDatasource.add_stock_symbol_archive(…)`.

        If in live mode, return `True` if there is at least one stock
        symbol has been added, there are no pending symbol additions
        from `MarketDatasource.add_stock_symbol_live(…)`, and an API
        key has been set.

        Otherwise return `False`.
        """

        if len(self._symbols) > 0 and len(self._symbol_data) == 0:
            if self._mode == 'LIVE':
                if self._api_key is not None:
                    return True
                else:
                    return False
            else:
                return True
        else:
            return False


    def confirm(self) -> None:
        """Disable the ability to add or remove stock symbols and
        enable this `MarketDatasource` to use its `.get_next_prices()`
        function. May only be called if this `MarketDatasource`'s
        datasource is prepared to be read. If no stock symbols have
        been added, raise a `MarketDatasource.DatasourcesMissingError`
        exception. If no API key has been set in “`LIVE`" mode, raises a
        `MarketDatasource.AlphaVantageApiKeyMissingError` exception.
        """

        if not len(self._symbols) == 0:
            if self._mode == 'LIVE' and self._api_key is None:
                raise AlphaVantageApiKeyMissingError(
                    'MarketDatasource.confirm()')
            else:
                self._confirmed = True
        else:
            raise DatasourcesMissingError()


    def get_live_api_key(self) -> typing.Optional[str]:
        """Return a string containing the currently configured Alpha
        Vantage API key, or `None` if it has not yet been specified.
        """
        return self._api_key


    def get_mode(self) -> str:
        """Return a string that signifies which mode is in use. The
        modes can be either “`LIVE`" or “`ARCHIVE`".
        """
        return self._mode


    def get_next_prices(self
    ) -> typing.Optional[typing.Tuple[datetime.datetime,typing.Dict[str, float]]]:
        """A blocking call: Return `None` if this datasource hasn't
        begun yet or if no more prices are left in the datasource.

        Otherwise halt until a new batch of prices has been
        collected. Getting the next data in “`LIVE`" mode in
        particular may be slow, so query it from a background thread.
        """
        if len(self._symbol_data) == 0:
            return None
        else:
            return self._symbol_data.pop()


    def get_stock_symbols(self) -> typing.List[str]:
        """Return a list of strings for each stock symbol that has
        been added. The list should change after the following two
        events: `MARKET_DATASOURCE_STOCK_SYMBOL_ADDED` and
        `MARKET_DATASOURCE_STOCK_SYMBOL_REMOVED`.
        """
        return self._symbols


    def is_confirmed(self) -> bool:
        """Return `True` if this `MarketDatasource`'s datasource is
        ready to be read. Otherwise return `False`.
        """
        return self._confirmed


    def remove_stock_symbol(self,
        stock_symbol: str
    ) -> None:
        """Remove a stock symbol whose name matches the passed
        string. If called after the datasource has already been
        confirmed, throw a `MarketDatasource.DatasourceConfirmedError`
        exception.
        """
        if not self.is_confirmed():
            self._symbols.remove(stock_symbol)
        else:
            raise DatasourceConfirmedError(
                'MarketDatasource.remove_stock_symbol('
                                           + stock_symbol + ')')


    def set_live_api_key(self,
        api_key: str
    ) -> None:
        """Set the API key for Alpha Vantage access. If called after
        the datasource has already been confirmed, throw a
        `MarketDatasource.DatasourceConfirmedError` exception.
        """
        if not self.is_confirmed():
            self._api_key = api_key
        else:
            raise DatasourceConfirmedError(
                'MarketDatasource.set_live_api_key().')


    def set_mode(self,
        mode: str
    ) -> None:
        """Given a string, set which datasource will be used. The new
        mode must be either of the two strings “`LIVE`" or
        “`ARCHIVE`". If the datasource has not been confirmed and the
        mode is changed, the list of added stock symbols is cleared. If
        the datasource has been confirmed and this method is called,
        throw a `MarketDatasource.DatasourceConfirmedError` exception.
        """
        if not mode == self._mode:
            if not self.is_confirmed():
                self._mode = mode
                self._symbols.clear()
            else:
                raise DatasourceConfirmedError(
                    'MarketDatasource.set_mode(' + mode + ')')

    def unconfirm(self) -> None:
        """Enable the ability to add or remove stock symbols and
        prevent this `MarketDatasource`'s ability to use its
        `.get_next_prices()` function.
        """
        self._confirmed = False
