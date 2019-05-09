"""Defines `TradersTab` and supporting classes."""


__copyright__ = 'Copyright © 2019, Erik Anderson, James Abernathy, and Tyler Gerritsen'
__license__ = 'MIT'


import typing

from kivy.app import App
from kivy.properties import (
    NumericProperty, ObjectProperty, StringProperty)
from kivy.uix.bubble import Bubble
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.textinput import TextInput

# Local package imports duplicated at end of file to resolve circular dependencies
if typing.TYPE_CHECKING:
    from model.sim_model import SimModel
    from model.trader import Trader




class PopupInputTooltip(Bubble):
    """Tooltip to explain an invalid input."""

    input: typing.Union[TextInput, Spinner] = ObjectProperty()

    message: str = StringProperty()




class TraderPopup(Popup):
    """Popup dialog for adding and editing traders."""


    trader: typing.Optional['Trader'] = ObjectProperty(None, allownone=True)
    """The `Trader` to edit, or `None` to add a new trader."""

    # References to component widgets
    tooltip_container: FloatLayout
    input_name: TextInput
    input_algorithm: Spinner
    input_initial_funds: TextInput
    input_trading_fee: TextInput


    def on_open(self,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        """Prepare the popup when opened."""
        # Focus first control automatically
        first_control = (self.input_name if self.trader is None
            else self.input_initial_funds)
        first_control.focus = True

        # Force initial validation, which doesn't trigger when .trader is set
        self.validate_name()
        self.validate_algorithm()
        self.validate_initial_funds()
        self.validate_trading_fee()


    def validate_input(self,
        input: typing.Union[TextInput, Spinner],
        validate: typing.Callable[[str], typing.Tuple[bool, typing.Optional[str]]]
    ) -> None:
        """Check the contents of `input` with `validate`, and display an error
        message if invalid.
        """
        input.valid, invalid_reason = validate(
            input.text)

        if input.valid:
            if input.tooltip:  # Remove old error
                self.tooltip_container.remove_widget(input.tooltip)
                input.tooltip = False

        # Invalid
        elif input.tooltip:  # Update old error
            input.tooltip.message = invalid_reason
        else:  # Show new error
            input.tooltip = PopupInputTooltip(
                input=input, message=invalid_reason)
            self.tooltip_container.add_widget(input.tooltip)

    def validate_name(self
    ) -> None:
        controller = App.get_running_app().get_controller()

        input = self.input_name
        if self.trader is not None:  # Name in use by this trader
            input.valid = True  # Changing name isn't allowed anyway
            return

        self.validate_input(input, controller.validate_trader_name)

    def validate_algorithm(self
    ) -> None:
        controller = App.get_running_app().get_controller()

        self.validate_input(self.input_algorithm,
            controller.validate_trader_algorithm)

    def validate_initial_funds(self
    ) -> None:
        controller = App.get_running_app().get_controller()

        self.validate_input(self.input_initial_funds,
            controller.validate_trader_initial_funds)

    def validate_trading_fee(self
    ) -> None:
        controller = App.get_running_app().get_controller()

        self.validate_input(self.input_trading_fee,
            controller.validate_trader_trading_fee)


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




class TraderRow(FloatLayout):
    """Selectable table body row representing a trader."""


    tab: 'TradersTab' = ObjectProperty()
    """Reference to parent tab for tracking the selected row."""

    trader_name: str = StringProperty()
    trading_algorithm: str = StringProperty()
    initial_funds: float = NumericProperty()
    trading_fee: float = NumericProperty()


    def __init__(self,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        super().__init__(*args, **kwargs)

        model = App.get_running_app().get_controller().get_model()
        trader = model.get_trader(self.trader_name)
        assert trader is not None, \
            'Attempt to create table row for non-existent trader.'

        trader.bind(
            TRADER_INITIAL_FUNDS_CHANGED=self.on_trader_initial_funds_changed,
            TRADER_TRADING_FEE_CHANGED=self.on_trader_trading_fee_changed)


    def on_trader_initial_funds_changed(self,
        trader: 'Trader',
        initial_funds: float
    ) -> None:
        self.initial_funds = initial_funds

    def on_trader_trading_fee_changed(self,
        trader: 'Trader',
        trading_fee: float
    ) -> None:
        self.trading_fee = trading_fee




class TradersTab(TabbedPanelItem):
    """Class associated with the `<TradersTab>` template defined within
    `traders_tab.kv`.
    """


    # References to component widgets
    table_rows: BoxLayout

    selected_trader_row: typing.Optional[TraderRow] = ObjectProperty(
        None, allownone=True)
    """The selected trader's table row, or `None` when unselected."""

    trader_names_to_rows: typing.Dict[str, TraderRow]
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
        TraderPopup(trader=None).open()

    def on_simmodel_trader_added(self,
        model: 'SimModel',
        trader: 'Trader'
    ) -> None:
        """Add a table row for the newly added `trader`."""
        trader_row = TraderRow(tab=self,
            trader_name=trader.get_name(),
            trading_algorithm=trader.get_algorithm_name(),
            initial_funds=trader.get_initial_funds(),
            trading_fee=trader.get_trading_fee())

        self.table_rows.add_widget(trader_row)
        self.trader_names_to_rows[trader.get_name()] = trader_row


    def on_edit_clicked(self
    ) -> None:
        """Show a popup to edit `selected_trader_row`."""
        assert self.selected_trader_row is not None, \
            'Edit button clicked without a trader row selected.'

        model = App.get_running_app().get_controller().get_model()
        trader = model.get_trader(self.selected_trader_row.trader_name)

        TraderPopup(trader=trader).open()


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
