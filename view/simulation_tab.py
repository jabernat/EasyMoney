"""Defines `SimulationTab` and supporting classes."""


__copyright__ = 'Copyright © 2019, Erik Anderson, James Abernathy, and Tyler Gerritsen'
__license__ = 'MIT'


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



# class SymbolRow(BoxLayout):
#     """Row that displays live symbol data"""
#
#     symbol_name: str = StringProperty()
#     symbol_price: str = StringProperty()
#
#     def __init__(self,
#         *args,
#         **kwargs: typing.Any
#     ) -> None:
#         super().__init__(*args, **kwargs)
#         controller = App.get_running_app().get_controller()
#         controller.bind(
#             MARKETDATASOURCE_STOCK_SYMBOL_ADDED=self.on_marketdatasource_stock_symbol_added,
#             STOCKMARKET_ADDITION=self.on_stockmarket_addition)
#
#     def refresh_symbol_row(self,
#     ) -> None:
#         pass
#
#     def on_marketdatasource_stock_symbol_added(self):
#         pass
#
#     def on_stockmarket_addition(self):
#         pass

# class TraderBox(FloatLayout):
#     """Box for an individual trader"""
#
#     trader_name: str = StringProperty()
#     bought_str: str = StringProperty()
#     sold_str: str = StringProperty()
#
#     trader_account: 'TraderAccount'
#     model: 'SimModel'
#
#     def __init__(self,
#         *args: typing.Any,
#         **kwargs: typing.Any
#     ) -> None:
#         super().__init__(*args, **kwargs)
#
#
#         self.model = App.get_running_app().get_controller().get_model()
#         trader = self.model.get_trader(self.trader_name)
#         trader.bind(TRADER_ACCOUNT_CREATED=self.on_trader_account_created)
#
#     def on_trader_account_created(self,
#         trader: 'Trader',
#         account: 'TraderAccount'
#     ) -> None:
#         self.trader_account = self.model.get_trader(
#             self.trader_name).get_account()
#
#         self.trader_account.bind(
#             TRADERACCOUNT_SOLD=self.on_traderaccount_sold,
#             TRADERACCOUNT_BOUGHT=self.on_traderaccount_bought)
#
#     def refresh_trader_display(self,
#     ) -> None:
#         pass
#
#     def on_traderaccount_sold(self,
#         account: 'TraderAccount',
#         stock_symbol: str,
#         shares: float,
#         profit: float
#     ) -> None:
#         self.sold_str = "Sold {} {}".format(stock_symbol, profit)
#         print(self.sold_str)
#
#     def on_traderaccount_bought(self,
#         account: 'TraderAccount',
#         stock_symbol: str,
#         shares: float,
#         cost: float
#     ) -> None:
#         self.bought_str = "Bought {} {}".format(stock_symbol, cost)


class SimulationTab(TabbedPanelItem):
    """Class associated with the `<SimulationTab>` template defined within
    `simulation_tab.kv`.
    """

    # References to component widgets
    # symbol_rows: BoxLayout
    # trader_boxes: BoxLayout

    # symbol_names_to_rows: typing.Dict[str, SymbolRow]
    # """Mapping of symbol names to their corresponding rows."""
    #
    # trader_names_to_boxes: typing.Dict[str, TraderBox]
    # """Mapping of trader names to their corresponding boxes."""

    updater_state: str = StringProperty("reset")
    simulation_time: str = StringProperty("[Simulation Time]")

    def __init__(self,
        *args: typing.Any,
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)

        # self.symbol_names_to_rows = {}
        # self.trader_names_to_boxes = {}
        # self.symbol_rows = BoxLayout()
        # self.trader_boxes = BoxLayout()

        controller = self._get_controller()

        market_updater = controller.get_updater()

        # model.bind(
        #     SIMMODEL_TRADER_ADDED=self.on_simmodel_trader_added,
        #     SIMMODEL_TRADER_REMOVED=self.on_simmodel_trader_removed)
        market_updater.bind(
            MARKETUPDATER_PLAYING=self.on_marketupdater_playing,
            MARKETUPDATER_PAUSED=self.on_marketupdater_paused,
            MARKETUPDATER_RESET=self.on_marketupdater_reset)

        # Clock.schedule_once(self.update_time, -1)
        # Clock.schedule_interval(self.update_time, 1)


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

    # def on_simmodel_trader_added(self,
    #     model: 'SimModel',
    #     trader: 'Trader'
    # ) -> None:
    #     """Add a trader box for the newly added 'trader'"""
    #     trader_box = TraderBox(trader_name=trader.get_name())
    #     self.trader_boxes.add_widget((trader_box))
    #     self.trader_names_to_boxes[trader.get_name()] = trader_box

    # def on_simmodel_trader_removed(self,
    #     model: 'SimModel',
    #     trader: 'Trader'
    # ) -> None:
    #     """Remove the trader box for deleted `trader`."""
    #     trader_box = self.trader_names_to_boxes[trader.get_name()]
    #
    #     self.trader_boxes.remove_widget(trader_box)
    #     del self.trader_names_to_boxes[trader.get_name()]


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
from controller.market_datasource import MarketDatasource
from model.trader_account import TraderAccount
