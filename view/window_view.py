"""Defines `WindowView` and supporting classes."""


__copyright__ = 'Copyright © 2019, Erik Anderson, James Abernathy, and Tyler Gerritsen'
__license__ = 'MIT'


import typing
from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.lang import Builder

# Local package imports duplicated at end of file to resolve circular dependencies
if typing.TYPE_CHECKING:
    from controller.sim_controller import SimController
    from model.algorithms.momentum_trader import MomentumTrader

Builder.load_string("""

<AppStart>:
    size_hint: 1, 1
    pos_hint: {'center_x': .5, 'center_y': .5}
    do_default_tab: False

    TabbedPanelItem:
        text: 'Trading Bots'
        BoxLayout: 
            orientation: 'vertical'
            BoxLayout: # Bot info panel
                orientation: 'vertical'                
                BoxLayout:
                    canvas.before: 
                        Color: 
                            rgb: 25/255.0, 135/255.0, 184/255.0
                        Rectangle:
                            pos: self.pos
                            size: self.size
                    Label:

                        text: 'Bot Name'
                    Label:
                        text: 'Trading Algorithm'
                    Label:
                        text: 'Starting Funds'
                    Label:
                        text: 'Trading Fee'
                BoxLayout:
                    Label:
                        text: 'MADOFF'
                    Label:
                        text: 'NBit Predictor'
                    Label:
                        text: '$10,000'
                    Label:
                        text: '$0'
                BoxLayout:
                    Label:
                        text: 'BELFORT'
                    Label:
                        text: 'NBit Predictor'
                    Label:
                        text: '$10,000'
                    Label:
                        text: '$0'
                BoxLayout:
                    Label:
                        text: 'STEWART'
                    Label:
                        text: 'Random Trading'
                    Label:
                        text: '$50,000'
                    Label:
                        text: '$5'
            BoxLayout:
            BoxLayout:  
            BoxLayout:
            BoxLayout:
            BoxLayout: # Button panel
                Button:
                    text: 'Add'
                Button:
                    text: 'Edit'
                Button:
                    text: 'Remove'
                Label:
                Label:

    TabbedPanelItem:
        text: 'Data Source'
        BoxLayout: 
            orientation: 'vertical'
            BoxLayout: # Stock symbol info panel
                orientation: 'vertical'                
                BoxLayout: # Row 1
                    canvas.before: 
                        Color: 
                            rgb: 25/255.0, 135/255.0, 184/255.0
                        Rectangle:
                            pos: self.pos
                            size: self.size
                    Label:

                        text: 'Stock Exchange'
                    Label:
                        text: 'Stock Symbol'
                    Label:
                    Label:
                BoxLayout: # Row 2
                    Label:
                        text: 'NYSE'
                    Label:
                        text: 'AAPL'
                    Label:
                    Label:
                BoxLayout: # Row 3
                    Label:
                        text: 'NYSE'
                    Label:
                        text: 'AMD'
                    Label:
                    Label:
                BoxLayout: # Row 4
                    Label:
                        text: 'NYSE'
                    Label:
                        text: 'CHSP'
                    Label:
                    Label:
                BoxLayout: # Row 5
                    Label:
                        text: 'NYSE'
                    Label:
                        text: 'MSFT'
                    Label:
                    Label:
            BoxLayout:
            BoxLayout:
            BoxLayout:
            BoxLayout:
            BoxLayout:
                Button:
                    text: 'Add'
                Button:
                    text: 'Remove'
                Label:
                Label:
                Label:

    TabbedPanelItem:
        text: 'Simulation'
        BoxLayout:
            orientation: 'vertical'
            BoxLayout: # Sim control panel
                BoxLayout:
                    Label:
                    Image:
                        source: 'pause.png'
                    Label:
                    Image:
                        source: 'reset.png'
                Label:
                Label:
                Label:
                Label:
                Label:

            Image:
                source: 'stock1.gif'
            Image:
                source: 'stock2.gif'
            Image:
                source: 'stock3.gif'
            BoxLayout:


    TabbedPanelItem:
        text: 'Statistics'
        BoxLayout:
            orientation: 'vertical'
            BoxLayout:
                Label:
                    text: 'Bot\\'s Daily Statistics'
                Label:
                    text: 'Bot\\'s Overall Statistics'

            BoxLayout:
                size_hint_y: 3
                Label:
                    text: "Lorem ipsum dolor sit amet, consectetur adipiscing elit"
                    color: 0,0,0,1 
                    canvas.before:
                        Color:
                            rgba: 1, 1, 1, 1
                        Rectangle:
                            pos: self.pos
                            size: self.size
                Label:
                    text: "Lorem ipsum dolor sit amet, consectetur adipiscing elit"
                    color: 0,0,0,1 
                    canvas.before:
                        Color:
                            rgba: 1, 1, 1, 1
                        Rectangle:
                            pos: self.pos
                            size: self.size
""")


class AppStart(TabbedPanel):
    pass


class PrototypeGUI(App):
    def build(self):
        return AppStart()

class WindowView(object):
    """
    """


    _sim_controller: 'SimController'
    """"""


    def __init__(self,
        sim_controller: 'SimController'
    ) -> None:
        """
        """
        self._sim_controller = sim_controller


    def get_controller(self
    ) -> 'SimController':
        """
        """
        return self._sim_controller


    def run(self
    ) -> None:
        """
        """
        PrototypeGUI().run()
        # self._print_console()

    def _print_console(self) -> None:
        print('Welcome to EasyMoney')

        # TRADER
        names = ['Madoff', 'Belfort', 'Stewart']
        initial_funds: float = 10000.0
        trading_fee: float = .05
        momentum_trader = MomentumTrader()
        algorithm: str = momentum_trader.get_algorithm_name()
        algorithm_settings: dict = momentum_trader.get_algorithm_settings_defaults()
        print('Adding traders')
        try:
            for name in names:
                self._sim_controller.add_trader(name,
                                                initial_funds,
                                                trading_fee,
                                                algorithm,
                                                algorithm_settings)
        except Exception as e:
            print(e)
        print('Traders Madoff, Belfort, Stewart successfully added.\n')

        # DATASOURCE
        file_names = ['AAPL.json', 'MSFT.json', 'AMD.json', 'JCOM.json']
        print('Adding datasources.')
        for filename in file_names:
            try:
                self._sim_controller.get_datasource().add_stock_symbol(
                    filename)
            except Exception as e:
                print(e)
        try:
            if self._sim_controller.get_datasource().can_confirm():
                self._sim_controller.get_datasource().confirm()
        except Exception as e:
            print(e)
        print('Datasources successfully added.\n')

        # SIMULATION
        print('Starting simulation.')
        try:
            self._sim_controller.get_updater().play()
        except Exception as e:
            print(e)
        print('Simulation complete.\n')

        # STATISTICS
        print('Statistics display:')
        trader_list = self._sim_controller.get_model().get_traders()
        for trader in trader_list:
            try:
                print('Trader: ' + trader.get_name())
                print(trader.get_account().get_statistics_overall())
                print()
            except Exception as e:
                print(e)

        print('\nThank you for using EasyMoney.')


# Imported last to avoid circular dependencies
from controller.sim_controller import SimController
from model.algorithms.momentum_trader import MomentumTrader

