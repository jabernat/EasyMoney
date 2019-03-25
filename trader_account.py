from stock_market import StockMarket
from trader import Trader

#TODO:
    #Events:
        #TRADER_ACCOUNT_BOUGHT
        #TRADER_ACCOUNT_FROZEN
        #TRADER_ACCOUNT_SOLD
        #TRADER_ACCOUNT_UPDATED

class FrozenError (ValueError):
    An exception raised when attempting to buy or sell with this account after
    it was frozen.
class InsufficientBalanceError (ValueError):
    An exception raised when attempting to buy more stock shares than this
    trader’s account can afford.
class InsufficientStockSharesError (ValueError):
    An exception raised when attempting to sell more stock shares than this
    trader’s account currently holds.
class StockShareQuantityError (ValueError):
    An exception raised when attempting to buy or sell an invalid non-positive
    quantity of stock shares

class TraderAccount:
    
    def _init__ (self,
                market : StockMarket,
                trader : Trader
                ) -> None:
        """
        The trader account’s constructor, which initializes it with the trader’s
        configured initial funds. All future buying and selling occurs on
        market.
        """
        pass
        
    def buy (self,
            stock_symbol : str,
            shares : float
            ) -> None:
        """
        Buys a quantity shares of stock_symbol using the StockMarket ’s current
        prices, and adds these purchased shares to this account. To perform this
        action, the account must not be frozen; Buying with a frozen account
        raises a TraderAccount.FrozenError exception.

        The given stock_symbol must exist within the StockMarket linked with
        this account. If it does not, this method raises a
        StockMarket.StockSymbolUnrecognizedError exception.

        The quantity to buy, shares , must be positive, yet less than or equal
        to this account’s current balance. If shares is zero or less, this
        raises a TraderAccount.StockShareQuantityError. If shares is positive
        but greater than .get_balance() , this method raises a
        TraderAccount.InsufficientBalanceError exception.
        """
        pass
        
    def freeze (self,
                reason : typing.Optional[str] = None,
                exception : typing.Optional[Exception] = None
                ) -> None:
        """
        Stops this account’s trader from buying or selling. An account cannot be
        unfrozen; its trader must instead create a new account.

        A brief reason sentence can be provided for the user, optionally with
        the offending exception.
        """
        pass
        
    def get_balance (self) -> float:
        """
        Returns this account’s current bank balance, in the same unit of
        currency as the associated StockMarket.
        """
        pass
        
    def get_statistics_daily (self) -> typing.Dict[str, typing.Any]:
        """
        Returns a dictionary of daily running statistics collected during a
        simulation. The keys of this dictionary identify particular trading
        statistics using display-language-independent English identifiers,
        like “ AVERAGE_PROFIT ”, and the dictionary values can be converted to
        text with str.
        """
        pass
    
    def get_statistics_overall (self) -> typing.Dict[str, typing.Any]:
        """
        Returns a dictionary of overall running statistics collected during a
        simulation. The keys of this dictionary identify particular trading
        statistics using display-language-independent English identifiers, like
        “AVERAGE_PROFIT”, and the dictionary values can be converted to text
        with str.
        """
        pass
    
    def get_stock_market (self) -> StockMarket:
        """
        Returns the StockMarket that this account was created for. All .buy(…)
        and .sell(…) prices are sampled from this stock market.
        """
        pass
    
    def get_stocks (self) -> typing.Dict[str, float]:
        """
        Returns the stock shares contained within this account, owned by the
        account’s trader. The resulting dictionary maps stock symbol keys to
        price quantity values.
        """
        pass
    
    def get_trader (self) -> Trader:
        """
        Returns the Trader instance that created this account and owns its
        contents.
        """
        pass
    
    def is_frozen (self) -> bool:
        """
        Returns True if this account has been frozen and can no longer trade.
        The simulation freezes the accounts of traders that encounter errors or
        violate simulation rules. The following violations will freeze an
        account: selling unowned stock shares, or buying unaffordable stock
        shares.

        Frozen accounts are effectively excluded from the simulation, and the
        trader must create a new account if they need to continue participating.
        """
        pass
    
    def sell (self,
                stock_symbol : str,
                shares : float
                ) -> None:
        """
        Sells a quantity shares of stock_symbol contained within this account at
        the StockMarket ’s current prices, exchanging those shares for a
        deposit to this account’s balance. To perform this action, the account
        must not be frozen; Selling from a frozen account raises a
        TraderAccount.FrozenError exception.
        
        The given stock_symbol must exist within the StockMarket linked with
        this account. If it does not, this method raises a
        StockMarket.StockSymbolUnrecognizedError exception.

        The quantity to sell, shares , must be positive, yet less than or equal
        to this account’s current quantity of stock_symbol . If shares is zero
        or less, this raises a TraderAccount.StockShareQuantityError. If shares
        is positive but greater than the quantity of stock_symbol owned, this
        method raises a TraderAccount.InsufficientStockSharesError exception.
        """
        pass
    
