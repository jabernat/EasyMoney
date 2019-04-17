"""Defines `SimController` and supporting classes."""


__copyright__ = 'Copyright © 2019, Erik Anderson, James Abernathy, and Tyler Gerritsen'
__license__ = 'MIT'


import typing

# Local package imports duplicated at end of file to resolve circular dependencies
if typing.TYPE_CHECKING:
    from model.sim_model import SimModel
    from model.trader import Trader
    from controller.market_datasource import MarketDatasource
    from controller.market_updater import MarketUpdater




class TraderNotFoundError(ValueError):
    """An exception raised when attempting to access a `Trader` by name, but no
    such trader was found in the simulation.
    """

    name: str
    """The requested trader name that could not be found."""

    def __init__(self,
        name: str
    ) -> None:
        self.name = name
        super().__init__(
            'Trader name {!r} was not found in the simulation.'.format(name))




class SimController(object):
    """This module unifies various controls of the simulation `SimModel`. It
    exposes functions to manipulate simulation `Trader` participants, the
    stock market data used within the simulation, and the simulated flow of
    time.
    """


    _model: 'SimModel'
    """The stock market simulation model that this controller manipulates."""

    _datasource: 'MarketDatasource'
    """The datasource responsible for inputting stock market data over time for
    insertion into the market simulation.
    """

    _updater: 'MarketUpdater'
    """The updater responsible for controlling the simulation's flow of time,
    periodically feeding price data into the model.
    """


    def __init__(self,
        model: 'SimModel'
    ) -> None:
        """Initialize without a datasource, an updater, and an existing
        `SimModel` to control.
        """
        self._model = model
        self._datasource = MarketDatasource()
        self._updater = MarketUpdater(self._datasource, model)


    def get_model(self
    ) -> 'SimModel':
        """Return this `SimController's` current `SimModel`. Data within this
        model should not be modified, only read; To manipulate the model,
        instead use this `SimController`'s implemented methods.
        """
        return self._model

    def get_datasource(self
    ) -> 'MarketDatasource':
        """Return this `SimController`'s current `MarketDatasource`, providing
        access to its data input controlls.
        """
        return self._datasource

    def get_updater(self
    ) -> 'MarketUpdater':
        """Return this `SimController`'s current `MarketUpdater`, providing
        control over the simulation rate.
        """
        return self._updater


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
        `model.TraderNameTakenError` is raised.

        When this new trader creates a `TraderAccount`, its balance will start
        at `initial_funds`, measured in the same currency used by the
        `StockMarket`. If `initial_funds` is not positive,
        `model.trader.InitialFundsError` is raised.

        The new trader must pay `trading_fee` to buy or sell through its
        created `TraderAccount`s. If `trading_fee` is negative,
        `model.trader.TradingFeeError` is raised.

        The new trader's named `algorithm` determines how it reacts to stock
        market changes and makes trading decisions. The specified algorithm
        must have been registered with the `SimModel`; A list of registered
        names is available from `.get_model().get_trader_algorithms()`.
        Unrecognized algorithms raise `model.UnrecognizedAlgorithmError`.

        The contents of `algorithm_settings` are validated according to
        `algorithm`, and invalid arguments raise subclasses of `TypeError` and
        `ValueError`.
        """
        return self._model.add_trader(
            name, initial_funds, trading_fee,
            algorithm, algorithm_settings)

    def remove_trader(self,
        name: str
    ) -> None:
        """Remove a `Trader` instance from this `SimModel` by name. If `name`
        does not exist within the simulation, no error occurs.
        """
        self._model.remove_trader(name)

    def freeze_trader(self,
        name: str,
        reason: typing.Optional[str]
    ) -> None:
        """Prevent a `Trader` with `name` from either buying or selling stocks.
        The only way that the trader may resume activity is when this
        `SimController`'s `MarketUpdater` gets `.reset()`.
        """
        trader = self._model.get_trader(name)
        if trader is None:
            raise TraderNotFoundError(name)

        trader.freeze(reason)

    def set_trader_initial_funds(self,
        trader_name: str,
        initial_funds: float
    ) -> None:
        """Configure the trader with `trader_name` to initialize all future
        `TraderAccounts` with an initial balance of `initial_funds`.

        The `initial_funds` value is measured in the same units of currency as
        `StockMarket` prices within the `SimModel`. It must be positive, or
        else this method raises `model.trader.InitialFundsError`.
        """
        trader = self._model.get_trader(trader_name)
        if trader is None:
            raise TraderNotFoundError(trader_name)

        trader.set_initial_funds(initial_funds)

    def set_trader_trading_fee(self,
        trader_name: str,
        trading_fee: float
    ) -> None:
        """Change the cost that this trader must pay in order to buy or sell
        stocks through its created `TraderAccount`s. The new `trading_fee` must
        be non-negative, otherwise this method raises
        `model.trader.TradingFeeError`.
        """
        trader = self._model.get_trader(trader_name)
        if trader is None:
            raise TraderNotFoundError(trader_name)

        trader.set_trading_fee(trading_fee)

    def set_trader_algorithm_settings(self,
        trader_name: str,
        algorithm_settings: typing.Dict[str, typing.Any]
    ) -> None:
        """Replace the algorithm-specific settings of a trader identified by
        `trader_name` with `algorithm_settings`. These new settings get
        validated by the `Trader`'s sub-class, and raised exceptions extend
        `TypeError` and `ValueError`.
        """
        trader = self._model.get_trader(trader_name)
        if trader is None:
            raise TraderNotFoundError(trader_name)

        trader.set_algorithm_settings(algorithm_settings)


    def validate_trader_algorithm(self,
        algorithm_name: str
    ) -> typing.Tuple[bool, typing.Optional[str]]:
        """Validate an `algorithm_name` and return a `tuple` containing a flag
        indicating valid arguments along with a string explaining the reason if
        not. The passed `algorithm_name` must be one of the strings returned by
        `.get_model().get_trader_algorithms()`. If it is in the list,
        the method returns `(True, None)`. Otherwise, the method returns
        `(False, reason_string)`.
        """
        if algorithm_name not in self._model.get_trader_algorithms():
            return False, 'Algorithm not present.'

        return True, None

    def validate_trader_name(self,
        trader_name: str
    ) -> typing.Tuple[bool, typing.Optional[str]]:
        """Validate the string `trader_name`, and returns a `tuple` containing
        a flag indicating valid arguments along with a string explaining the
        reason if not. If `trader_name` is blank or matches an existing
        trader's name, the method returns `(False, reason_string)`. Otherwise
        the string is valid and the method returns `(True, None)`.
        """
        if not trader_name:
            return False, 'Trader name cannot be blank.'

        elif self._model.get_trader(trader_name) is not None:
            return False, 'Trader name already in use.'

        return True, None

    def validate_trader_initial_funds(self,
        initial_funds: float
    ) -> typing.Tuple[bool, typing.Optional[str]]:
        """Validate the given `initial_funds` value and return a `tuple`
        containing a flag indicating valid arguments along with a string
        explaining the reason if not. If the number is positive quantity, the
        method returns `(True, None)`. Otherwise the method returns
        `(False, reason_string)`.
        """
        if initial_funds <= 0:
            return False, 'Initial funds must be a positive number.'

        return True, None

    def validate_trader_trading_fee(self,
        trading_fee: float
    ) -> typing.Tuple[bool, typing.Optional[str]]:
        """Validate the given `trading_fee`, and return a `tuple` containing a
        flag indicating valid arguments along with a string explaining the
        reason if not. If `trading_fee` is negative, the
        method returns `(False, reason_string)`. Otherwise the method returns
        `(True, None)`.
        """
        if trading_fee < 0:
            return False, 'Trading fee cannot be negative.'

        return True, None




# Imported last to avoid circular dependencies
from model.sim_model import SimModel
from model.trader import Trader
from controller.market_datasource import MarketDatasource
from controller.market_updater import MarketUpdater
