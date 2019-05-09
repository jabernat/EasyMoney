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



class SymbolRow(BoxLayout):
    """Row that displays live symbol data"""

    symbol_name: str = StringProperty()
    symbol_price: str = StringProperty()

    def __init__(self,
        *args,
        **kwargs: typing.Any
    ) -> None:
        super().__init__(*args, **kwargs)
        controller = App.get_running_app().get_controller()
        controller.bind(
            MARKETDATASOURCE_STOCK_SYMBOL_ADDED=self.on_marketdatasource_stock_symbol_added,
            STOCKMARKET_ADDITION=self.on_stockmarket_addition)

    def refresh_symbol_row(self,
    ) -> None:
        pass

    def on_marketdatasource_stock_symbol_added(self):
        pass

    def on_stockmarket_addition(self):
        pass

class TraderBox(BoxLayout):
    """Box for an individual trader"""

    trader_name: str = StringProperty()
    bought_str: str = StringProperty()
    sold_str: str = StringProperty()

    def __init__(self,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        super().__init__(*args, **kwargs)


        model = App.get_running_app().get_controller().get_model()
        trader = model.get_trader(self.trader_name)
        trader.bind(
            TRADERACCOUNT_SOLD=self.on_traderaccount_sold,
            TRADERACCOUNT_BOUGHT=self.on_traderaccount_bought)

    def refresh_trader_display(self,
    ) -> None:
        pass

    def on_traderaccount_sold(self
    ) -> None:
        pass

    def on_traderaccount_bought(self
    ) -> None:
        pass


class SimulationTab(TabbedPanelItem):
    """Class associated with the `<SimulationTab>` template defined within
    `simulation_tab.kv`.
    """

    symbol_names_to_rows: typing.Dict[str, SymbolRow]
    """Mapping of symbol names to their corresponding rows."""

    trader_names_to_box: typing.Dict[str, TraderBox]
    """Mapping of trader names to their corresponding boxes."""


    def __init__(self,
        **kwargs
    ) -> None:
        super(SimulationTab, self).__init__(**kwargs)

        controller = App.get_running_app().get_controller()
        model = controller.get_model()

        model.bind(
            SIMMODEL_TRADER_ADDED=self.on_simmodel_trader_added,
            SIMMODEL_TRADER_REMOVED=self.on_simmodel_trader_removed)


    def on_simmodel_trader_added(self
    ) -> None:
        self.refresh_trader_display()

    def on_simmodel_trader_removed(self
    ) -> None:
        self.refresh_trader_display()


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
        for filename in [
            'data/AAPL.json',
            'data/MSFT.json',
            'data/AMD.json',
            'data/JCOM.json'
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
