"""Defines `Trader` and supporting classes."""


__copyright__ = 'Copyright © 2019, Erik Anderson, James Abernathy, and Tyler Gerritsen'
__license__ = 'MIT'


import abc
import inspect
import typing
import datetime

import dispatch

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




class TraderMeta(abc.ABCMeta):
    """Metaclass for `Trader` subclasses to automatically register all concrete
    implementations.
    """
    def __init__(trader_subclass,
        name: str,
        bases: typing.Sequence[typing.Type],
        namespace: typing.Mapping[str, typing.Any],
        **kwargs: typing.Any
    ) -> None:
        if not inspect.isabstract(trader_subclass):
            Trader.register_subclass(trader_subclass)  # type: ignore




class Trader(dispatch.Dispatcher, metaclass=TraderMeta):
    """The abstract base class of simulated traders within a `SimModel`. Each
    sub-class implements a unique trading strategy, and is identified by a
    unique algorithm name. Traders maintain settings that persist through
    market resets, which affect how they interact with simulated stock markets.

    Traders create and expose `TraderAccount`s that store their bank funds and
    purchased stocks for one simulation. As price samples are added to the
    simulation's `StockMarket`, traders react by buying and selling through
    their associated accounts.
    """


    _subclasses: typing.ClassVar[typing.Set[typing.Type['Trader']]] = set()
    """All registered concrete subclasses of the `Trader` abstract base class.
    """

    _stock_market: 'StockMarket'
    """The market that this trader reacts to."""

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

    EVENTS: typing.ClassVar[typing.FrozenSet[str]] = frozenset([
        'TRADER_ACCOUNT_CREATED',
        'TRADER_ALGORITHM_SETTINGS_CHANGED',
        'TRADER_INITIAL_FUNDS_CHANGED',
        'TRADER_TRADING_FEE_CHANGED'])
    """Events broadcast by `Trader`s."""


    @classmethod
    def register_subclass(cls,
        subclass: typing.Type['Trader']
    ) -> bool:
        """Add concrete `subclass` of `Trader` to the set of available
        implementations, returning `True` if successfully added.
        """
        if not issubclass(subclass, cls):
            raise ValueError('Subclass {!r} does not actually inherit from '
                '{!r} parent class.'.format(
                    subclass, cls))
        if inspect.isabstract(subclass) or subclass in cls._subclasses:
            return False

        cls._subclasses.add(subclass)
        return True

    @classmethod
    def iter_subclasses(cls
    ) -> typing.Iterator[typing.Type['Trader']]:
        """Return an iterator that yields all concrete `Trader` subclasses that
        were registered with `register_subclass`.
        """
        for subclass in cls._subclasses:
            yield subclass


    def __init__(self,
        market: 'StockMarket',
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
        self._stock_market = market

        self._name = name
        self._account = None

        self.set_initial_funds(initial_funds)
        self.set_trading_fee(trading_fee)
        self.set_algorithm_settings(algorithm_settings)

        market.bind(
            STOCKMARKET_CLEARED=self._on_stockmarket_cleared)

    def _on_stockmarket_cleared(self,
    ) -> None:
        """Responds to market resets by creating a new account."""
        self.create_account()


    def get_stock_market(self
    ) -> 'StockMarket':
        """Return the market that this trader participates in."""
        return self._stock_market

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

    def create_account(self
    ) -> 'TraderAccount':
        """Discard any previously created `TraderAccount`, and create a new one
        tied to `_stock_market`. The new account starts with this trader's
        configured initial funds (see `get_initial_funds`). Returns the newly
        created account.

        Triggers `TRADER_ACCOUNT_CREATED` if successful.
        """
        if self._account is not None:
            # Disconnect from old account
            self._account.unbind(
                self._on_traderaccount_frozen)

        self._account = TraderAccount(self._stock_market, self)
        self._account.bind(
            TRADERACCOUNT_FROZEN=self._on_traderaccount_frozen)
        self._stock_market.bind(
            STOCKMARKET_ADDITION=self._on_stockmarket_addition)

        self.emit('TRADER_ACCOUNT_CREATED',
            trader=self,
            account=self._account)

    def _on_traderaccount_frozen(self,
    ) -> None:
        """Stop reacting to the `StockMarket` once frozen."""
        self._stock_market.unbind(
            self._on_stockmarket_addition)

    def _on_stockmarket_addition(self,
    ) -> None:
        """Make trading decisions as `StockMarket` prices update."""
        try:
            self.trade()
        except Exception as e:
            assert self._account is not None, ('Received stock market update '
                'without an open trader account.')
            self._account.freeze(
                'Trader encountered an error when making a trading decision.',
                exception=e)


    @classmethod
    @abc.abstractmethod
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
            trader=self,
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
            trader=self,
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
            trader=self,
            algorithm_settings=algorithm_settings)

    @abc.abstractmethod
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
            'Trader subclass must implement set_algorithm_settings method.')
        # Subclasses validate settings and then assign and broadcast them:
        #self._set_algorithm_settings(algorithm_settings)

    @abc.abstractmethod
    def trade(self
    ) -> None:
        """Choose to buy or sell based on updated stock market conditions."""
        raise NotImplementedError(
            'Trader subclass must implement set_algorithm_settings method.')

