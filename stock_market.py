#!/usr/bin/env python3
"""Defines `StockMarket` and supporting classes."""


__copyright__ = 'Copyright © 2019, Erik Anderson, James Abernathy, and Tyler Gerritsen'
__license__ = 'MIT'


import datetime
import typing




class InvalidSharePriceError(ValueError):
    """An exception raised when attempting to add a non-positive share price.
    """
    pass


class NonconsecutiveTimeError(ValueError):
    """An exception raised when attempting to add a new sampling of prices that
    doesn't follow the previous one. This includes the case of adding a
    duplicate time.
    """
    pass


class StockSymbolMissingError(ValueError):
    """An exception raised when attempting to add a sample of stock symbols, but
    did not include a previously added symbol.
    """
    pass


class StockSymbolUnrecognizedError(ValueError):
    """An exception raised when referencing an unrecognized stock symbol.
    """
    pass




class StockMarket(object):
    """The SimModel 's StockMarket sub-component stores a time-series of stock
    share prices that accumulates over the course of a simulation. Each sample
    includes its time and the prices-per-share of multiple stock symbols at that
    time. The stock market can be reset to begin a new simulation. Traders
    create accounts associated with a single StockMarket to do their trading.
    """


    #TODO: Events:
    #   STOCK_MARKET_ADDITION
    #   STOCK_MARKET_CLEARED


    def __init__(self
    ) -> None:
        """The stock market's constructor, which initializes it with no price data
        samples.
        """
        pass


    def clear(self
    ) -> None:
        """Removes all previously added price data from this StockMarket.
        """
        pass


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
        pass


    def get_prices(self,
        time: datetime.datetime
    ) -> typing.Optional[typing.Dict[str, float]]:
        """Returns a dictionary that maps stock symbol keys to price-per-share
        values following time , or None if no data has been added by that time
        yet.
        """
        pass


    def iter_prices(self
    ) -> typing.Iterable[datetime.datetime, typing.Dict[str, float]]:
        """Returns an iterator that repeatedly yields pairs of times and
        dictionaries of stock symbols' prices at those times.
        This iterator should be iterated immediately, as market changes will
        invalidate it.
        """
        pass
