"""Defines `MarketDatasource` and supporting classes."""


__copyright__ = 'Copyright © 2019, Erik Anderson, James Abernathy, and Tyler Gerritsen'
__license__ = 'MIT'


import typing
import datetime


# TODO: Events:
#           MARKET_DATASOURCE_CAN_CONFIRM_UPDATED,
#           MARKET_DATASOURCE_CONFIRMATION_UPDATED,
#           MARKET_DATASOURCE_MODE_CHANGED,
#           MARKET_DATASOURCE_STOCK_SYMBOL_ADD_LIVE_ERROR,
#           MARKET_DATASOURCE_STOCK_SYMBOL_REMOVED

class AlphaVantageApiKeyMissingError(RuntimeError):
    """An exception raised when attempting to access Alpha Vantage
    without specifying an API key.
    """
    pass


class DatasourceConfirmedError(RuntimeError):
    """An exception raised when the datasource has already been
    confirmed and a configuration attempt has been made.
    """
    pass


class DatasourcesMissingError(RuntimeError):
    """An exception raised when using this `MarketDatasource`'s
    `.confirm()` method if no stock symbols have been added yet.
    """
    pass


class WrongModeError(RuntimeError):
    """An exception raised when the module attempts to add stock symbols
    with an invalid method for the current mode.
    """
    pass


class MarketDatasource:
    """Depending on the source, this component has the ability to
    collate data and pass it to the SimModel. If the source is live,
    an API key is used to connect to Alpha Vantage to retrieve the
    newest stock information. If the source is offline, data is
    gathered from historical JSON files. Any pertinent datasource
    changes are broadcasted to the Window View module.
    """

    def __init__(self) -> None:
        """Initialize with no starting stock symbols."""
        pass


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
        pass


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
        pass


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
        pass


    def confirm(self) -> None:
        """Disable the ability to add or remove stock symbols and
        enable this `MarketDatasource` to use its `.get_next_prices()`
        function. May only be called if this `MarketDatasource`'s
        datasource is prepared to be read. If no stock symbols have
        been added, raise a `MarketDatasource.DatasourcesMissingError`
        exception. If no API key has been set in “`LIVE`" mode, raises a
        `MarketDatasource.AlphaVantageApiKeyMissingError` exception.
        """
        pass


    def get_live_api_key(self) -> typing.Optional[str]:
        """Return a string containing the currently configured Alpha
        Vantage API key, or `None` if it has not yet been specified.
        """
        pass


    def get_mode(self) -> str:
        """Return a string that signifies which mode is in use. The
        modes can be either “`LIVE`" or “`ARCHIVE`".
        """
        pass


    def get_next_prices(self
    ) -> typing.Optional[(datetime.datetime, typing.Dict[str, float])]:

        """A blocking call: Return `None` if this datasource hasn't
        begun yet or if no more prices are left in the datasource.

        Otherwise halt until a new batch of prices has been
        collected. Getting the next data in “`LIVE`" mode in
        particular may be slow, so query it from a background thread.
        """
        pass


    def get_stock_symbols(self) -> typing.List[str]:
        """Return a list of strings for each stock symbol that has
        been added. The list should change after the following two
        events: `MARKET_DATASOURCE_STOCK_SYMBOL_ADDED` and
        `MARKET_DATASOURCE_STOCK_SYMBOL_REMOVED`.
        """
        pass


    def is_confirmed(self) -> bool:
        """Return `True` if this `MarketDatasource`'s datasource is
        ready to be read. Otherwise return `False`.
        """
        pass


    def remove_stock_symbol(self,
        stock_symbol: str
    ) -> None:
        """Remove a stock symbol whose name matches the passed
        string. If called after the datasource has already been
        confirmed, throw a `MarketDatasource.DatasourceConfirmedError`
        exception.
        """
        pass


    def set_live_api_key(self,
        api_key: str
    ) -> None:
        """Set the API key for Alpha Vantage access. If called after
        the datasource has already been confirmed, throw a
        `MarketDatasource.DatasourceConfirmedError` exception.
        """
        pass


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
        pass


    def unconfirm(self) -> None:
        """Enable the ability to add or remove stock symbols and
        prevent this `MarketDatasource`'s ability to use its
        `.get_next_prices()` function.
        """
        pass
