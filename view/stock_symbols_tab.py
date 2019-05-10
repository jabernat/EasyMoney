"""Defines `StockSymbolsTab` and supporting classes."""


__copyright__ = 'Copyright © 2019, Erik Anderson, James Abernathy, and Tyler Gerritsen'
__license__ = 'MIT'


import typing

from kivy.app import App
from kivy.properties import (
    NumericProperty, ObjectProperty, StringProperty, ListProperty)
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


class FilePopup(Popup):
    """Popup dialog for adding symbols."""

    def _open(self,
        file: str
    ) -> None:
        """Apply presumably valid symbol info before closing the popup."""
        datasource = App.get_running_app().get_controller().get_datasource()
        datasource.add_stock_symbol(file);
        self.dismiss()


class SymbolRow(FloatLayout):
    """Selectable table body row representing a symbol."""

    tab: 'StockSymbolsTab' = ObjectProperty()
    """Reference to parent tab for tracking the selected row."""

    symbol_name: str = StringProperty()

    def __init__(self,
        symbol: str
    ) -> None:
        super().__init__()

        self.symbol_name = symbol
        assert self.symbol_name is not None, \
            'Attempt to create table row for non-existent symbol.'


class StockSymbolsTab(TabbedPanelItem):
    """Class associated with the `<symbolsTab>` template defined within
    `symbols_tab.kv`.
    """

    # References to component widgets
    table_rows: BoxLayout

    selected_symbol_row: typing.Optional[SymbolRow] = ObjectProperty(
        None, allownone=True)
    """The selected symbol's table row, or `None` when unselected."""

    symbol_names_to_rows: typing.Dict[str, SymbolRow]
    """Mapping of symbol names to their corresponding table rows."""


    def __init__(self,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        super().__init__(*args, **kwargs)

        self.symbol_names_to_rows = {}

        datasource = App.get_running_app().get_controller().get_datasource()

        datasource.bind(
            MARKETDATASOURCE_STOCK_SYMBOL_ADDED=self.on_datasource_symbol_added,
            MARKETDATASOURCE_STOCK_SYMBOL_REMOVED=self.on_datasource_symbol_removed)

    def on_add_clicked(self
    ) -> None:
        """Show a popup to add a new symbol."""
        FilePopup().open()

    def on_datasource_symbol_added(self,
        datasource: 'MarketDatasource',
        stock_symbol: str
    ) -> None:

        """Add a table row for the newly added symbol."""
        symbol_row = SymbolRow(stock_symbol)

        self.table_rows.add_widget(symbol_row)
        self.symbol_names_to_rows[stock_symbol] = symbol_row

    def on_remove_clicked(self
    ) -> None:
        """Remove `selected_symbol_row`."""
        assert self.selected_symbol_row is not None, \
            'Remove button clicked without a symbol row selected.'

        datasource = App.get_running_app().get_controller().get_datasource()
        datasource.remove_stock_symbol(
            self.selected_symbol_row.symbol_name)

    def on_datasource_symbol_removed(self,
        datasource: 'MarketDatasource',
        stock_symbol: str
    ) -> None:
        """Remove the table row for deleted `symbol`."""
        symbol_row = self.symbol_names_to_rows[symbol]

        self.table_rows.remove_widget(symbol)
        del self.symbol_names_to_rows[symbol]

        if self.selected_symbol_row == symbol_row:
            self.selected_symbol_row = None




# Imported last to avoid circular dependencies
from model.sim_model import SimModel
