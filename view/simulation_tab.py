"""Defines `SimulationTab` and supporting classes."""


__copyright__ = 'Copyright © 2019, Erik Anderson, James Abernathy, and Tyler Gerritsen'
__license__ = 'MIT'


import typing

from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanelItem

# Local package imports duplicated at end of file to resolve circular dependencies
if typing.TYPE_CHECKING:
    from controller.market_updater import MarketUpdater




class SimulationTab(TabbedPanelItem):
    """Class associated with the `<SimulationTab>` template defined within
    `simulation_tab.kv`.
    """


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
