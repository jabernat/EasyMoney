"""Defines `TradingBotsTab` and supporting classes."""


__copyright__ = 'Copyright © 2019, Erik Anderson, James Abernathy, and Tyler Gerritsen'
__license__ = 'MIT'


import typing

from kivy.app import App
from kivy.properties import (
    BoundedNumericProperty, ObjectProperty, StringProperty)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.tabbedpanel import TabbedPanelItem

# Local package imports duplicated at end of file to resolve circular dependencies
if typing.TYPE_CHECKING:
    #from controller.sim_controller import SimController
    pass




class TradingBotRow(FloatLayout):
    """Selectable table body row representing a trading bot."""
    tab: 'TradingBotsTab' = ObjectProperty()
    trader_name: str = StringProperty()
    trading_algorithm: str = StringProperty()
    starting_funds: float = BoundedNumericProperty(0.00, min=0.00)
    trading_fee: float = BoundedNumericProperty(0.00, min=0.00)




class TradingBotsTab(TabbedPanelItem):
    """Class associated with the `<TradingBotsTab>` template defined within
    `trading_bots_tab.kv`.
    """


    # References to component widgets
    button_add: Button
    button_edit: Button
    button_remove: Button
    table_rows: BoxLayout

    selected_trader: typing.Optional[TradingBotRow] = ObjectProperty(
        None, allownone=True)
    """The selected trader's table row, or `None` when unselected."""


    @staticmethod
    def on_selected_trader(
        instance: 'TradingBotsTab',
        selected_trader: typing.Optional[TradingBotRow]
    ) -> None:
        """Disable edit and remove buttons when no trader is selected.

        Note: `selected_trader` is an `ObjectProperty`, which does not
        automatically trigger this handler when instantiated.
        """
        buttons_disabled = selected_trader is None

        instance.button_edit.disabled = buttons_disabled
        instance.button_remove.disabled = buttons_disabled


    def on_button_add_clicked(self
    ) -> None:
        """Show a popup to add a new trader."""
        self.table_rows.add_widget(TradingBotRow(
            tab=self,
            trader_name='2',
            trading_algorithm='ALG',
            starting_funds=10,
            trading_fee=1))


    def on_button_edit_clicked(self
    ) -> None:
        """Show a popup to edit `selected_trader`."""
        assert self.selected_trader is not None, \
            'Edit button clicked without a trader row selected.'
        self.selected_trader.trading_fee += 1


    def on_button_remove_clicked(self
    ) -> None:
        """Remove `selected_trader`."""
        assert self.selected_trader is not None, \
            'Remove button clicked without a trader row selected.'
        self.table_rows.remove_widget(self.selected_trader)
        self.selected_trader = None




# Imported last to avoid circular dependencies
#from controller.sim_controller import SimController
