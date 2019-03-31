# Local package imports at end of file to resolve circular dependencies

#TODO: 
    #Events:
        #MARKET_UPDATER_PAUSED
        #MARKET_UPDATER_PLAYING
        #MARKET_UPDATER_RESET

class MarketUpdater(object):
    """
    The Market Updater periodically gets data from the Datasource component and
    channels it to the StockMarket component in the SimModel module. It also
    receives state calls from the Window View module to start and pause the data
    flow to the Simulation Model. This component also passes calls to reset the
    simulation to the Simulation Model from the Window View module. Whether the
    MarketUpdater has been started, paused, or reset, each has a respective
    event that is broadcasted to the Window View module.
    """

    def __init__ (self,
                datasource: 'MarketDatasource'
                ) -> None:
        """
        The constructor for MarketUpdater . All new MarketUpdater s start in a
        paused state.
        """
        pass
    
    def is_playing (self) -> bool:

        """
        This method returns true when MarketUpdater is in a play state.
        """
        pass
    
    def pause (self) -> None:
        """
        This method sets this MarketUpdater to a pause state. While paused,
        new data samples will no longer be sent to the SimModel from the
        datasource.
        """
        pass
    
    def play (self) -> None:
        """
        This method sets this MarketUpdater to a play state. While playing, new
        data samples may be periodically sent to the SimModel from the
        datasource.
        """
        pass
    
    def reset (self) -> None:
        """
        This method calls resets the market and trader accounts, unconfirms the
        datasource, and pauses this MarketUpdater.
        """
        pass




# Imported last to avoid circular dependencies
from model.stock_market import StockMarket
from controller.market_datasource import MarketDatasource
