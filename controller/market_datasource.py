"""Defines `MarketDatasource` and supporting classes."""


__copyright__ = 'Copyright © 2019, Erik Anderson, James Abernathy, and Tyler Gerritsen'
__license__ = 'MIT'


import datetime
import json
import typing

import dispatch




class SymbolPrice(typing.NamedTuple):
    """A single stock symbol's price datapoint at a given time."""
    time: datetime.datetime
    price: float


class CombinedPrices(typing.NamedTuple):
    """The combined prices of all stock symbols at a given time."""
    time: datetime.datetime
    prices: typing.Dict[str, float]




class DatasourceConfirmedError(RuntimeError):
    """An exception raised when attempting to configure the datasource after it
    has already been confirmed.
    """
    def __init__(self
    ) -> None:
        super().__init__(
            'Cannot perform configuration when datasource is confirmed.')


class DatasourceUnconfirmedError(RuntimeError):
    """An exception raised when attempting to access datasource data before
    confirming it.
    """
    def __init__(self
    ) -> None:
        super().__init__(
            'Cannot access stock price data before datasource is confirmed.')


class DatasourcesMissingError(RuntimeError):
    """An exception raised when attempting to confirm before adding any stock
    symbols.
    """
    def __init__(self
    ) -> None:
        super().__init__(
            'Cannot confirm without adding at least one stock symbol.')




