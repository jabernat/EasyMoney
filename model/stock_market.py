"""Defines `StockMarket` and supporting classes."""


__copyright__ = 'Copyright © 2019, Erik Anderson, James Abernathy, and Tyler Gerritsen'
__license__ = 'MIT'


import bisect
import datetime
import typing

import dispatch




class InvalidSharePriceError(ValueError):
    """An exception raised when attempting to add a non-positive share price.
    """

    stock_symbol: str
    """The stock symbol that failed to be added."""

    price: float
    """The invalid non-positive share price that was rejected."""

    def __init__(self,
        stock_symbol: str,
        price: float
    ) -> None:
        self.stock_symbol = stock_symbol
        self.price = price
        super().__init__('Stock {!r} share price must be positive.'.format(
            stock_symbol))


class NonconsecutiveTimeError(ValueError):
    """An exception raised when attempting to add a new sampling of prices that
    doesn't follow the previous one. This includes the case of adding a
    duplicate time.
    """

    time: datetime.datetime
    """The invalid time of prices that could not be added."""

    time_previous: datetime.datetime
    """The most recent time that new entries must precede."""

    def __init__(self,
        time: datetime.datetime,
        time_previous: datetime.datetime
    ) -> None:
        self.time = time
        self.time_previous = time_previous
        super().__init__('Cannot add non-consecutive prices at time {} '
            'following previous time {}.'.format(
                time, time_previous))


class StockSymbolMissingError(ValueError):
    """An exception raised when an attempt to add new stock price readings left
    out a previously-added symbol.
    """

    symbols_old: typing.Set[str]
    """The set of all expected stock symbols that were included in past data.
    """

    symbols_new: typing.Set[str]
    """The set of stock symbols that could not be added because one or more
    symbols from `symbols_old` was omitted.
    """

    def __init__(self,
        symbols_old: typing.Set[str],
        symbols_new: typing.Set[str]
    ) -> None:
        self.symbols_old = symbols_old
        self.symbols_new = symbols_new

        if symbols_old:
            error = ('Cannot omit existing stocks when adding new prices: '
                'Missing {:s}.'.format(
                    ', '.join(repr(symbol)
                        for symbol in sorted(symbols_old - symbols_new))))
        else:  # First addition
            error = ('Must include at least one stock symbol price for the '
                'first stock market reading.')
        super().__init__(error)


class StockSymbolUnrecognizedError(ValueError):
    """An exception raised when referencing an unrecognized stock symbol.
    """

    stock_symbol: str
    """The requested stock symbol that could not be found."""

    def __init__(self,
        stock_symbol: str
    ) -> None:
        self.stock_symbol = stock_symbol
        super().__init__('Stock symbol {!r} not included in the market.'.format(
            stock_symbol))




