"""Defines `TradersTab` and supporting classes."""


__copyright__ = 'Copyright © 2019, Erik Anderson, James Abernathy, and Tyler Gerritsen'
__license__ = 'MIT'


import typing

from kivy.app import App
from kivy.properties import (
    NumericProperty, ObjectProperty, StringProperty)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.textinput import TextInput
from kivy.uix.filechooser import FileChooser
from kivy.uix.filechooser import FileChooserLayout

# Local package imports duplicated at end of file to resolve circular dependencies
if typing.TYPE_CHECKING:
    from model.sim_model import SimModel
    from model.trader import Trader




class FilePopup(Popup):
    """Popup dialog for adding symbols."""

    # References to component widgets
    stock_exchange: TextInput
    symbol_name: str

    def on_open(self,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        """Prepare the popup when opened."""

    '''
    def validate_name(self
    ) -> None:
        controller = App.get_running_app().get_controller()

        input = self.input_name
        if self.trader is not None:  # Name in use by this trader
            input.valid = True  # Changing name isn't allowed anyway
            return

        input.valid, invalid_reason = controller.validate_trader_name(
            input.text)


    def validate_algorithm(self
    ) -> None:
        controller = App.get_running_app().get_controller()

        input = self.input_algorithm
        input.valid, invalid_reason = controller.validate_trader_algorithm(
            input.text)


    def validate_initial_funds(self
    ) -> None:
        controller = App.get_running_app().get_controller()

        input = self.input_initial_funds
        input.valid, invalid_reason = controller.validate_trader_initial_funds(
            input.text)


    def validate_trading_fee(self
    ) -> None:
        controller = App.get_running_app().get_controller()

        input = self.input_trading_fee
        input.valid, invalid_reason = controller.validate_trader_trading_fee(
            input.text)


    def _save(self
    ) -> None:
        """Apply presumably valid trader info before closing the popup."""
        controller = App.get_running_app().get_controller()

        if self.trader is None:  # Create new trader
            controller.add_trader(
                name=self.input_name.text,
                initial_funds=self.input_initial_funds.text,
                trading_fee=self.input_trading_fee.text,
                algorithm=self.input_algorithm.text)

        else:  # Edit existing trader
            trader_name = self.trader.get_name()
            controller.set_trader_initial_funds(
                trader_name, self.input_initial_funds.text)
            controller.set_trader_trading_fee(
                trader_name, self.input_trading_fee.text)

        self.dismiss()
        '''




class SymbolRow(FloatLayout):
    """Selectable table body row representing a trader."""


    tab: 'StockSymbolsTab' = ObjectProperty()
    """Reference to parent tab for tracking the selected row."""

    symbol_name: str = StringProperty()
    symbol_exchange: str = StringProperty()

    def __init__(self,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        super().__init__(*args, **kwargs)

        datasource = App.get_running_app().get_controller().get_datasource()
        assert self.symbol_name is not None, \
            'Attempt to create table row for non-existent symbol.'


class StockSymbolsTab(TabbedPanelItem):
    """Class associated with the `<TradersTab>` template defined within
    `traders_tab.kv`.
    """

    # References to component widgets
    table_rows: BoxLayout

    selected_symbol_row: typing.Optional[SymbolRow] = ObjectProperty(
        None, allownone=True)
    """The selected symbol's table row, or `None` when unselected."""

    trader_names_to_rows: typing.Dict[str, SymbolRow]
    """Mapping of trader names to their corresponding table rows."""


    def __init__(self,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        super().__init__(*args, **kwargs)

        self.trader_names_to_rows = {}

        model = App.get_running_app().get_controller().get_model()

        model.bind(
            SIMMODEL_TRADER_ADDED=self.on_simmodel_trader_added,
            SIMMODEL_TRADER_REMOVED=self.on_simmodel_trader_removed)

        # Add preexisting traders
        for trader in model.get_traders():
            self.on_simmodel_trader_added(
                model=model,
                trader=trader)


    def on_add_clicked(self
    ) -> None:
        """Show a popup to add a new trader."""
        FilePopup().open()

    def on_simmodel_trader_added(self,
        model: 'SimModel',
        trader: 'Trader'
    ) -> None:
        """Add a table row for the newly added `trader`."""
        symbol_row = SymbolRow(tab=self,
            trader_name=trader.get_name(),
            trading_algorithm=trader.get_algorithm_name(),
            initial_funds=trader.get_initial_funds(),
            trading_fee=trader.get_trading_fee())

        self.table_rows.add_widget(symbol_row)
        self.trader_names_to_rows[trader.get_name()] = symbol_row

    def on_remove_clicked(self
    ) -> None:
        """Remove `selected_trader_row`."""
        assert self.selected_trader_row is not None, \
            'Remove button clicked without a trader row selected.'

        controller = App.get_running_app().get_controller()
        controller.remove_trader(
            self.selected_trader_row.trader_name)

    def on_simmodel_trader_removed(self,
        model: 'SimModel',
        trader: 'Trader'
    ) -> None:
        """Remove the table row for deleted `trader`."""
        trader_row = self.trader_names_to_rows[trader.get_name()]

        self.table_rows.remove_widget(trader_row)
        del self.trader_names_to_rows[trader.get_name()]

        if self.selected_trader_row == trader_row:
            self.selected_trader_row = None




# Imported last to avoid circular dependencies
from model.sim_model import SimModel
from model.trader import Trader
