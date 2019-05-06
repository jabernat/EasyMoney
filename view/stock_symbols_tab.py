"""Defines `StockSymbolsTab` and supporting classes."""


__copyright__ = 'Copyright © 2019, Erik Anderson, James Abernathy, and Tyler Gerritsen'
__license__ = 'MIT'


import typing


from kivy.properties import ObjectProperty
from kivy.properties import ListProperty
from kivy.app import Builder

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.button import Button

# Local package imports duplicated at end of file to resolve circular dependencies
if typing.TYPE_CHECKING:
    #from controller.sim_controller import SimController
    pass

class StockSymbolsTab(TabbedPanelItem):
    """Class associated with the `<StockSymbolsTab>` template defined within
    `stock_symbols_tab.kv`.
    """

    stock_symbol: str

    # References to component widgets
    button_add: Button
    button_remove: Button

    def on_add_button_click(self,
        controller: 'SimController'
    ) -> None:
        """
        Method for a press of the add button on the GUI. Checks if there are
        any symbols left to add to the simulation. If not, informs the user
        of that fact. If there is an available symbol to add, opens a dialog
        to choose which symbol.
        """
        filename = self.stock_symbol + ".json"
        controller.get_datasource().add_stock_symbol(filename)

    def on_remove_button_click(self,
        controller: 'SimController'
    ) -> None:
        """
        Method for a press of the remove button on the GUI. Checks if there are
        any symbols left to remove from the simulation. If not, informs the user
        of that fact. If there is an available symbol to remove, it must be
        highlighted by the user. If no symbol is highlighted, the user
        will be informed of that fact and prompted to select a symbol to remove.
        """
        controller.get_datasource().remove_stock_symbol(self.stock_symbol)

    def on_symbol_label_select(self,
        symbol: str
    ) -> None:
        """
        When a user clicks on a stock symbol on the list, the symbol should be highlighted
        and appropriate data keeping track of that action should be set. The goal is,
        if the remove button is pressed, it should remove the selected symbol.
        """
        self.stock_symbol = symbol





# Imported last to avoid circular dependencies
#from controller.sim_controller import SimController