class StockMarket(dispatch.Dispatcher):
    """A component of `SimModel` that stores a time series of stock share
    prices accumulated over simulation runs. To begin a new simulation, the
    stock market can be reset.
    """


    _price_times: typing.List[datetime.datetime]
    """A `list` of times for the price readings stored in `_symbol_prices`."""

    _symbol_prices: typing.Dict[str, typing.List[float]]
    """A `dict` of included stock symbols mapped to `list`s of recorded prices
    corresponding to insertion times within `_price_times`.
    """

    EVENTS: typing.ClassVar[typing.FrozenSet[str]] = frozenset([
        'STOCKMARKET_ADDITION',
        'STOCKMARKET_CLEARED'])
    """Events broadcast by instances of the `StockMarket`."""


    def __init__(self
    ) -> None:
        """Initialize this `StockMarket` with no stock price readings."""
        self._price_times = []
        self._symbol_prices = {}


    def clear(self
    ) -> None:
        """Remove all previously-added price data from this `StockMarket`.

        Always triggers `STOCKMARKET_CLEARED`.
        """
        # Always trigger, so that Traders can reliably react by also resetting
        #if not self._price_times:
        #   return  # Nothing to clear

        self._price_times.clear()
        self._symbol_prices.clear()
        self.emit('STOCKMARKET_CLEARED',
            market=self)


    def add_next_prices(self,
        time: datetime.datetime,
        stock_symbol_prices: typing.Dict[str, float]
    ) -> None:
        """Add new price readings to this market's history.

        The new prices were sampled at `time`, which must follow the previously
        added sample chronologically. Attempting to add prices at a `time` that
        precedes or matches the previous reading raises
        `NonconsecutiveTimeError`.

        The `stock_symbol_prices` `dict` maps stock symbol keys to
        price-per-share values. All previously-added stock symbol prices should
        be provided, except on the first addition when at least one symbol is
        required; If these requirements are not met, this method raises
        `StockSymbolMissingError`. All price-per-share
        values must be positive, or `InvalidSharePriceError` will be raised.

        Triggers `STOCKMARKET_ADDITION` if successful.
        """
        # Validate prices
        for stock_symbol, price in stock_symbol_prices.items():
            if not price > 0:
                raise InvalidSharePriceError(stock_symbol, price)

        if not self._symbol_prices:  # First datapoint
            if not stock_symbol_prices:
                # Need at least one initial stock
                raise StockSymbolMissingError(set(), set())

            # Initialize storage
            for stock_symbol in stock_symbol_prices.keys():
                self._symbol_prices[stock_symbol] = []

        else:
            # Must include previously-seen symbols
            symbols_old = set(self._symbol_prices.keys())
            symbols_new = set(stock_symbol_prices.keys())
            if symbols_old != symbols_new:
                raise StockSymbolMissingError(symbols_old, symbols_new)

            # Times must be consecutive
            time_previous = self._price_times[-1]
            if not time > time_previous:
                raise NonconsecutiveTimeError(time, time_previous)

        # Save valid datapoint
        self._price_times.append(time)
        for stock_symbol, price in stock_symbol_prices.items():
            self._symbol_prices[stock_symbol].append(price)
        self.emit('STOCKMARKET_ADDITION',
            market=self,
            time=time,
            stock_symbol_prices=stock_symbol_prices)


    def _get_prices_at_index(self,
        index: int
    ) -> typing.Dict[str, float]:
        """Return a mapping of stock symbols to their prices per share at
        sample `index`.
        """
        
        return {stock_symbol: prices[index]
            for stock_symbol, prices in self._symbol_prices.items()}


    def get_prices(self,
        time: typing.Optional[datetime.datetime] = None
    ) -> typing.Optional[typing.Dict[str, float]]:
        """Return a `dict` mapping stock symbol keys to their price-per-share
        values that follow `time`, or `None` if no data had been added by that
        time. If `time` is `None`, the most recent prices are returned.
        """
        if time is None:  # Get most recent prices
            index = len(self._price_times)
        else:
            index = bisect.bisect_right(self._price_times, time)

        return (None if index == 0
            else self._get_prices_at_index(index - 1))


    def iter_prices(self
    ) -> typing.Iterator[typing.Tuple[datetime.datetime, typing.Dict[str, float]]]:
        """Return an iterator that yields times with `dict`s that map stock
        symbols to their prices in reverse chronological order. This iterator
        should be iterated immediately, as market changes will invalidate it.
        """
        for index, time in enumerate(reversed(self._price_times)):
            yield time, self._get_prices_at_index(index)


    def get_stock_symbol_price(self,
        stock_symbol: str
    ) -> float:
        """Return the most recent cost for one share of `stock_symbol`.

        If `stock_symbol` isn't included in this `StockMarket`, including when
        no prices have been added yet, raises `StockSymbolUnrecognizedError`.

        This result changes upon `STOCKMARKET_ADDITION` and
        `STOCKMARKET_CLEARED` events.
        """
        try:
            return self._symbol_prices[stock_symbol][-1]

        except KeyError as e:
            raise StockSymbolUnrecognizedError(stock_symbol) from e
