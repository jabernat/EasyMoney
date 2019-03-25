from stock_market import StockMarket
from trader_account import TraderAccount

#TODO:
    #Events:
        #TRADER_ACCOUNT_CREATED
        #TRADER_ALGORITHM_SETTINGS_CHANGED
        #TRADER_INITIAL_FUNDS_CHANGED
        #TRADER_TRADING_FEE_CHANGED

class InitialFundsError (ValueError):
    """
    An exception raised when attempting to set a Trader ’s initial funds to zero
    or a negative value.
    """
    pass
    
class TradingFeeError (ValueError):
    """
    An exception raised when attempting to set a Trader ’s trading fee to a
    negative value.
    """
    pass

class Trader:
    def _init__ (self,
                name : str,
                initial_funds : float, trading_fee : float,
                algorithm_settings : typing.Dict[str, typing.Any]
                ) -> None:
        """
        The trader’s constructor, which initializes it with the given settings
        and no initial account.

        When this new trader creates a TraderAccount , its balance will start at
        initial_funds, measured in the same currency used by the StockMarket.
        Must be positive; Invalid quantities raise Trader.InitialFundsError
        exceptions.

        The new trader must pay trading_fee to .buy(…) or .sell(…) through
        created TraderAccount s. This fee must be non-negative; Invalid
        quantities raise Trader.TradingFeeError exceptions.

        The contents of algorithm_settings are validated according to the
        instantiated Trader sub-class, and invalid arguments raise subclasses of
        TypeError and ValueError.
        """
        pass
        
    def create_account (self,
                        market : StockMarket
                        ) -> TraderAccount:
        """
        This trader discards any current TraderAccount , and creates a new one
        tied to market. The new account starts with this trader’s configured
        initial funds (see .get_initial_funds() ). Returns the newly created
        account.
        """
        pass
        
    def get_account (self) -> typing.Optional[TraderAccount]:
        """
        Returns this trader’s active account, created using .create_account(…),
        or None if not created yet.

        This result changes upon .TRADER_ACCOUNT_CREATED events.
        """
        pass
        
    @classmethod
    def get_algorithm_name () -> str:
        """
        Class method that returns the name identifying this Trader sub-class’
        trading algorithm.
        """
        pass
    
    def get_algorithm_settings (self) -> typing.Dict[str, typing.Any]:
        """
        Returns this trader’s dictionary of algorithm-specific settings, used to
        adjust trading decisions. The structure of these settings can be
        gathered from .get_algorithm_settings_ui_definition().
        
        This result changes upon .TRADER_ALGORITHM_SETTINGS_CHANGED events.
        """
        pass
        
    @classmethod
    def get_algorithm_settings_defaults () -> typing.Dict[str, typing.Any]:
        """
        Class method that returns a default settings dictionary appropriate for
        this Trader sub-class.
        """
        pass
        
    @classmethod
    def get_algorithm_settings_ui_definition (
                                            ) -> typing.Dict[str, typing.Any]:
        """
        Class method that returns a dictionary which defines how the Kivy GUI
        toolkit can render this Trader sub-class’ configuration controls. Its
        contents mirror the expected structure of settings dictionaries within
        instances. The organization of this dictionary is defined by Kivy, and
        used exclusively by the Window View module.
        """
        pass
        
    def get_name (self) -> str:
        """
        Returns the name of this trader, unique within its containing SimModel.
        """
        pass
        
    def get_initial_funds (self) -> float:
        """
        Returns the initial balance of this trader’s TraderAccount s will start
        with. This balance will be positive, and in the same currency as the
        associated StockMarket.

        This result changes upon .TRADER_INITIAL_FUNDS_CHANGED events.
        """
        pass
        
    def get_trading_fee (self) -> float:
        """
        Returns the fee that this trader must pay when .buy(…) ing or
        .sell(…) ing through created TraderAccounts. This fee is always
        non-negative, but can be zero.

        This result changes upon .TRADER_TRADING_FEE_CHANGED events.
        """
        pass

    def set_algorithm_settings (self,
                            algorithm_settings : typing.Dict[str, typing.Any]
                            ) -> None:
        """
        Replaces this trader’s algorithm-specific settings dictionary with
        algorithm_settings .

        These new settings are validated by the Trader ’s sub-class, and raised
        exceptions extend TypeError and ValueError.
        """
        pass
        
    def set_initial_funds (self,
                            initial_funds : float
                            ) -> None:
        """
        Configures this trader to initialize all future TraderAccount s with an
        initial balance equal to initial_funds.
        
        The initial_funds value is measured in the same units of currency as
        StockMarket prices within this SimModel . It must be a positive
        quantity, or else this method raises A Trader.InitialFundsError
        exception.
        """
        pass
        
    def set_trading_fee (self,
                        trading_fee : float
                        ) -> None:
        """
        Changes the cost that this trader must pay in order to .buy(…) or
        .sell(…) through created TraderAccounts.
        
        The new trading_fee must be non-negative, otherwise this method throws a
        Trader.TradingFeeError exception.
        """
        pass
