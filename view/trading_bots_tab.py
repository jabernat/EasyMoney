"""Defines `TradingBotsTab` and supporting classes."""


__copyright__ = 'Copyright © 2019, Erik Anderson, James Abernathy, and Tyler Gerritsen'
__license__ = 'MIT'


import typing

from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.button import Button

# Local package imports duplicated at end of file to resolve circular dependencies
if typing.TYPE_CHECKING:
    #from controller.sim_controller import SimController
    pass




class TradingBotsTab(TabbedPanelItem):
    """Class associated with the `<TradingBotsTab>` template defined within
    `trading_bots_tab.kv`.
    """


    button_add: Button
    button_edit: Button
    button_remove: Button

    selected_trader: typing.Optional[str] = StringProperty(allownone=True)


    @staticmethod
    def on_selected_trader(
        instance: 'TradingBotsTab',
        selected_trader: typing.Optional[str]
    ) -> None:
        """Disable edit and remove buttons when no trader is selected."""
        buttons_disabled = selected_trader is None

        instance.button_edit.disabled = buttons_disabled
        instance.button_remove.disabled = buttons_disabled


    def on_button_add_clicked(self,
    ) -> None:
        """Show a popup to add a new trader."""
        print('Add')


    def on_button_edit_clicked(self,
    ) -> None:
        """Show a popup to edit `selected_trader`."""
        print('Edit', self.selected_trader)


    def on_button_remove_clicked(self,
    ) -> None:
        """Remove `selected_trader`."""
        print('Remove', self.selected_trader)




# Imported last to avoid circular dependencies
#from controller.sim_controller import SimController
