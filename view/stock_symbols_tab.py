"""Defines `StockSymbolsTab` and supporting classes."""


__copyright__ = 'Copyright © 2019, Erik Anderson, James Abernathy, and Tyler Gerritsen'
__license__ = 'MIT'


import typing

from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanelItem

# Local package imports duplicated at end of file to resolve circular dependencies
if typing.TYPE_CHECKING:
    #from controller.sim_controller import SimController
    pass




class StockSymbolsTab(TabbedPanelItem):
    """Class associated with the `<StockSymbolsTab>` template defined within
    `stock_symbols_tab.kv`.
    """
    pass




# Imported last to avoid circular dependencies
#from controller.sim_controller import SimController
