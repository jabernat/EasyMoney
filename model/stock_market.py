"""Defines `StockMarket` and supporting classes."""


__copyright__ = 'Copyright © 2019, Erik Anderson, James Abernathy, and Tyler Gerritsen'
__license__ = 'MIT'


import bisect
import datetime
import typing




class InvalidSharePriceError(ValueError):
    """An exception raised when attempting to add a non-positive share price.
    """

    stock_symbol: str
    """"""

    price: float
    """"""

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
    """"""

    time_previous: datetime.datetime
    """"""

    def __init__(self,
        time: datetime.datetime,
        time_previous: datetime.datetime
    ) -> None:
        self.time = time
        self.time_previous = time_previous
        super().__init__(
            'Cannot add non-consecutive prices at time {} following previous time {}.'.format(
                time, time_previous))


class StockSymbolMissingError(ValueError):
    """An exception raised when attempting to add a sample of stock symbols, but
    did not include a previously added symbol.
    """

    symbols_old: typing.Set[str]
    """"""

    symbols_new: typing.Set[str]
    """"""

    def __init__(self,
        symbols_old: typing.Set[str],
        symbols_new: typing.Set[str]
    ) -> None:
        self.symbols_old = symbols_old
        self.symbols_new = symbols_new
        super().__init__(
            'Cannot omit previously-added stocks when adding new prices: Missing {:s}.'.format(
                ', '.join(repr(symbol)
                    for symbol in sorted(symbols_old - symbols_new))))


class StockSymbolUnrecognizedError(ValueError):
    """An exception raised when referencing an unrecognized stock symbol.
    """

    stock_symbol: str
    """"""

    def __init__(self,
        stock_symbol: str
    ) -> None:
        self.stock_symbol = stock_symbol
        super().__init__('Stock symbol {!r} not included in the market.'.format(
            stock_symbol))




class StockMarket(object):
    """The SimModel 's StockMarket sub-component stores a time-series of stock
    share prices that accumulates over the course of a simulation. Each sample
    includes its time and the prices-per-share of multiple stock symbols at that
    time. The stock market can be reset to begin a new simulation. Traders
    create accounts associated with a single StockMarket to do their trading.
    """


    _price_times: typing.List[datetime.datetime]
    """"""

    _symbol_prices: typing.Dict[str, typing.List[float]]
    """"""

    #TODO: Events:
    #   STOCK_MARKET_ADDITION
    #   STOCK_MARKET_CLEARED


    def __init__(self
    ) -> None:
        """The stock market's constructor, which initializes it with no price data
        samples.
        """
        self._price_times = []
        self._symbol_prices = {}


    def clear(self
    ) -> None:
        """Removes all previously added price data from this StockMarket.
        """
        self._price_times.clear()
        self._symbol_prices.clear()

        # TODO: Broadcast STOCK_MARKET_CLEARED


    def add_next_prices(self,
        time: datetime.datetime,
        stock_symbol_prices: typing.Dict[str, float]
    ) -> None:
        """Adds a new data-point to this stock market's history, including the time
        of the sample and the latest prices for each stock symbol.

        The new prices originated at time , which must follow the previously
        added sample chronologically. Invalid times raise
        StockMarket.NonconsecutiveTimeError exceptions.

        The stock_symbol_prices dictionary maps stock symbol keys to
        price-per-share values. Prices for all previously-added stock symbols
        must be given, except on the first addition when at least one symbol
        is required; If these requirements are not met, this method raises a
        StockMarket.StockSymbolMissingError exception. All price-per-share
        values must be positive, or a StockMarket.InvalidSharePriceError
        exception will be raised.
        """
        # Validate prices
        for stock_symbol, price in stock_symbol_prices:
            if not price > 0:
                raise InvalidSharePriceError(stock_symbol, price)

        if not self._symbol_prices:  # First datapoint
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
        for stock_symbol, price in stock_symbol_prices:
            self._symbol_prices[stock_symbol].append(price)

        # TODO: Broadcast STOCK_MARKET_ADDITION


    def _get_prices_at_index(self,
        index: int
    ) -> typing.Dict[str, float]:
        """
        """
        return {stock_symbol: prices[index]
            for stock_symbol, prices in self._symbol_prices}


    def get_prices(self,
        time: typing.Optional[datetime.datetime] = None
    ) -> typing.Optional[typing.Dict[str, float]]:
        """Returns a dictionary that maps stock symbol keys to price-per-share
        values following time , or None if no data has been added by that time
        yet.
        """
        if time is None:  # Get most recent prices
            index = len(self._price_times)
        else:
            index = bisect.bisect_right(self._price_times, time)

        if index:  # Time follows recorded data at (index - 1)
            return self._get_prices_at_index(index - 1)


    def iter_prices(self
    ) -> typing.Iterator[typing.Tuple[datetime.datetime, typing.Dict[str, float]]]:
        """Returns an iterator that repeatedly yields pairs of times and
        dictionaries of stock symbols' prices at those times.
        This iterator should be iterated immediately, as market changes will
        invalidate it.
        """
        for index, time in enumerate(self._price_times):
            yield time, self._get_prices_at_index(index)


    def get_stock_symbol_price(self,
        stock_symbol: str
    ) -> float:
        """
        """
        try:
            return self._symbol_prices[stock_symbol][-1]

        except KeyError as e:
            raise StockSymbolUnrecognizedError(stock_symbol) from e
