#!/usr/bin/env python3
"""Defines `SimModel` and supporting classes."""


__copyright__ = 'Copyright © 2019, Erik Anderson, James Abernathy, and Tyler Gerritsen'
__license__ = 'MIT'


import typing

from stock_market import StockMarket
from trader import Trader




class TraderNameTakenError(ValueError):
    """An exception raised when attempting to add a new trader to the
    simulation using a name that is already taken by an existing `Trader`.
    """
    pass


class UnrecognizedAlgorithmError(ValueError):
    """An exception raised when a method expects the name of a known trading
    algorithm, but receives an unrecognized name argument.
    """
    pass




class SimModel(object):
    """The state of a simulated stock market along with the bank accounts and
    stock portfolios of participating traders. This high-level MVC model module
    broadcasts state update events to observers.
    """


    _stock_market: StockMarket
    _traders: typing.Dict[str, Trader]

    #TODO: Events:
    #   TRADER_ADDED
    #   TRADER_ALGORITHM_ADDED
    #   TRADER_REMOVED


    def __init__(self
    ) -> None:
        """Initialize with no stock market prices or participating traders."""
        pass


    def add_trader(self,
        name: str,
        initial_funds: float,
        trading_fee: float,
        algorithm: str,
        algorithm_settings: typing.Dict[str, typing.Any]
    ) -> Trader:
        """Addand return a uniquely named `Trader` to the simulation that will
        buy and sell in response to `StockMarket` updates based on `algorithm`.

        The new `Trader` and its settings will remain in this simulation until
        removed using `remove_trader`.

        If `name` is already taken by a participating `Trader`,
        `TraderNameTakenError` is raised.

        When this new trader creates a `TraderAccount`, its balance will start
        at `initial_funds`, measured in the same currency used by the
        `StockMarket`. If `initial_funds` is not positive, `InitialFundsError`
        is raised.

        The new trader must pay `trading_fee` to buy or sell through its
        created `TraderAccount`s. If `trading_fee` is negative,
        `TradingFeeError` is raised.

        The new trader’s named `algorithm` determines how it reacts to stock
        market changes and makes trading decisions. The specified algorithm
        must have already been registered with this `SimModel`; A list of
        registered names is available from `get_trader_algorithms`.
        Unrecognized algorithms raise `UnrecognizedAlgorithmError`.

        The contents of `algorithm_settings` are validated according to
        `algorithm`, and invalid arguments raise subclasses of `TypeError` and
        `ValueError`.
        """
        pass


    def add_trader_algorithm(self,
        trader_class: typing.Callable[..., Trader]
    ) -> None:
        """Add a new trader algorithm, which is represented by `trader_class`,
        a specialized implementation of `Trader`. This added `trader_class`'s
        name (see `Trader.get_algorithm_name`) becomes an available option for
        the `add_trader` factory method.
        """
        pass


    def get_stock_market(self
    ) -> StockMarket:
        """Return this simulation's `StockMarket` instance, which exposes its
        interfaces for reading, adding, and resetting stock market price data.
        """
        pass


    def get_trader_algorithm_settings_defaults(
        algorithm: str
    ) -> typing.Dict[str, typing.Any]:
        """Return a `dict` of default settings to use for new traders using the
        named `algorithm`. Its organization corresponds to the algorithm-
        specific result of `get_trader_algorithm_settings_ui_definition`.

        If the specified `algorithm` is not recognized, this function raises
        `UnrecognizedAlgorithmError`.
        """
        pass


    def get_trader_algorithm_settings_ui_definition(
        algorithm: str
    ) -> typing.Dict[str, typing.Any]:
        """Return a `dict` defining how the Kivy GUI toolkit can render the
        named `algorithm`'s configuration controls. The organization of this
        dictionary is defined by Kivy, and used exclusively by the
        `window_view` module.

        If the specified `algorithm` name is not recognized, this function
        raises `UnrecognizedAlgorithmError`.
        """
        pass


    def get_trader_algorithms(self
    ) -> typing.List[str]:
        """Return a `list` of registered trader algorithm names usable by
        participating traders.

        This result changes following the `TRADER_ALGORITHM_ADDED` event.
        """
        pass


    def get_traders(self
    ) -> typing.List[Trader]:
        """Return a `list` of the simulation's participating `Trader`s, which
        each expose their configuration and `TraderAccount` interfaces.

        This result changes following `TRADER_ADDED` and `TRADER_REMOVED`
        events.
        """
        pass


    def remove_trader(self,
        name: str
    ) -> None:
        """Remove a `Trader` from this `SimModel` by `name`.

        No error occurs if `name` does not exist.
        """
        pass


    def reset_market_and_trader_accounts(self
    ) -> None:
        """Clear this simulation model's `StockMarket` of old price data, and
        prompts all `Traders` to discard their `TraderAccount`s and create new
        ones.
        """
        pass
