"""Defines `SimModel` and supporting classes."""


__copyright__ = 'Copyright © 2019, Erik Anderson, James Abernathy, and Tyler Gerritsen'
__license__ = 'MIT'


import typing

import dispatch

# Local package imports at end of file to resolve circular dependencies




class TraderNameTakenError(ValueError):
    """An exception raised when attempting to add a new trader to the
    simulation using a name that is already taken by an existing `Trader`.
    """

    name: str
    """The requested trader name that could not be re-used."""

    def __init__(self,
        name: str
    ) -> None:
        self.name = name
        super().__init__(
            'Trader name {!r} is already in use.'.format(name))


class UnrecognizedAlgorithmError(ValueError):
    """An exception raised when a method expects the name of a known trading
    algorithm, but receives an unrecognized name argument.
    """

    algorithm: str
    """The requested algorithm name that hadn't been registered."""

    def __init__(self,
        algorithm: str
    ) -> None:
        self.algorithm = algorithm
        super().__init__(
            'Unrecognized algorithm name {!r}.'.format(algorithm))




class SimModel(dispatch.Dispatcher):
    """The state of a simulated stock market along with the bank accounts and
    stock portfolios of participating traders. This high-level MVC model module
    broadcasts state update events to observers.
    """


    _trader_algorithms: typing.Dict[str, typing.Type['Trader']]
    """Registered `Trader` subclasses indexed by their algorithm names."""

    _stock_market: 'StockMarket'
    """This model's accumulated `StockMarket` price data."""

    _traders: typing.Dict[str, 'Trader']
    """Participating `Trader` subclass instances indexed by their names."""

    EVENTS: typing.ClassVar[typing.FrozenSet[str]] = frozenset([
        'SIMMODEL_TRADER_ADDED',
        'SIMMODEL_TRADER_ALGORITHM_ADDED',
        'SIMMODEL_TRADER_REMOVED'])
    """Events broadcast by the `SimModel`."""


    def __init__(self
    ) -> None:
        """Initialize with no stock market prices or participating traders."""
        self._trader_algorithms = {}

        self._stock_market = StockMarket()
        self._traders = {}

        # Add all known Trader implementations
        for trader_subclass in Trader.iter_subclasses():
            self.add_trader_algorithm(trader_subclass)


    def reset_market_and_trader_accounts(self
    ) -> None:
        """Clear this simulation model's `StockMarket` of old price data, and
        prompts all `Traders` to discard their `TraderAccount`s and create new
        ones.
        """
        self._stock_market.clear()
        # Traders react by creating new accounts


    def get_stock_market(self
    ) -> 'StockMarket':
        """Return this simulation's `StockMarket` instance, which exposes its
        interfaces for reading, adding, and resetting stock market price data.
        """
        return self._stock_market


    def get_trader_algorithms(self
    ) -> typing.List[str]:
        """Return a `list` of registered trader algorithm names usable by
        participating traders.

        This result changes following the `SIMMODEL_TRADER_ALGORITHM_ADDED`
        event.
        """
        return list(self._trader_algorithms.keys())

    def add_trader_algorithm(self,
        trader_class: typing.Type['Trader']
    ) -> None:
        """Add a new trader algorithm, which is represented by `trader_class`,
        a specialized implementation of `Trader`. This added `trader_class`'s
        name (see `Trader.get_algorithm_name`) becomes an available option for
        the `add_trader` factory method.

        Triggers `SIMMODEL_TRADER_ALGORITHM_ADDED` if successful.
        """
        name = trader_class.get_algorithm_name()
        if name in self._trader_algorithms:
            return

        self._trader_algorithms[name] = trader_class
        self.emit('SIMMODEL_TRADER_ALGORITHM_ADDED',
            model=self,
            algorithm=name)

    def _get_trader_class_by_algorithm_name(self,
        algorithm_name: str
    ) -> typing.Type['Trader']:
        """Return the registered `Trader` class with `algorithm_name`.

        If no registered `Trader` uses `algorithm_name`, raises
        `UnrecognizedAlgorithmError`.
        """
        try:
            return self._trader_algorithms[algorithm_name]
        except KeyError as e:
            raise UnrecognizedAlgorithmError(algorithm_name) from e

    def get_trader_algorithm_settings_defaults(self,
        algorithm: str
    ) -> typing.Dict[str, typing.Any]:
        """Return a `dict` of default settings to use for new traders using the
        named `algorithm`. Its organization corresponds to the algorithm-
        specific result of `get_trader_algorithm_settings_ui_definition`.

        If the specified `algorithm` is not recognized, this function raises
        `UnrecognizedAlgorithmError`.
        """
        trader_class = self._get_trader_class_by_algorithm_name(algorithm)
        return trader_class.get_algorithm_settings_defaults()

    def get_trader_algorithm_settings_ui_definition(self,
        algorithm: str
    ) -> typing.Dict[str, typing.Any]:
        """Return a `dict` defining how the Kivy GUI toolkit can render the
        named `algorithm`'s configuration controls. The organization of this
        dictionary is defined by Kivy, and used exclusively by the
        `window_view` module.

        If the specified `algorithm` name is not recognized, this function
        raises `UnrecognizedAlgorithmError`.
        """
        trader_class = self._get_trader_class_by_algorithm_name(algorithm)
        return trader_class.get_algorithm_settings_ui_definition()


    def get_traders(self
    ) -> typing.List['Trader']:
        """Return a `list` of the simulation's participating `Trader`s, which
        each expose their configuration and `TraderAccount` interfaces.

        This result changes following `SIMMODEL_TRADER_ADDED` and
        `SIMMODEL_TRADER_REMOVED` events.
        """
        return list(self._traders.values())

    def get_trader(self,
        name: str
    ) -> typing.Optional['Trader']:
        """Return the `Trader` known by `name`, or `None` if not found."""
        return self._traders.get(name)

    def add_trader(self,
        name: str,
        initial_funds: float,
        trading_fee: float,
        algorithm: str,
        algorithm_settings: typing.Dict[str, typing.Any]
    ) -> 'Trader':
        """Add and return a uniquely named `Trader` to the simulation that will
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

        The new trader's named `algorithm` determines how it reacts to stock
        market changes and makes trading decisions. The specified algorithm
        must have already been registered with this `SimModel`; A list of
        registered names is available from `get_trader_algorithms`.
        Unrecognized algorithms raise `UnrecognizedAlgorithmError`.

        The contents of `algorithm_settings` are validated according to
        `algorithm`, and invalid arguments raise subclasses of `TypeError` and
        `ValueError`.

        Triggers `SIMMODEL_TRADER_ADDED` if successful.
        """
        if name in self._traders:
            raise TraderNameTakenError(name)

        trader_class = self._get_trader_class_by_algorithm_name(algorithm)
        trader = trader_class(
            self._stock_market,
            name, initial_funds, trading_fee, algorithm_settings)

        self._traders[name] = trader
        self.emit('SIMMODEL_TRADER_ADDED',
            model=self,
            trader=trader)
        return trader

    def remove_trader(self,
        name: str
    ) -> None:
        """Remove a `Trader` from this `SimModel` by `name`.

        No error occurs if `name` does not exist.

        Triggers `SIMMODEL_TRADER_REMOVED` if successful.
        """
        try:
            trader = self._traders[name]
        except KeyError:
            return

        del self._traders[name]
        self.emit('SIMMODEL_TRADER_REMOVED',
            model=self,
            trader=trader)




# Imported last to avoid circular dependencies
from model.stock_market import StockMarket
from model.trader import Trader
