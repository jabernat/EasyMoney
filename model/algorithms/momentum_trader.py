import typing
import datetime

from model.trader import Trader
from model.trader_account import TraderAccount




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
    intended to be at the front of the list.
    """


    _prices_last: typing.Optional[typing.Dict[str, float]]
    """Previously seen stock prices used to calculate price changes."""


    @classmethod
    def get_algorithm_name(cls
    ) -> str:
        """Return this `Trader` subclass' identifying algorithm name, unique
        to the `SimModel` that it is registered within.
        """
        return 'Momentum'


    def create_account(self
    ) -> TraderAccount:
        """Reinitializes the bot upon creation of a new `TraderAccount`."""
        account = super().create_account()

        # Reinitialize
        self._prices_last = None
        return account


    def trade(self
    ) -> None:
        """Choose to buy or sell based on updated stock market conditions.
        The algorithm here will be a simple strategy known as momentum.
        The bot simply assumes that current trends will continue for each
        symbol, and makes decisions accordingly
        """
        price_deltas = self._calculate_price_deltas()

        # buy as many shares of the highest priority stock as possible
        # given the current balance
        free_balance = self.get_account().get_balance() - self.get_trading_fee()
        if free_balance > 0:
            for stock_symbol in self._choose_symbols_to_buy(price_deltas):
                price = self.get_stock_market().get_stock_symbol_price(stock_symbol)
                quantity = price / free_balance

                self.get_account().buy(stock_symbol, quantity)
                break

        # sell everything that is depreciating
        owned_stocks = self.get_account().get_stocks()
        for stock_symbol in self._choose_symbols_to_sell(price_deltas):
            self.get_account().sell(stock_symbol, owned_stocks[stock_symbol])


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
        self._set_algorithm_settings(algorithm_settings)


    def _calculate_price_deltas(self
    ) -> typing.Dict[str, float]:
        """Calculates the difference between current stock prices and those
        seen during the last call.
        """
        prices_current = self.get_stock_market().get_prices()

        price_deltas = {}
        for stock_symbol, price_current in prices_current:
            if self._prices_last is None:  # First data point
                price_delta = 0.0
            else:
                price_delta = price_current - self._prices_last[stock_symbol]
            price_deltas[stock_symbol] = price_delta

        self._prices_last = prices_current
        return price_deltas

    def _choose_symbols_to_buy(self,
        price_deltas: typing.Dict[str, float]
    ) -> typing.List[str]:
        """Rank all symbols first to last based on which ones would be the best
        buying investment, and return a list of symbols for the result.
        """
        return [stock_symbol
            for stock_symbol, price_delta
                in sorted(price_deltas.items(), reverse=True,
                    key=lambda symbol, delta: delta)
                if price_delta > 0]

    def _choose_symbols_to_sell(self,
        price_deltas: typing.Dict[str, float]
    ) -> typing.List[str]:
        """Return a list of stock symbols that should be sold."""
        LOSS_THRESHOLD = -0.1  # Sell if delta goes below this

        return [stock_symbol
            for stock_symbol, price_delta in price_deltas
                if price_delta <= LOSS_THRESHOLD]
