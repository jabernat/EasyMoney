
from kivy.clock import (
    Clock, ClockEvent)

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
    event that is broadcast to the Window View module.
    """

    market_updater_state: str
    """
    state attribute represents the current running status of the updater; paused,
    playing, or reset
    """
    parent_application_controller: 'SimController'
    """
    this controller attribute will be the simulation controller object that 
    contains this updater. Using this object will allow for simulation
    updates and information retrieval from the datasource
    """
    sheduled_simulation_update_event: ClockEvent
    """
    Kivy provides a ClockEvent ADT to work with. This datatype represents an 
    event that can be scheduled to occur at regular intervals. This application
    uses this data type to schedule a call to a function which retrieves
    symbol data from the market datasource module and updates the data in the
    simulation model accordingly.
    """

    def __init__(self,
                  controller: 'SimController'
                 ) -> None:
        """
        The constructor for MarketUpdater . All new MarketUpdater s start in a
        paused state.
        """
        self.parent_application_controller = controller
        self.market_updater_state = "paused"

    
    def is_playing (self
                    ) -> bool:
        """
        This method returns true when MarketUpdater is in a play state.
        """
        return self.market_updater_state == "playing"
    
    def pause(self
              ) -> None:
        """
        This method sets this MarketUpdater to a pause state. While paused,
        new data samples will no longer be sent to the SimModel from the
        data source.
        """
        self.sheduled_simulation_update_event.cancel()
        self.market_updater_state = "paused"
        # TODO MARKET_UPDATER_PAUSED
    
    def play(self
             ) -> None:
        """
        This method sets this MarketUpdater to a play state. While playing, new
        data samples may be periodically sent to the SimModel from the
        datasource.
        """
        self.sheduled_simulation_update_event = Clock.schedule_interval(
            self.update_model_prices_from_datasource, 12)
        self.market_updater_state = "playing"
        # TODO MARKET_UPDATER_PLAYING

    
    def reset(self
              ) -> None:
        """
        This method call resets the market and trader accounts, unconfirms the
        datasource, and pauses this MarketUpdater.
        """
        self.market_updater_state = "reset"

        #TODO MARKET_UPDATER_RESET

    def update_model_prices_from_datasource(self
                                            ) -> None:
        '''
        Gets the current prices from the datasource, if an update is confirmed,
        and calls appropriate simulation module functions to update those prices.
        '''
        if self.parent_application_controller.is_confirmed():
            prices = self.parent_application_controller.get_datasource().get_next_prices()
            self.parent_application_controller.get_model().get_stock_market().add_next_prices(prices[0], prices[1])




# Imported last to avoid circular dependencies
from controller.sim_controller import SimController
