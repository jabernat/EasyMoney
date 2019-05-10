"""Defines `StockSymbolsTab` and supporting classes."""


__copyright__ = 'Copyright © 2019, Erik Anderson, James Abernathy, and Tyler Gerritsen'
__license__ = 'MIT'


import os
import typing

from kivy.app import App
from kivy.properties import (
    ObjectProperty, StringProperty)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanelItem

from view.window_view import ErrorPopup

# Local package imports duplicated at end of file to resolve circular dependencies
if typing.TYPE_CHECKING:
    from controller.market_datasource import MarketDatasource
    from model.sim_model import SimModel




class AddSymbolFilePopup(Popup):
    """Popup dialog for adding `*.json` symbol files from AlphaVantage."""

    def open_file(self,
        path: str,
        filepath: str
    ) -> None:
        """Apply symbol file and close the popup."""
        os.chdir(path)  # Remember chosen folder for next time

        datasource = App.get_running_app().get_controller().get_datasource()
        try:
            datasource.add_stock_symbol(filepath)
        except Exception as e:
            popup = ErrorPopup(
                description='Cannot open file:', exception=e)
            popup.open()
        else:
            self.dismiss()




class SymbolRow(FloatLayout):
    """Selectable table body row representing a symbol."""

    tab: 'StockSymbolsTab' = ObjectProperty()
    """Reference to parent tab for tracking the selected row."""

    stock_symbol: str = StringProperty()
    """Key used to identify this stock, which may include the exchange."""

    exchange_name: typing.Optional[str] = StringProperty(None, allownone=True)
    """Stock exchange name extracted from `stock_symbol`, or `None` if the
    data file didn't specify one.
    """

    symbol_name: str = StringProperty()
    """Just the stock symbol, extracted from `stock_symbol`."""




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
            MARKETDATASOURCE_STOCK_SYMBOL_ADDED= \
                self.on_datasource_symbol_added,
            MARKETDATASOURCE_STOCK_SYMBOL_REMOVED= \
                self.on_datasource_symbol_removed)


    def on_add_clicked(self
    ) -> None:
        """Show a popup to add a new symbol."""
        popup = AddSymbolFilePopup()
        popup.filechooser.path = os.getcwd()
        popup.open()

    def on_datasource_symbol_added(self,
        datasource: 'MarketDatasource',
        stock_symbol: str
    ) -> None:
        """Add a table row for the newly added symbol."""
        exchange_and_symbol: typing.List = stock_symbol.split(':')
        if len(exchange_and_symbol) < 2:
            exchange_and_symbol.insert(0, None)
        exchange_name, symbol_name = exchange_and_symbol[:2]

        symbol_row = SymbolRow(tab=self,
            exchange_name=exchange_name,
            symbol_name=symbol_name)
        self.table_rows.add_widget(symbol_row)
        self.symbol_names_to_rows[stock_symbol] = symbol_row


    def on_remove_clicked(self
    ) -> None:
        """Remove `selected_symbol_row`."""
        assert self.selected_symbol_row is not None, \
            'Remove button clicked without a symbol row selected.'

        datasource = App.get_running_app().get_controller().get_datasource()
        datasource.remove_stock_symbol(
            self.selected_symbol_row.stock_symbol)

    def on_datasource_symbol_removed(self,
        datasource: 'MarketDatasource',
        stock_symbol: str
    ) -> None:
        """Remove the table row for deleted `symbol`."""
        symbol_row = self.symbol_names_to_rows[stock_symbol]

        self.table_rows.remove_widget(symbol_row)
        del self.symbol_names_to_rows[stock_symbol]

        if self.selected_symbol_row == symbol_row:
            self.selected_symbol_row = None




# Imported last to avoid circular dependencies
from controller.market_datasource import MarketDatasource
from model.sim_model import SimModel
