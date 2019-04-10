"""Defines `Trader` and supporting classes."""


__copyright__ = 'Copyright © 2019, Erik Anderson, James Abernathy, and Tyler Gerritsen'
__license__ = 'MIT'


import typing

import pydispatch

# Local package imports at end of file to resolve circular dependencies




class InitialFundsError(ValueError):
    """An exception raised when attempting to set a `Trader`'s initial funds to
    zero or a negative value.
    """

    initial_funds: float
    """The invalid initial funds value that was requested."""

    def __init__(self,
        initial_funds: float
    ) -> None:
        self.initial_funds = initial_funds
        super().__init__(
            'Initial funds must be greater than zero.')


class TradingFeeError(ValueError):
    """An exception raised when attempting to set a `Trader`'s trading fee to a
    negative value.
    """

    trading_fee: float
    """The invalid trading negative fee that was requested."""

    def __init__(self,
        trading_fee: float
    ) -> None:
        self.trading_fee = trading_fee
        super().__init__(
            'Trading fee cannot be negative.')




class Trader(pydispatch.Dispatcher):
    """The abstract base class of simulated traders within a `SimModel`. Each
    sub-class implements a unique trading strategy, and is identified by a
    unique algorithm name. Traders maintain settings that persist through
    market resets, which affect how they interact with simulated stock markets.

    Traders create and expose `TraderAccount`s that store their bank funds and
    purchased stocks for one simulation. As price samples are added to the
    simulation's `StockMarket`, traders react by buying and selling through
    their associated accounts.
    """


    _name: str
    """The name that uniquely identifies this trader within its `SimModel`."""

    _initial_funds: float
    """The positive funds that this trader's `TraderAccounts` start with."""

    _trading_fee: float
    """The non-negative fee that this trader must pay to buy or sell stocks."""

    _algorithm_settings: typing.Dict[str, typing.Any]
    """This trader's subclass-specific configuration values."""

    _account: typing.Optional['TraderAccount']
    """This trader's active bank account and stock portfolio."""

    _events_: typing.ClassVar[typing.List[str]] = [
        'TRADER_ACCOUNT_CREATED',
        'TRADER_ALGORITHM_SETTINGS_CHANGED',
        'TRADER_INITIAL_FUNDS_CHANGED',
        'TRADER_TRADING_FEE_CHANGED']
    """Events broadcast by `Trader`s."""


    def __init__(self,
        name: str,
        initial_funds: float,
        trading_fee: float,
        algorithm_settings: typing.Dict[str, typing.Any]
    ) -> None:
        """Initializes a trader with the given settings and no initial account.

        When this new trader creates a `TraderAccount`, its balance will start
        at `initial_funds`, measured in the same currency used by the simulated
        `StockMarket`. Must be positive; Invalid quantities raise
        `InitialFundsError`.

        Each stock purchase or sale through a `TraderAccount` costs this trader
        `trading_fee`. This fee must be non-negative; Invalid quantities raise
        `TradingFeeError`.

        The contents of `algorithm_settings` are validated according to the
        instantiated subclass of `Trader`, and invalid arguments raise
        subclasses of `TypeError` and `ValueError`.
        """
        # TODO: Fail if instantiating an abstract Trader? Maybe in __new__?
        self._name = name
        self._account = None

        self.set_initial_funds(initial_funds)
        self.set_trading_fee(trading_fee)

        # Subclass initializes algorithm settings during construction
        #self.set_algorithm_settings(algorithm_settings)

        # TODO: Register for STOCK_MARKET_CLEARED to create a new account?


    def get_name(self
    ) -> str:
        """Return the name of this trader, unique within its containing
        `SimModel`.
        """
        return self._name


    def get_account(self
    ) -> typing.Optional['TraderAccount']:
        """Return this trader's active account, created using `create_account`,
        or `None` if not created yet.

        This result changes upon `TRADER_ACCOUNT_CREATED` events.
        """
        return self._account

    def create_account(self,
        market: 'StockMarket'
    ) -> 'TraderAccount':
        """Discard any previously created `TraderAccount`, and create a new one
        tied to `market`. The new account starts with this trader's configured
        initial funds (see `get_initial_funds`). Returns the newly created
        account.

        Triggers `TRADER_ACCOUNT_CREATED` if successful.
        """
        self._account = TraderAccount(market, self)
        # TODO: Register for TRADER_ACCOUNT_FROZEN to unregister from StockMarket updates?
        # TODO: Register for STOCK_MARKET_ADDITION to make buy and sell decisions? On error, freeze account.
        self.emit('TRADER_ACCOUNT_CREATED',
            instance=self,
            account=self._account)


    @classmethod
    def get_algorithm_name(cls
    ) -> str:
        """Return this `Trader` subclass' identifying algorithm name, unique
        to the `SimModel` that it is registered within.
        """
        raise NotImplementedError(
            'Trader subclass must implement get_algorithm_name.')

    @classmethod
    def get_algorithm_settings_defaults(cls
    ) -> typing.Dict[str, typing.Any]:
        """Return a default settings `dict` appropriate for this `Trader`
        subclass.
        """
        return {}

    @classmethod
    def get_algorithm_settings_ui_definition(cls
    ) -> typing.Dict[str, typing.Any]:
        """Return a `dict` which defines how the Kivy GUI toolkit can render
        this `Trader` subclass' configuration controls. Its contents mirror the
        expected structure of settings dictionaries. The organization of this
        dictionary is defined by Kivy, and used exclusively within
        `window_view`.
        """
        return {}


    def get_initial_funds(self
    ) -> float:
        """Return the initial balance that this trader's `TraderAccount`s will
        start with. This balance will be positive, and in the same currency as
        the associated `StockMarket`.

        This result changes upon `TRADER_INITIAL_FUNDS_CHANGED` events.
        """
        return self._initial_funds

    def set_initial_funds(self,
        initial_funds: float
    ) -> None:
        """Configure this trader to initialize all future `TraderAccount`s with
        an initial balance of `initial_funds`.
        
        The `initial_funds` value is measured in the same units of currency as
        `StockMarket` prices within this `SimModel`. It must be a positive
        quantity, or else `InitialFundsError` is raised.

        Triggers `TRADER_INITIAL_FUNDS_CHANGED` if successful.
        """
        if self._initial_funds == initial_funds:
            return  # No change

        elif initial_funds <= 0:
            raise InitialFundsError(initial_funds)

        self._initial_funds = initial_funds
        self.emit('TRADER_INITIAL_FUNDS_CHANGED',
            instance=self,
            initial_funds=initial_funds)


    def get_trading_fee(self
    ) -> float:
        """Return the fee that this trader must pay for each purchase or sale
        through created `TraderAccount`s. This fee is always non-negative, but
        can be zero.

        This result changes upon `TRADER_TRADING_FEE_CHANGED` events.
        """
        return self._trading_fee

    def set_trading_fee(self,
        trading_fee: float
    ) -> None:
        """Change the cost that this trader must pay in order to `buy` or
        `sell` through created `TraderAccounts`.
        
        The new `trading_fee` must be non-negative, otherwise this method
        raises `TradingFeeError`.

        Triggers `TRADER_TRADING_FEE_CHANGED` if successful.
        """
        if self._trading_fee == trading_fee:
            return  # No change

        elif trading_fee < 0:
            raise TradingFeeError(trading_fee)

        self._trading_fee = trading_fee
        self.emit('TRADER_TRADING_FEE_CHANGED',
            instance=self,
            trading_fee=trading_fee)


    def get_algorithm_settings(self
    ) -> typing.Dict[str, typing.Any]:
        """Return this trader's `dict` of algorithm-specific settings, used to
        adjust trading decisions. The structure of these settings can be
        gathered from `get_algorithm_settings_ui_definition`.
        
        This result changes upon `TRADER_ALGORITHM_SETTINGS_CHANGED` events.
        """
        return self._algorithm_settings

    def _set_algorithm_settings(self,
        algorithm_settings: typing.Dict[str, typing.Any]
    ) -> None:
        """Helper for `Trader` subclasses to assign and broadcast changed
        settings.
        """
        self._algorithm_settings = algorithm_settings
        self.emit('TRADER_ALGORITHM_SETTINGS_CHANGED',
            instance=self,
            algorithm_settings=algorithm_settings)

    def set_algorithm_settings(self,
        algorithm_settings: typing.Dict[str, typing.Any]
    ) -> None:
        """Replace this trader's algorithm-specific settings `dict` with
        `algorithm_settings`.

        These new settings are validated by the `Trader`'s subclass, and raised
        exceptions extend `TypeError` and `ValueError`.

        Triggers `TRADER_ALGORITHM_SETTINGS_CHANGED` if successful.
        """
        raise NotImplementedError(
            'Trader subclass must implement set_algorithm_settings.')
        # Subclasses validate settings and then assign and broadcast them:
        #self._set_algorithm_settings(algorithm_settings)




# Imported last to avoid circular dependencies
from model.stock_market import StockMarket
from model.trader_account import TraderAccount
