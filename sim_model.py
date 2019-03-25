from stock_market import StockMarket
from trader import Trader

#TODO:
    #Events:
        #TRADER_ADDED
        #TRADER_ALGORITHM_ADDED
        #TRADER_REMOVED

class TraderNameTakenError (ValueError):
    """
    An exception raised when attempting to add a new trader to the simulation
    using a name that is already taken by an existing trader.
    """
    pass
class UnrecognizedAlgorithmError (ValueError):
    """
    An exception raised when a method expects the name of a known trading
    algorithm, but receives an unrecognized name argument.
    """
    pass

class SimModel:
    """
    EasyMoney instantiates a single SimModel instance, which represents the MVC
    architecture’s model: the state of a simulated stock market and the bank
    accounts and stock portfolios of participating traders. This high-level
    module organizes its sub-components with an observer design pattern, by
    sharing StockMarket data updates among listening Traders.
    """
    pass

    def _init__ (self) -> None:
        """
        The simulation model’s constructor, which initializes it with no stock
        market price data, no trader algorithms, and no traders.
        """
        pass

    def add_trader (self,
                    name : str,
                    initial_funds : float,
                    trading_fee : float,
                    algorithm : str,
                    algorithm_settings : typing.Dict[str, typing.Any]
                    ) -> Trader:
        """
        Adds a Trader instance to the simulation with a uniquely identifiable
        name that will make trading decisions based on the specified algorithm
        name, and returns it. This new trader and its settings will remain in
        the simulation until removed using .remove_trader( name ).

        The new trader’s name must be unique within this SimModel. Specifying
        name s shared with existing traders raises
        SimModel.TraderNameTakenError exceptions.

        When this new trader creates a TraderAccount , its balance will start at
        initial_funds, measured in the same currency used by the StockMarket.
        Must be positive; Invalid quantities raise Trader.InitialFundsError
        exceptions.

        The new trader must pay trading_fee to .buy(…) or .sell(…) through
        created TraderAccount s. This fee must be non-negative; Invalid
        quantities raise Trader.TradingFeeError exceptions.

        The new trader’s named algorithm determines how it reacts to stock
        market changes and makes trading decisions. The specified algorithm must
        have already been registered with this SimModel ; A list of registered
        names is available from .get_trader_algorithms() . Invalid algorithms
        raise SimModel.UnrecognizedAlgorithmError exceptions.

        The contents of algorithm_settings are validated according to algorithm,
        and invalid arguments raise subclasses of TypeError and ValueError.
        """
        pass
    
    def add_trader_algorithm (self,
                                trader_class : typing.Callable[..., Trader]
                                ) -> None:
        """
        Adds a new trader algorithm, which is represented by trader_class , a
        specialized implementation of Trader . This added trader_class ’s name
        (see Trader.get_algorithm_name() ) becomes an available option for the
        factory method add_trader.
        """
        pass
    
    def get_stock_market (self) -> StockMarket:
        """
        Returns the simulation’s StockMarket instance, which exposes its
        interface for reading, adding, and resetting stock market price data.
        """
        pass
    
    def get_trader_algorithm_settings_defaults (
                                            algorithm : str
                                            ) -> typing.Dict[str, typing.Any]:
        """
        Returns a dictionary containing default settings to use for new traders
        using the named algorithm . This dictionary’s organization corresponds
        to the algorithm-specific result of
        get_trader_algorithm_settings_ui_definition( algorithm ).
        
        If the specified algorithm is not recognized, this function throws a
        SimModel.UnrecognizedAlgorithmError exception.
        """
        pass
    def get_trader_algorithm_settings_ui_definition (
                                            algorithm : str
                                            ) -> typing.Dict[str, typing.Any]:
        """
        Returns a dictionary which defines how the Kivy GUI toolkit can render
        the named algorithm ’s configuration controls. The organization of this
        dictionary is defined by Kivy, and used exclusively by the Window View
        module.

        If the specified algorithm name is not recognized, this function throws
        a SimModel.UnrecognizedAlgorithmError exception.
        """
        pass
    
    def get_trader_algorithms (self) -> typing.List[str]:
        """
        Returns a list of known trader algorithm names which have been
        registered through add_trader_algorithm . These names are used by other
        methods in this component to specify an algorithm to access more info on
        or use for new traders. This result changes upon
        .TRADER_ALGORITHM_ADDED events.
        """
        pass
    
    def get_traders (self) -> typing.List[Trader]:
        """
        Returns a list of the simulation’s Trader instances, which each expose
        their interfaces to get and set configuration and to control behavior.
        Furthermore, TraderAccount s can be accessed through these traders,
        exposing trading behavior and statistics. This result changes upon
        .TRADER_ADDED and .TRADER_REMOVED events.
        """
        pass
    
    def remove_trader (self,
                        name : str
                        ) -> None:
        """
        Removes a Trader instance from this SimModel by name. If name does not
        exist within the simulation, no error occurs.
        """
        pass
    
    def reset_market_and_trader_accounts (self) -> None:
        """
        Clears this simulation model’s StockMarket of old price data, and
        prompts all Traders to discard their TraderAccount s and create new
        ones.
        """
        pass
