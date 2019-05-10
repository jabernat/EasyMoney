"""Defines `StatisticsTab` and supporting classes."""


__copyright__ = 'Copyright © 2019, Erik Anderson, James Abernathy, and Tyler Gerritsen'
__license__ = 'MIT'


import os.path
import typing

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanelItem

# Local package imports duplicated at end of file to resolve circular dependencies
if typing.TYPE_CHECKING:
    from model.sim_model import SimModel
    from model.trader import Trader
    from model.trader_account import TraderAccount




class SaveDialog(BoxLayout):
    """Popup dialog for selecting a save destination."""

    save = ObjectProperty(None)
    """Function to save to a given file path."""

    cancel = ObjectProperty(None)
    """Function to dismiss the popup without saving a file."""

class SaveErrorPopup(Popup):
    """Popup dialog for showing file save errors."""

    error_message = StringProperty()




class StatisticsTab(TabbedPanelItem):
    """Class associated with the `<StatisticsTab>` template defined within
    `statistics_tab.kv`.
    """


    bot_spinner = ObjectProperty(None)
    """Dropdown menu selecting a trader to view statistics for."""

    statistics_overall_label_text = StringProperty()
    """Overall statistics display text."""

    statistics_daily_label_text = StringProperty()
    """Daily statistics display text."""


    def __init__(self,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        super().__init__(*args, **kwargs)

        model = App.get_running_app().get_controller().get_model()
        model.bind(
            SIMMODEL_TRADER_ADDED=self.on_simmodel_trader_added,
            SIMMODEL_TRADER_REMOVED=self.on_simmodel_trader_removed)

        Clock.schedule_once(self.update_statistics, -1)
        Clock.schedule_interval(self.update_statistics, 1)


    @staticmethod
    def format_dollars(
        dollars: float
    ) -> str:
        """Return a positive or negative quantity of `dollars` in `'$9,999.99'`
        form."""
        if dollars < 0:
            return '-${:,.2f}'.format(-dollars)
        else:
            return '${:,.2f}'.format(dollars)

    STATISTIC_FORMATTERS: typing.ClassVar[typing.Dict[str,
        typing.Callable[[str, typing.Any], str]]
    ] = {
        'PROFIT_NET': (lambda key, value:
            'Net Profit: {}'.format(StatisticsTab.format_dollars(value)))}
    """Maps statistic keys to formatter functions for their values."""

    @classmethod
    def statistics_to_string(cls,
        statistics: typing.Dict[str, typing.Any]
    ) -> str:
        """Return a human-readable version of `statistics`."""
        lines = []
        for key, value, in statistics.items():
            try:
                formatter = cls.STATISTIC_FORMATTERS[key]
            except KeyError:  # Generic format
                line = '{}: {}'.format(key, value)
            else:
                line = formatter(key, value)
            lines.append(line)

        lines.sort()
        return '\n'.join(lines)

    def update_statistics(self,
        delta: float
    ) -> None:
        """Periodically update statistics text."""
        model = App.get_running_app().get_controller().get_model()

        statistics_overall = statistics_daily = ''

        selected_trader = model.get_trader(self.bot_spinner.text)
        if selected_trader is not None:
            account = selected_trader.get_account()
            if account:
                # Statistics available from simulation
                statistics_overall = self.statistics_to_string(
                    account.get_statistics_overall())
                statistics_daily = self.statistics_to_string(
                    account.get_statistics_overall())

        self.statistics_overall_label_text = statistics_overall
        self.statistics_overall_label_text = statistics_daily


    def get_active_trader_names(self
    ) -> typing.List[str]:
        """Return a sorted list of trader names currently in the simulation."""
        model = App.get_running_app().get_controller().get_model()

        trader_names = [trader.get_name()
            for trader in model.get_traders()
                if trader.get_account() is not None]
        trader_names.sort()
        return trader_names

    def update_trader_menu(self
    ) -> None:
        """Update the spinner values to reflect traders that are active in the
        simulation.
        """
        traders_list = self.get_active_trader_names()
        self.bot_spinner.values = traders_list

        if self.bot_spinner.text not in traders_list:
            self.bot_spinner.text = traders_list[0] if traders_list else ''

    def on_simmodel_trader_added(self,
        model: 'SimModel',
        trader: 'Trader'
    ) -> None:
        self.update_trader_menu()
        trader.bind(
            TRADER_ACCOUNT_CREATED=self.on_trader_account_created)

    def on_simmodel_trader_removed(self,
        model: 'SimModel',
        trader: 'Trader'
    ) -> None:
        self.update_trader_menu()

    def on_trader_account_created(self,
        trader: 'Trader',
        account: 'TraderAccount'
    ) -> None:
        self.update_trader_menu()


    def show_save(self
    ) -> None:
        """Open save dialog."""

        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        content.filechooser.path = os.getcwd()
        self._popup = Popup(title='Save file', content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def save(self,
        path,
        filename
    ) -> None:
        """Start os write stream and save to filename in specified path. """
        if not filename:
            return

        os.chdir(path)  # Remember chosen folder for next time
        filepath = os.path.join(path, filename)

        try:
            with open(filepath, 'w', encoding='utf_8') as stream:
                stream.write('Trader: ' + self.bot_spinner.text + '\n\n')
                stream.write('Daily Statistics:\n'
                    + self.statistics_daily_label_text + '\n\n')
                stream.write('Overall Statistics:\n'
                    + self.statistics_overall_label_text + '\n')
        except Exception as e:
            popup = SaveErrorPopup(error_message=str(e))
            popup.open()
            return

        self.dismiss_popup()

    def dismiss_popup(self
    ) -> None:
        self._popup.dismiss()




# Imported last to avoid circular dependencies
from model.sim_model import SimModel
from model.trader import Trader
from model.trader_account import TraderAccount