class MomentumTrader(Trader):
    """Trader implementation for the abstract base class. The algorithm for
    this bot is known as a "momentum" strategy. It assumes that a given price
    trend will continue, and makes trades accordingly. So, prices going down
    will be assumed to go further down in the future, and vice versa for upward
    trends. Hence, this trader aims to buy the most rapidly increasing symbol
    under the assumption that it is likely to continue increasing for a little
    while, and then sell the symbol at the first sign of a price drop.

    Note: It is possible that this strategy will work in a no-commision
    environment, but it will almost certainly fail under the pressure of
    trading fees.

    To implement the strategy, this bot will sort all symbols into a list
    based on the most significant price increases. Bigger increases are
    intended to be at the front of the list."""
    def trade(self
    ) -> None:
        """Choose to buy or sell based on updated stock market conditions.
        The algorithm here will be a simple strategy known as momentum.
        The bot simply assumes that current trends will continue for each
        symbol, and makes decisions accordingly"""
        # prioritize the information
        prioritized_stocks_to_purchase = self.prioritize_symbols_to_buy()

        # buy as many shares of the highest priority stock as possible
        # given the current balance
        for quote in prioritized_stocks_to_purchase:
            if quote[1] < self.get_account().get_balance():
                quantity = quote[1] / self.get_account().get_balance()
                self.get_account().buy(quote[0], quantity)
                break

        # get a list of all stocks that are depreciating in value
        stocks_to_sell = self.choose_symbols_to_sell()

        # sell everything that is depreciating
        for quote in stocks_to_sell:
            self.get_account().sell(quote[0], quote[1])

    def get_algorithm_name(self
    ) -> str:
        """Return this `Trader` subclass' identifying algorithm name, unique
        to the `SimModel` that it is registered within.
        """
        return "Momentum"

    def set_algorithm_settings(self,
        algorithm_settings: typing.Dict[str, typing.Any]
    ) -> None:
        """Replace this trader's algorithm-specific settings `dict` with
        `algorithm_settings`.

        These new settings are validated by the `Trader`'s subclass, and raised
        exceptions extend `TypeError` and `ValueError`.

        Triggers `TRADER_ALGORITHM_SETTINGS_CHANGED` if successful.

        In the momentum bot, there are not any algorithm settings
        implemented yet. This algorithm may not require settings.
        Therefore, there isn't really anything to validate about the
        argument in this case.
        """
        self._algorithm_settings = algorithm_settings
        self.emit('TRADER_ALGORITHM_SETTINGS_CHANGED', trader=self, new_settings=algorithm_settings)
        # Subclasses validate settings and then assign and broadcast them:
        # self._set_algorithm_settings(algorithm_settings)

    def prioritize_symbols_to_buy(self
    ) -> typing.List[typing.Tuple[str, float]]:
        """Helper function for the trade abstract method. Rank all
        symbols first to last based on which ones would be the
        best buying investment, and return a list of symbol-price
        tuples for the result. For the implemented algorithm, The best
        investment is decided based on price differences between the
        last set of prices and the current known prices"""

        # get the previous and current price dictionaries, itemized into
        # a list of tuples
        immediate_prices = self.get_stock_market().get_prices().items()
        previous_prices = self.get_stock_market().get_prices(
            datetime.datetime.now()
            - datetime.timedelta(1)).items()

        # calculate the price changes between the two lists of quotes,
        # create a list of the differences in order to rank them by
        # price increase
        price_deltas: typing.List
        index = 0
        for quote in immediate_prices:
            price_deltas.append(typing.Tuple[quote[0],
                                             quote[1] -
                                             previous_prices[index][1] ]) # might not work yet. my python is weak :(
            index += 1

        # sort the list of stock quote tuples, smallest price difference to largest
        price_deltas.sort(key=lambda tup: tup[1])

        return price_deltas

    def choose_symbols_to_sell(self
    ) -> typing.List[typing.Tuple[str, float]]:
        """Helper function for the trade abstract method. make a list of symbols
        to sell. for the implemented algorithm, selling is decided based on
        price differences between the last price grouping and the current
        known prices. If any owned stocks experienced a significant enough
        price decrease, they are returned in a list of quote tuples to be
        sold off."""

        # declare a list of the owned stocks, and a list of owned stocks
        # to sell
        owned_stocks = self.get_account().get_stocks().items()
        stocks_to_sell: typing.List[typing.Tuple[str, float]]
        for quote in owned_stocks:
            if (quote[1] - self.get_stock_market().get_stock_symbol_price(quote[0])) > 1:
                stocks_to_sell.append(quote)
        return stocks_to_sell



# Imported last to avoid circular dependencies
from model.stock_market import StockMarket
from model.trader_account import TraderAccount
