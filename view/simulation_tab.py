"""Defines `SimulationTab` and supporting classes."""


__copyright__ = 'Copyright © 2019, Erik Anderson, James Abernathy, and Tyler Gerritsen'
__license__ = 'MIT'


import traceback
import typing

from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.lang import Builder
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image

import dispatch

# Local package imports duplicated at end of file to resolve circular dependencies
if typing.TYPE_CHECKING:
    from controller.market_updater import MarketUpdater
    from model.trader import Trader
    from model.trader_account import TraderAccount




class ImageButton(ButtonBehavior, Image):
    pass




class SimulationTab(TabbedPanelItem):
    """Class associated with the `<SimulationTab>` template defined within
    `simulation_tab.kv`.
    """


    @classmethod
    def load_templates(cls
    ) -> None:
        """Loads Kivy UI template files (`*.kv`) for this tab."""
        Builder.load_file('view/simulation_tab.kv')


    def run_console_test(self,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        # Only allow running once
        if hasattr(self, '_ran_console_test'):
            return  # You'll crash because traders were already added
        self._ran_console_test = True

        import pprint
        pprinter = pprint.PrettyPrinter(indent=4)

        def create_event_printer(
            event_name: str
        ) -> typing.Callable[..., None]:
            def event_printer(*args, **kwargs):
                kwargs.update(enumerate(args))
                arguments = pprinter.pformat(kwargs)
                print('{} = \\\n{}'.format(event_name, arguments))
                if 'exception' in kwargs and kwargs['exception'] is not None:
                    traceback.print_tb(kwargs['exception'].__traceback__)
            return event_printer

        def print_all_events(
            dispatcher: dispatch.Dispatcher
        ) -> None:
            dispatcher.bind(**{event_name: create_event_printer(event_name)
                for event_name in dispatcher.EVENTS})

        def on_trader_account_created(
            trader: 'Trader',
            account: 'TraderAccount'
        )-> None:
            print_all_events(account)

        def on_marketupdater_paused(
            updater: 'MarketUpdater'
        ) -> None:
            """Print statistics after updater switches to PAUSED state."""
            print('Statistics')
            for trader in model.get_traders():
                print('Trader {!r}:'.format(trader.get_name()))
                pprinter.pprint(trader.get_account().get_statistics_overall())

        print('Welcome to EasyMoney')
        controller = App.get_running_app().get_controller()
        print_all_events(controller.get_datasource())
        print_all_events(controller.get_updater())
        controller.get_updater().bind(
            MARKETUPDATER_PAUSED=on_marketupdater_paused)

        model = controller.get_model()
        print_all_events(model)
        print_all_events(model.get_stock_market())

        print('Adding traders')
        ALGORITHM = 'Momentum'
        INITIAL_FUNDS = 10_000.0
        algorithm_settings = model.get_trader_algorithm_settings_defaults(ALGORITHM)
        for name, trading_fee in [
            ('Madoff',  0.00),
            ('Belfort', 0.50),
            ('Stewart', 5.00)
        ]:
            trader = controller.add_trader(name,
                initial_funds=INITIAL_FUNDS, trading_fee=trading_fee,
                algorithm=ALGORITHM, algorithm_settings=algorithm_settings)
            print_all_events(trader)
            trader.bind(
                TRADER_ACCOUNT_CREATED=on_trader_account_created)

        print('Adding datasources')
        for filename in [
            'data/AAPL.json',
            'data/MSFT.json',
            'data/AMD.json',
            'data/JCOM.json'
        ]:
            controller.get_datasource().add_stock_symbol(filename)
        controller.get_datasource().confirm()

        print('Starting simulation')
        controller.get_updater().play()




# Imported last to avoid circular dependencies
from controller.market_updater import MarketUpdater
from model.trader import Trader
from model.trader_account import TraderAccount
