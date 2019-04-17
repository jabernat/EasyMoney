"""Defines `WindowView` and supporting classes."""


__copyright__ = 'Copyright © 2019, Erik Anderson, James Abernathy, and Tyler Gerritsen'
__license__ = 'MIT'


import typing

from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.lang import Builder
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image

import dispatch

# Local package imports duplicated at end of file to resolve circular dependencies
if typing.TYPE_CHECKING:
    from controller.sim_controller import SimController
    from model.algorithms.momentum_trader import MomentumTrader
    from model.trader import Trader
    from model.trader_account import TraderAccount




class ImageButton(ButtonBehavior, Image):
    pass


class RootWidget(TabbedPanel):
    pass




class WindowView(App):
    """
    """


    _sim_controller: 'SimController'
    """"""


    def __init__(self,
        sim_controller: 'SimController'
    ) -> None:
        """
        """
        super().__init__()

        self._sim_controller = sim_controller

        Builder.load_file('view/window.kv')


    def get_controller(self
    ) -> 'SimController':
        """
        """
        return self._sim_controller


    def build(self
    ) -> RootWidget:
        """
        """
        return RootWidget()


    def run(self
    ) -> None:
        """
        """
        super().run()


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
            print('ALPHA')
            print(account)

        print('Welcome to EasyMoney')
        controller = self.get_controller()
        print_all_events(controller.get_datasource())
        print_all_events(controller.get_updater())

        model = controller.get_model()
        print_all_events(model)
        print_all_events(model.get_stock_market())

        print('Adding traders')
        ALGORITHM = 'Momentum'
        INITIAL_FUNDS = 10_000.0
        TRADING_FEE = 0.50
        algorithm_settings = model.get_trader_algorithm_settings_defaults(ALGORITHM)
        for name in ['Madoff', 'Belfort', 'Stewart']:
            trader = self._sim_controller.add_trader(name,
                initial_funds=INITIAL_FUNDS, trading_fee=TRADING_FEE,
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


        ''' TODO: Print statistics after updater switches to PAUSED state.
        print('Statistics')
        for trader in model.get_traders():
            print('Trader {!r}:'.format(trader.get_name()))
            pprinter.pprint(trader.get_account().get_statistics_overall())
        '''


# Imported last to avoid circular dependencies
from controller.sim_controller import SimController
from model.algorithms.momentum_trader import MomentumTrader
from model.trader import Trader
from model.trader_account import TraderAccount

