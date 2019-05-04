"""Defines `TradingBotsTab` and supporting classes."""


__copyright__ = 'Copyright © 2019, Erik Anderson, James Abernathy, and Tyler Gerritsen'
__license__ = 'MIT'


import typing

from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanelItem

# Local package imports duplicated at end of file to resolve circular dependencies
if typing.TYPE_CHECKING:
    #from controller.sim_controller import SimController
    pass




class TradingBotsTab(TabbedPanelItem):
    """Class associated with the `<TradingBotsTab>` template defined within
    `trading_bots_tab.kv`.
    """
    pass




# Imported last to avoid circular dependencies
#from controller.sim_controller import SimController
