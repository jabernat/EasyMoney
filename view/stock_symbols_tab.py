"""Defines `StockSymbolsTab` and supporting classes."""


__copyright__ = 'Copyright © 2019, Erik Anderson, James Abernathy, and Tyler Gerritsen'
__license__ = 'MIT'


import typing

from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.lang import Builder

# Local package imports duplicated at end of file to resolve circular dependencies
if typing.TYPE_CHECKING:
    #from controller.sim_controller import SimController
    pass




class StockSymbolsTab(TabbedPanelItem):
    """Class associated with the `<StockSymbolsTab>` template defined within
    `stock_symbols_tab.kv`.
    """

    def __init__(self):
        super.__init__()
        Builder.load_file('view/stock_symbols_tab.kv')

    def on_add_button_press(self
        ) -> None:
        """
        Method for a press of the add button on the GUI. Checks if there are
        any symbols left to add to the simulation. If not, informs the user
        of that fact. If there is an available symbol to add, opens a dialog
        to choose which symbol.
        :return:
        """
        pass

    def on_remove_button_press(self
        ) -> None:
        """
        Method for a press of the remove button on the GUI. Checks if there are
        any symbols left to remove from the simulation. If not, informs the user
        of that fact. If there is an available symbol to remove, it must be
        highlighted by the user. If no symbol is highlighted, the user
        will be informed of that fact and prompted to select a symbol to remove.
        """
        pass

    def on_symbol_label_select(self,
        stock_symbol: str
        ) -> None:
        """
        When a user clicks on a stock symbol on the list, the symbol should highlight
        and appropriate data keeping track of that action should be set. The goal is,
        if the remove button is pressed, it should remove the selected symbol.
        """
        pass







# Imported last to avoid circular dependencies
#from controller.sim_controller import SimController
