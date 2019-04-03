from model.stock_market import StockMarket
from controller.market_datasource import MarketDatasource
from kivy.clock import Clock

#TODO: 
    #Events:
        #MARKET_UPDATER_PAUSED
        #MARKET_UPDATER_PLAYING
        #MARKET_UPDATER_RESET

class MarketUpdater(object):
    '''
    The following data members are used to manage the module state
    '''
    state : str
    source : MarketDatasource
    event : Clock.ClockEvent

    """
    The Market Updater periodically gets data from the Datasource component and
    channels it to the StockMarket component in the SimModel module. It also
    receives state calls from the Window View module to start and pause the data
    flow to the Simulation Model. This component also passes calls to reset the
    simulation to the Simulation Model from the Window View module. Whether the
    MarketUpdater has been started, paused, or reset, each has a respective
    event that is broadcast to the Window View module.
    """

    def __init__ (self, datasource: MarketDatasource) -> None:
        """
        The constructor for MarketUpdater . All new MarketUpdater s start in a
        paused state.
        """
        self.source = datasource
        self.state = "paused"

    
    def is_playing (self) -> bool:
        """
        This method returns true when MarketUpdater is in a play state.
        """
        if self.state is "playing":
            return True
        else:
            return False
    
    def pause(self) -> None:
        """
        This method sets this MarketUpdater to a pause state. While paused,
        new data samples will no longer be sent to the SimModel from the
        data source.
        """
        self.event.cancel()
        self.state = "paused"
        # TODO MARKET_UPDATER_PAUSED
    
    def play(self) -> None:
        """
        This method sets this MarketUpdater to a play state. While playing, new
        data samples may be periodically sent to the SimModel from the
        datasource.
        """
        self.event = Clock.schedule_interval(self.get_prices(), 12)
        self.state = "playing"
        # TODO MARKET_UPDATER_PLAYING

    
    def reset(self) -> None:
        """
        This method calls resets the market and trader accounts, unconfirms the
        datasource, and pauses this MarketUpdater.
        """
        self.state = "reset"

        #TODO MARKET_UPDATER_RESET

    def get_prices(self) -> None:
        '''
        Gets the current prices from the datasource, if an update is confirmed,
        and calls appropriate simulation module functions to update those prices.
        '''
        if self.source.can_confirm():
            self.source.get_next_prices()