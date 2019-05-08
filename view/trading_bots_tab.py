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
    from model.sim_model import SimModel
    from model.trader import Trader




class TradingBotRow(FloatLayout):
    """Selectable table body row representing a trading bot."""
    tab: 'TradingBotsTab' = ObjectProperty()
    trader_name: str = StringProperty()
    trading_algorithm: str = StringProperty()
    initial_funds: float = BoundedNumericProperty(0.00, min=0.00)
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

    trader_names_to_rows: typing.Dict[str, TradingBotRow]
    """Mapping of trader names to their corresponding table rows."""


    def __init__(self,
        *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)

        self.trader_names_to_rows = {}

        controller = App.get_running_app().get_controller()
        model = controller.get_model()

        model.bind(
            SIMMODEL_TRADER_ADDED=self.on_simmodel_trader_added,
            SIMMODEL_TRADER_REMOVED=self.on_simmodel_trader_removed)

        # Add preexisting traders
        for trader in model.get_traders():
            self.on_simmodel_trader_added(
                model=model,
                trader=trader)


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
        controller = App.get_running_app().get_controller()
        for index in range(1, 21):
            controller.add_trader('John Madden {}'.format(index),
                initial_funds=999_999, trading_fee=0.01,
                algorithm='Momentum')

    def on_simmodel_trader_added(self,
        model: 'SimModel',
        trader: 'Trader'
    ) -> None:
        """Add a table row for the newly added `trader`."""
        trading_bot_row = TradingBotRow(tab=self,
            trader_name=trader.get_name(),
            trading_algorithm=trader.get_algorithm_name(),
            initial_funds=trader.get_initial_funds(),
            trading_fee=trader.get_trading_fee())

        self.table_rows.add_widget(trading_bot_row)
        self.trader_names_to_rows[trader.get_name()] = trading_bot_row


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
        controller = App.get_running_app().get_controller()
        controller.remove_trader(
            self.selected_trader.trader_name)

    def on_simmodel_trader_removed(self,
        model: 'SimModel',
        trader: 'Trader'
    ) -> None:
        """Remove the table row for deleted `trader`."""
        trading_bot_row = self.trader_names_to_rows[trader.get_name()]

        self.table_rows.remove_widget(trading_bot_row)
        del self.trader_names_to_rows[trader.get_name()]

        if self.selected_trader is trading_bot_row:
            self.selected_trader = None




# Imported last to avoid circular dependencies
from model.sim_model import SimModel
from model.trader import Trader
