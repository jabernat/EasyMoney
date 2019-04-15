import typing
import datetime

from model.trader import Trader

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