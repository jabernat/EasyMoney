"""Defines `SimulationTab` and supporting classes."""


__copyright__ = 'Copyright © 2019, Erik Anderson, James Abernathy, and Tyler Gerritsen'
__license__ = 'MIT'


import datetime
import typing

from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import (StringProperty, ObjectProperty)
from kivy.clock import Clock

# Local package imports duplicated at end of file to resolve circular dependencies
if typing.TYPE_CHECKING:
    from controller.market_updater import MarketUpdater
    from model.stock_market import StockMarket




class SimulationTab(TabbedPanelItem):
    """Class associated with the `<SimulationTab>` template defined within
    `simulation_tab.kv`.
    """

    updater_state: str = StringProperty("reset")
    simulation_time: str = StringProperty("[Simulation Time]")

    def __init__(self,
        *args: typing.Any,
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)

        controller = self._get_controller()
        controller.get_updater().bind(
            MARKETUPDATER_PLAYING=self.on_marketupdater_playing,
            MARKETUPDATER_PAUSED=self.on_marketupdater_paused,
            MARKETUPDATER_RESET=self.on_marketupdater_reset)
        controller.get_model().get_stock_market().bind(
            STOCKMARKET_ADDITION=self.on_stockmarket_addition,
            STOCKMARKET_CLEARED=self.on_stockmarket_cleared)


    def _get_controller(self):
        return App.get_running_app().get_controller()

    def on_marketupdater_playing(self, updater: 'MarketUpdater'):
        self.updater_state = 'playing'


    def on_marketupdater_paused(self, updater: 'MarketUpdater'):
        self.updater_state = 'paused'


    def on_marketupdater_reset(self, updater: 'MarketUpdater'):
        self.updater_state = 'reset'

    def play_simulation(self):
        self._get_controller().get_updater().play()

    def pause_simulation(self):
        self._get_controller().get_updater().pause()

    def reset_simulation(self):
        self._get_controller().get_updater().reset()


    def on_stockmarket_addition(self,
        market: 'StockMarket',
        time: datetime.datetime,
        stock_symbol_prices: typing.Dict[str, float]
    ) -> None:
        self.label_time.text = '{:%Y-%m-%d %H:%M}'.format(time)

    def on_stockmarket_cleared(self,
        market: 'StockMarket'
    ) -> None:
        self.label_time.text = ''


    def run_console_test(self
    ) -> None:
        # Only allow running once
        if hasattr(self, '_ran_console_test'):
            return  # You'll crash because traders were already added
        self._ran_console_test = True


        print('Welcome to EasyMoney')
        controller = App.get_running_app().get_controller()
        model = controller.get_model()


        print('Adding traders')
        ALGORITHM = 'Momentum'
        INITIAL_FUNDS = 10_000.0
        algorithm_settings = model.get_trader_algorithm_settings_defaults(ALGORITHM)
        for name, trading_fee in [
            ('Madoff',  0.00),
            ('Belfort', 0.50),
            ('Stewart', 5.00)
        ]:
            controller.add_trader(name,
                initial_funds=INITIAL_FUNDS, trading_fee=trading_fee,
                algorithm=ALGORITHM, algorithm_settings=algorithm_settings)


        print('Adding datasources')
        import os
        root_dir = os.path.dirname(os.path.abspath(__file__))
        for filename in [
            os.path.join(root_dir, '..', 'data/NYSE-AAPL.json'),
            os.path.join(root_dir, '..', 'data/NYSE-MSFT.json'),
            os.path.join(root_dir, '..', 'data/NYSE-AMD.json'),
            os.path.join(root_dir, '..', 'data/NYSE-JCOM.json')
        ]:
            controller.get_datasource().add_stock_symbol(filename)
        controller.get_datasource().confirm()


        def on_marketupdater_paused(
            updater: 'MarketUpdater'
        ) -> None:
            """Print statistics after updater switches to PAUSED state."""
            print('Statistics')
            for trader in model.get_traders():
                print('Trader {!r}: {}'.format(
                    trader.get_name(),
                    trader.get_account().get_statistics_overall()))
        controller.get_updater().bind(
            MARKETUPDATER_PAUSED=on_marketupdater_paused)

        print('Starting simulation')
        controller.get_updater().play()




# Imported last to avoid circular dependencies
from controller.market_updater import MarketUpdater
from model.stock_market import StockMarket