class MarketDatasource(dispatch.Dispatcher):
    """This component has the ability to collate data and pass it to the
    `SimModel`. Data is gathered from archived Alpha Vantage JSON files. Before
    being confirmed, the data is separated. After confirmation, the data is
    combined.
    """

    _symbols_prices: typing.Dict[str, typing.List[SymbolPrice]]
    """A list of all symbols and their data, separated."""

    _confirmed: bool
    """`True` while the user has confirmed the datasource for iteration."""

    _combined_prices: typing.Optional[typing.List[CombinedPrices]]
    """A list that contains the combined data for all symbols in this
    simulation. Only set while `.is_confirmed()`.
    """

    _combined_prices_index: typing.Optional[int]
    """The index of the next entry in `._combined_prices` for
    `.get_next_prices()` to serve. Only set while `.is_confirmed()`.
    """

    EVENTS: typing.ClassVar[typing.FrozenSet[str]] = frozenset([
        'MARKETDATASOURCE_CAN_CONFIRM_UPDATED',
        'MARKETDATASOURCE_CONFIRMED',
        'MARKETDATASOURCE_UNCONFIRMED',
        'MARKETDATASOURCE_STOCK_SYMBOL_ADDED',
        'MARKETDATASOURCE_STOCK_SYMBOL_REMOVED'])
    """Events broadcast by instances of the `MarketDatasource`."""


    def __init__(self
    ) -> None:
        """Initialize unconfirmed with no starting stock symbols."""
        self._symbols_prices = {}
        self._confirmed = False

        self._combined_prices = None
        self._combined_prices_index = None


    def get_stock_symbols(self
    ) -> typing.List[str]:
        """Return a list of added stock symbol names. This result changes
        following the `MARKETDATASOURCE_STOCK_SYMBOL_ADDED` and
        `MARKETDATASOURCE_STOCK_SYMBOL_REMOVED` events.
        """
        return list(self._symbols_prices.keys())

    def add_stock_symbol(self,
        json_filename: str
    ) -> None:
        """Load a JSON file with filename `json_filename` containing data for
        an individual stock symbol. If the file is for a stock symbol which has
        already been added, the data for the previously added symbol is
        replaced.

        Raises `DatasourceConfirmedError` if the datasource has already been
        confirmed.

        Fires `MARKETDATASOURCE_STOCK_SYMBOL_ADDED` if successful.
        Fires `MARKETDATASOURCE_CAN_CONFIRM_UPDATED` if adding the first stock
        symbol.
        """
        if self.is_confirmed():
            raise DatasourceConfirmedError()

        with open(json_filename, encoding='utf_8') as json_file:
            json_contents = json_file.read()

        stock_symbol, symbol_prices = self._parse_alpha_vantage_json(
            json_contents)
        # Replace existing data
        self._symbols_prices[stock_symbol] = symbol_prices

        self.emit('MARKETDATASOURCE_STOCK_SYMBOL_ADDED',
            datasource=self,
            stock_symbol=stock_symbol)
        if len(self._symbols_prices) == 1:
            # Added first stock symbol
            self.emit('MARKETDATASOURCE_CAN_CONFIRM_UPDATED',
                datasource=self)

    def remove_stock_symbol(self,
        stock_symbol: str
    ) -> None:
        """Remove the given `stock_symbol` from this datasource while
        unconfirmed. Raises `DatasourceConfirmedError` if already confirmed.

        Fires `MARKETDATASOURCE_STOCK_SYMBOL_REMOVED` if successful.
        Fires `MARKETDATASOURCE_CAN_CONFIRM_UPDATED` if removing the last stock
        symbol.
        """
        if self.is_confirmed():
            raise DatasourceConfirmedError()

        del self._symbols_prices[stock_symbol]

        self.emit('MARKETDATASOURCE_STOCK_SYMBOL_REMOVED',
            datasource=self,
            stock_symbol=stock_symbol)
        if not self._symbols_prices:
            # Removed last stock symbol
            self.emit('MARKETDATASOURCE_CAN_CONFIRM_UPDATED',
                datasource=self)


    def _parse_alpha_vantage_json(self,
       json_contents: str
    ) -> typing.Tuple[str, typing.List[SymbolPrice]]:
        """Parse an Alpha Vantage `TIME_SERIES_INTRADAY` JSON result for its
        contained stock symbol and price data.
        """
        json_data = json.loads(json_contents)

        stock_symbol = json_data['Meta Data']['2. Symbol']
        interval = json_data['Meta Data']['4. Interval']
        time_series = json_data['Time Series (' + interval + ')']

        symbol_prices = []
        for time_index in time_series:
            time: datetime.datetime = datetime.datetime.strptime(
                time_index, '%Y-%m-%d %H:%M:%S')
            close_price = float(time_series[time_index]['4. close'])

            symbol_prices.append(
                SymbolPrice(time=time, price=close_price))

        # JSON data came in reverse-chronological order
        symbol_prices.reverse()

        return stock_symbol, symbol_prices


    def _combine_confirmed_data(self
    ) -> None:
        """Combine data for all symbols in the simulation. If there are any
        times that are missing price data for a certain symbol, maintain the
        most recent data for that symbol.
        """
        '''
        TODO: Rewrite so that it automatically filters out segments missing
        data from some stock symbols.

        If this algorithm is too slow, use a merge-sort to join all
        `SymbolPrices` lists, using the previous `dict` of prices as the base
        for each successive entry to simultaneously fill in holes.
        '''
        assert self._combined_prices is None, 'Prices already combined'

        # First add all available data
        combined_prices: typing.List[CombinedPrices] = []
        for stock_symbol, symbol_prices in self._symbols_prices.items():
            for symbol_price in symbol_prices:
                self._combine_stock_price(combined_prices,
                    symbol_price.time, stock_symbol, symbol_price.price)

        # Next fill in any data holes
        for index, prices in enumerate(combined_prices):
            if index == 0:
                continue

            # Check if each symbol is present
            for symbol in self._symbols_prices.keys():
                if (symbol not in prices.prices
                    and symbol in combined_prices[index - 1].prices
                ):
                    # Carry old price over to fill in gap
                    previous_price = combined_prices[index - 1].prices[symbol]
                    prices.prices[symbol] = previous_price

        # Save combined list
        self._combined_prices = combined_prices

    def _combine_stock_price(self,
        combined_prices: typing.List[CombinedPrices],
        time: datetime.datetime,
        stock_symbol: str,
        price: float
    ) -> None:
        """Given a `time`, `stock_symbol`, and `price`, update the running list
        of `combined_prices` in chronological order. If there is already an
        entry at the given `time`, add the new stock price to the existing
        entry.
        """
        new_price = CombinedPrices(time=time, prices={stock_symbol: price})

        for index, prices in enumerate(combined_prices):
            if time < prices.time:
                combined_prices.insert(index, new_price)
                return
            elif time == prices.time:
                prices.prices.update(new_price.prices)
                return

        # Otherwise element is not present, add to end of list
        combined_prices.append(new_price)


    def _find_start_index(self
    ) -> None:
        """Set the index at which all monitored symbols in `._combined_prices`
        have recorded prices.
        """
        assert self._combined_prices is not None, 'Combined prices missing'

        num_symbols = len(self._symbols_prices)
        for index, combined_prices in enumerate(self._combined_prices):
            if len(combined_prices.prices) == num_symbols:
                self._combined_prices_index = index
                return

        # Otherwise, there are no complete datapoints with all prices
        self._combined_prices_index = len(self._combined_prices)


    def can_confirm(self
    ) -> bool:
        """Return `True` if there is at least one stock symbol added."""
        return bool(self._symbols_prices)
        # TODO: Check for at least one data point

    def is_confirmed(self
    ) -> bool:
        """Return `True` if this `MarketDatasource`'s data is ready to be read.
        Otherwise return `False`.
        """
        return self._confirmed

    def confirm(self
    ) -> None:
        """Disable adding or removing stock symbols to this datasource, and
        enable access to its data. Can only be called if `.can_confirm()` is
        `True`. Otherwise if no stock symbols have been added, raises
        `DatasourcesMissingError`.
        """
        if self.is_confirmed():
            return

        if not self._symbols_prices:
            raise DatasourcesMissingError()

        self._combine_confirmed_data()
        self._find_start_index()
        self._confirmed = True

        self.emit('MARKETDATASOURCE_CONFIRMED',
            datasource=self)

    def unconfirm(self
    ) -> None:
        """Enable adding or removing stock symbols to the datasource, but
        prevent access to its data.
        """
        if not self.is_confirmed():
            return

        self._confirmed = False
        self._combined_prices = None
        self._combined_prices_index = None

        self.emit('MARKETDATASOURCE_UNCONFIRMED',
            datasource=self)


    def get_next_prices(self
    ) -> typing.Optional[typing.Tuple[datetime.datetime, typing.Dict[str, float]]]:
        """Return the next time and set of prices from this datasource, or
        `None` if no more remain. Raises `DatasourceUnconfirmedError` if this
        datasource isn't yet confirmed.
        """
        if not self.is_confirmed():
            raise DatasourceUnconfirmedError()
        assert self._combined_prices is not None, 'Combined prices missing'
        assert self._combined_prices_index is not None, 'Prices index missing'

        if self._combined_prices_index >= len(self._combined_prices):
            return None  # Out of data

        next_prices = self._combined_prices[self._combined_prices_index]
        self._combined_prices_index += 1
        return next_prices
