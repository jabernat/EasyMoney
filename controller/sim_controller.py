"""Defines `SimController` and supporting classes."""


__copyright__ = 'Copyright © 2019, Erik Anderson, James Abernathy, and Tyler Gerritsen'
__license__ = 'MIT'


import typing

# Local package imports at end of file to resolve circular dependencies




class SimController(object):
    """This module unifies various controls of the simulation. It
    passes `Trader` modifications to the Simulation Model, as needed
    by the Window View model. The module also facilitates any changes to
    the datasource—live or offline—as directed from the Window View
    model, and returns broadcasted messages of these changes. The
    module may also receive access calls to play, pause, and reset
    the simulation when applicable, likewise broadcasting when these
    state changes have occurred. The Simulation Controller also feeds
    data to the Simulation Model as needed, from the chosen datasource.
    """

    def __init__(self,
        model: 'SimModel'
    ) -> None:
        """Initialize without starting data sources, a paused
        updater, and an existing `SimModel` to control.
        """
        pass


    def add_trader(self,
        name: str,
        initial_funds: float,
        trading_fee: float,
        algorithm: str,
        algorithm_settings: typing.Dict[str, typing.Any]
    ) -> 'Trader':
        """Add a `Trader` instance to the simulation with a uniquely
        identifiable name that will make trading decisions based on
        the specified `algorithm` name, and returns it. This new
        `Trader` and its settings will remain in the simulation until
        removed using `.remove_trader( name )`.

        The new `Trader`'s name must be unique within this
        `SimModel`. Specifying names shared with existing traders raises
        `SimModel.TraderNameTakenError` exceptions.

        When this new `Trader` creates a `TraderAccount`, its balance
        will start at `initial_funds`, measured in the same currency
        used by the `StockMarket`. Must be positive; Invalid
        quantities raise `Trader.InitialFundsError` exceptions.

        The new `Trader` must pay `trading_fee` to `.buy(…)` or
        `.sell(…)` through created `TraderAccounts`. This fee must be
        non-negative; Invalid quantities raise
        `Trader.TradingFeeError` exceptions.

        The new `Trader's` named `algorithm` determines how it reacts to
        stock market changes and makes trading decisions. The specified
        algorithm must have already been registered with this
        `SimModel`; A list of registered names is available from
        `.get_trader_algorithms()`. Invalid algorithms raise
        `SimModel.UnrecognizedAlgorithmError` exceptions.

        The contents of `algorithm_settings` are validated according
        to algorithm, and invalid arguments raise subclasses of
        `TypeError` and `ValueError`.
        """
        pass


    def freeze_trader(self,
        name: str,
        reason: typing.Optional[str]
    ) -> None:
        """Prevent a `Trader` with name from either buying or
        selling stocks. The only way the trader may resume activity is
        when this `SimController`'s `MarketUpdater` gets `.reset()`.
        """
        pass


    def get_datasource(self) -> 'MarketDatasource':
        """Return this `SimController`'s current `MarketDatasource`,
        providing access to its provided interface methods.
        """
        pass


    def get_model(self) -> 'SimModel':
        """Return this `SimController's` current `SimModel`. Data within
        this model should not be modified, only read; To manipulate the
        model, instead use this `SimController`'s implemented methods.
        """
        pass


    def get_updater(self) -> 'MarketUpdater':
        """Return this `SimController`'s current `MarketUpdater`,
        providing access to its provided interface methods.
        """
        pass


    def remove_trader(self,
        name: str
    ) -> None:
        """Remove a `Trader` instance from this `SimModel` by name. If
        `name` does not exist within the simulation, no error occurs.
        """
        pass


    def set_trader_algorithm_settings(self,
        trader_name: str,
        algorithm_settings: typing.Dict[str, typing.Any]
    ) -> None:
        """Replace the algorithm-specific settings dictionary of a
        trader identified by `trader_name` with `algorithm_settings`.
        These new settings are validated by the `Trader`'s sub-class,
        and raised exceptions extend `TypeError` and `ValueError`.
        """
        pass


    def set_trader_initial_funds(self,
        trader_name: str,
        initial_funds: float
    ) -> None:
        """Configure the trader with `trader_name` to initialize all
        future `TraderAccounts` with an initial balance equal to
        `initial_funds`.

        The `initial_funds` value is measured in the same units of
        currency as `StockMarket` prices within this SimModel. It must
        be a positive quantity, or else this method raises a
        `Trader.InitialFundsError` exception.
        """
        pass


    def set_trader_trading_fee(self,
        trader_name: str,
        trading_fee: float
    ) -> None:
        """Change the cost that this trader must pay in order to
        `.buy(…)` or `.sell(…)` through created `TraderAccounts`. The
        new `trading_fee must` be non-negative, otherwise this method
        throws a `Trader.TradingFeeError` exception.
        """
        pass


    def validate_trader_algorithm(self,
        algorithm_name: str
    ) -> typing.Tuple[bool, str]:
        """Validate algorithm names and return a `tuple` containing a
        flag indicating valid arguments, and a string explaining the
        reason if not. The passed `algorithm_name` must be one of the
        strings in the list returned by
        `SimModel.get_trader_algorithms()`. If it is in the list,
        the method returns `True` and `None`. If the `algorithm_name` is
        not in the list, the method returns `False` and a string
        holding the reason.
        """
        pass


    def validate_trader_initial_funds(self,
        initial_funds: float
    ) -> typing.Tuple[bool, str]:
        """Validate the passed `initial_funds` value, and return a
        `tuple` containing a flag indicating valid arguments, and a
        string explaining the reason if not. If the number is a
        positive quantity, the method returns `True` and `None`.
        Otherwise the method returns `False` and a string that provides
        a reason for failure.
        """
        pass


    def validate_trader_name(self,
        trader_name: str
    ) -> typing.Tuple[bool, str]:
        """Validate the string `trader_name`, and returns a `tuple`
        containing a flag indicating valid arguments, and a string
        explaining the reason if not. If the string is blank or matches
        an existing trader's name, the method returns `False` and a
        string holding the reason for failure. Otherwise the string
        is valid and the method returns `True` and `None`.
        """
        pass


    def validate_trader_trading_fee(self,
        trading_fee: float
    ) -> typing.Tuple[bool, str]:
        """Validate the `numeric trading_fee`, and return a `tuple`
        containing a flag indicating valid arguments, and a string
        explaining the reason if not. If `trading_fee` is negative, the
        method returns `False` and a string holding the reason for
        failure. Otherwise the method returns `True` and `None`.
        """
        pass




# Imported last to avoid circular dependencies
from model.sim_model import SimModel
from model.trader import Trader
from controller.market_datasource import MarketDatasource
from controller.market_updater import MarketUpdater
