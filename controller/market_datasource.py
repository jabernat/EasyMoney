"""Defines `MarketDatasource` and supporting classes."""


__copyright__ = 'Copyright © 2019, Erik Anderson, James Abernathy, and Tyler Gerritsen'
__license__ = 'MIT'


import typing
import datetime
import json
import dispatch


class SymbolPrice(typing.NamedTuple):
    time: datetime.datetime
    price: float


class CombinedPrices(typing.NamedTuple):
    time: datetime.datetime
    prices: typing.Dict[str, float]


class DatasourceConfirmedError(RuntimeError):
    """An exception raised when the datasource has already been
    confirmed and a configuration attempt has been made.
    """
    def __init__(self,
    ) -> None:
        super().__init__('Cannot perform configuration when '
                         'datasource has been confirmed.')


class DatasourcesMissingError(RuntimeError):
    """An exception raised when using this `MarketDatasource`'s
    `.confirm()` method if no stock symbols have been added yet.
    """

    def __init__(self) -> None:

        super().__init__('Cannot confirm with empty symbol list.')


class MarketDatasource(dispatch.Dispatcher):
    """This component has the ability to collate data and pass it to
    the SimModel. Data is gathered from historical JSON files. Before
    being confirmed, the data is separated. After confirmation,
    the data is combined.
    """

    _symbols_prices: typing.Dict[str, typing.List[typing.Tuple[
        datetime.datetime, float]]]
    """A list of all symbols and their data, separated."""

    _combined_prices: typing.List[typing.Tuple[datetime.datetime,
                                           typing.Dict[str, float]]]
    """A list that contains the combined data for all symbols in 
    this simulation.
    """

    _confirmed: bool
    """A boolean indicating the user has confirmed the datasource."""

    _current_time_index: int
    """An integer representing the index of _combined_prices time when 
    all symbols being to provide data. Is updated by 
    """

    EVENTS: typing.ClassVar[typing.List[str]] = [
        'MARKET_DATASOURCE_STOCK_SYMBOL_ADDED',
        'MARKET_DATASOURCE_CAN_CONFIRM_UPDATED',
        'MARKET_DATASOURCE_CONFIRMED',
        'MARKET_DATASOURCE_STOCK_SYMBOL_REMOVED',
        'MARKET_DATASOURCE_UNCONFIRMED']
    """Events broadcast by instances of the `MarketDatasource`."""

    def __init__(self) -> None:
        """Initialize with no starting stock symbols."""
        self._symbols_prices = {}
        self._combined_prices = []
        self._confirmed = False
        self._current_time_index = -1


    def add_stock_symbol(self,
        json_filename: str
    ) -> None:
        """Load a JSON file with a name `json_filename` for an
        individual stock symbol. If the file is for a stock symbol
        which has already been added, the data for the previously added
        symbol is replaced.

        May raise `MarketDatasource.DatasourceConfirmedError` if
        the datasource has already been confirmed.

        If this call succeeds, fire
        `MARKET_DATASOURCE_STOCK_SYMBOL_ADDED`.
        """
        if self.is_confirmed():
            raise DatasourceConfirmedError()
        with open(json_filename) as json_file:
            data = json.load(json_file)
        interval = data['Meta Data']['4. Interval']
        self._add_stock_json_data(data, interval)


    def _add_stock_json_data(self,
       data: dict,
       interval: str
    ) -> None:
        """Refresh or add stock data for a stock symbol in its
        separate data list.
        """
        stock_symbol = data['Meta Data']['2. Symbol']
        # Initialize dict for symbol
        self._symbols_prices[stock_symbol] = []

        for time_key in data['Time Series (' + interval + ')']:
            time: datetime.datetime = datetime.datetime.strptime(time_key,
                                              '%Y-%m-%d %H:%M:%S')
            close_price = float(
                data['Time Series (' + interval + ')'][time_key]['4. close'])

            symbol_price = SymbolPrice(time=time, price=close_price)
            self._symbols_prices[stock_symbol].insert(0, symbol_price)

        self.emit('MARKET_DATASOURCE_STOCK_SYMBOL_ADDED',
                  instance=self,
                  stock_symbol=stock_symbol)


    def _combine_data(self) -> None:
        """Combine data for all symbols in the simulation. If there are any
        times that are missing price data for a certain symbol, maintain the
        most recent data for that symbol.
        """
        # First add all available data
        for stock_symbol, data_list in self._symbols_prices.items():
            for symbol_price in data_list:
                time: datetime.datetime = symbol_price.time  # Raises error with mypy
                close_price: float = symbol_price.price  # Raises error with mypy
                self._add_stock_price_ascending(stock_symbol, time, close_price)
        # Next fill in any data holes
        for index, combined_prices in enumerate(self._combined_prices):
            # Loop through each (time, symbol dict) tuple
            for symbol in self._symbols_prices:
                # Loop through each symbol currently in simulation
                if index > 0:
                    if symbol not in combined_prices.prices and symbol in self._combined_prices[index - 1].prices: # Raises error with mypy
                        # symbol is not in current time but is in previous time
                        previous_price = self._combined_prices[index - 1][1][symbol]
                        combined_prices.prices[symbol] = previous_price # Raises error with mypy

    def _set_start_index(self) -> None:
        """Set the index at which all monitored symbols in _combined_prices
        start to show data
        """
        for index, time_and_data_dict in enumerate(self._combined_prices):
            if len(time_and_data_dict[1]) == len(self._symbols_prices):
                self._current_time_index = index
                return

                    
    def _add_stock_price_ascending(self,
        stock_symbol: str,
        time: datetime.datetime,
        close_price: float
    ) -> None:
        """Given a stock symbol, time, and close price, update the
        combined data list in ascending order. If there is already an
        entry for the given time, update the dictionary at that time
        appropriately.
        """

        combined_prices = CombinedPrices(time, {stock_symbol: close_price})

        for index, q in enumerate(self._combined_prices):
            if time < q.time:  # Raises error with mypy
                self._combined_prices.insert(index, combined_prices)
                return
            elif time == q.time:  # Raises error with mypy
                q.prices.update({stock_symbol: close_price})  # Raises error with mypy
                return
        # Otherwise element is not present, add to end of list
        self._combined_prices.extend([combined_prices])


    def can_confirm(self) -> bool:
        """Return `True` if there is at least one stock symbol added and there
        are no pending symbol additions from `MarketDatasource.add_stock_symbol(…)`.

        Otherwise return `False`.
        """
        if not self._symbols_prices or self._current_time_index + 1 < len(self._combined_prices):
            return False
        self.emit('MARKET_DATASOURCE_CAN_CONFIRM_UPDATED',
                  instance=self)
        return True


    def confirm(self) -> None:
        """Disable the ability to add or remove stock symbols and
        enable this `MarketDatasource` to use its `.get_next_prices()`
        function. May only be called if this `MarketDatasource`'s
        datasource is prepared to be read. If no stock symbols have
        been added, raise a `MarketDatasource.DatasourcesMissingError`
        exception.
        """
        if self.is_confirmed():
            return
        if not self._symbols_prices:
            raise DatasourcesMissingError()
        self._combine_data()
        self._set_start_index()
        self._confirmed = True

        self.emit('MARKET_DATASOURCE_CONFIRMED',
                  instance=self)

    def get_next_prices(self
    ) -> typing.Optional[typing.Tuple[datetime.datetime, typing.Dict[str, float]]]:
        """A blocking call: Return `None` if this datasource hasn't
        begun yet or if no more prices are left in the datasource.

        Otherwise halt until a new batch of prices has been
        collected.
        """
        if not self._combined_prices:
            return None
        if self._current_time_index >= len(self._combined_prices):
            return None
        else:
            next_prices = self._combined_prices[self._current_time_index]
            self._current_time_index += 1
            return next_prices


    def get_stock_symbols_prices(self
    ) -> typing.Dict[str, typing.List[typing.Tuple[datetime.datetime, float]]]:
        """Return a list of strings for each stock symbol that has
        been added. The list should change after the following two
        events: `MARKET_DATASOURCE_STOCK_SYMBOL_ADDED` and
        `MARKET_DATASOURCE_STOCK_SYMBOL_REMOVED`.
        """
        return self._symbols_prices


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
        if self.is_confirmed():
            raise DatasourceConfirmedError()
        del self._symbols_prices[stock_symbol]
        self.emit('MARKET_DATASOURCE_STOCK_SYMBOL_REMOVED',
                  instance=self,
                  stock_symbol=stock_symbol)


    def _remove_stock_combined_prices(self,
        stock_symbol: str
    ) -> None:
        """Remove all data from _combined_prices for a given symbol."""
        for i in self._combined_prices:
            del i[1][stock_symbol]


    def unconfirm(self) -> None:
        """Enable the ability to add or remove stock symbols and
        prevent this `MarketDatasource`'s ability to use its
        `.get_next_prices()` function.
        """
        if not self.is_confirmed():
            return
        self._confirmed = False
        self._combined_prices = None  # Raises error with mypy
        self._current_time_index = -1

        self.emit('MARKET_DATASOURCE_UNCONFIRMED',
                  instance=self)
