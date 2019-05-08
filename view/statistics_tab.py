"""Defines `StatisticsTab` and supporting classes."""


__copyright__ = 'Copyright © 2019, Erik Anderson, James Abernathy, and Tyler Gerritsen'
__license__ = 'MIT'


import typing
import numbers

from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.properties import  StringProperty
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner

import os

# Local package imports duplicated at end of file to resolve circular dependencies
if typing.TYPE_CHECKING:
    from controller.sim_controller import SimController


class SaveDialog(FloatLayout):
    """Class for the SaveDialog popup"""

    save = ObjectProperty(None)
    cancel = ObjectProperty(None)


class StatisticsTab(TabbedPanelItem):
    """Class associated with the `<StatisticsTab>` template defined within
    `statistics_tab.kv`.
    """

    bot_spinner = ObjectProperty(None)
    """Used for retrieving which bot user has selected"""

    statistics_overall_label_text = StringProperty("No data")
    """String Property for updating overall label"""

    statistics_daily_label_text = StringProperty("No data")
    """String Property for updating daily label"""


    def __init__(self,
        **kwargs
    ) -> None:
        super(StatisticsTab, self).__init__(**kwargs)
        Clock.schedule_interval(self.update_labels, 1)


        controller = App.get_running_app().get_controller()
        model = controller.get_model()

        model.bind(
            SIMMODEL_TRADER_ADDED=self.on_simmodel_trader_added,
            SIMMODEL_TRADER_REMOVED=self.on_simmodel_trader_removed)

    def update_labels(self,
        dt
    ) -> None:
        if self.get_controller().get_model().get_trader(self.bot_spinner.text):

            statistics_overall: dict = self.get_controller().get_model().get_trader(
                self.bot_spinner.text).get_account().get_statistics_overall()
            if statistics_overall:
                self.statistics_overall_label_text = self._get_readable_data(statistics_overall)

            statistics_daily: dict = self.get_controller().get_model().get_trader(
                self.bot_spinner.text).get_account().get_statistics_overall()
            if statistics_daily:
                self.statistics_overall_label_text = self._get_readable_data(statistics_daily)


    def get_controller(self
    ) -> 'SimController':
        return App.get_running_app().get_controller()


    def get_trader_list(self,
        controller: 'SimController'
    ) -> [str]:
        """Build and return a list of strings of trader names currently in the
        simulation.
        """
        trader_names: [str] = []
        for trader in controller.get_model().get_traders():
            trader_names.append(trader.get_name())
        return trader_names


    def show_save(self
    ) -> None:
        """Open save dialog."""

        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()


    def save(self,
        path,
        filename
    ) -> None:
        """Start os write stream and save to filename in specified path. """
        with open(os.path.join(path, filename), 'w') as stream:
            stream.write("Daily:\n" + self.statistics_daily_label_text + "\n")
            stream.write("Overall:\n" + self.statistics_overall_label_text + "\n")

        self.dismiss_popup()


    def dismiss_popup(self
    ) -> None:
        """Close popup"""
        self._popup.dismiss()


    def on_simmodel_trader_added(self,
        model: 'SimModel',
        trader: 'Trader'
    ) -> None:
        self._update_spinner()


    def on_simmodel_trader_removed(self,
        model: 'SimModel',
        trader: 'Trader'
    ) -> None:
        self._update_spinner()

    def _get_readable_data(self,
        data: dict
    ) -> str:
        """Return a readable str for a dict. Account for money values."""
        formatted_str = ''
        for key, value, in data.items():
            if isinstance(value, numbers.Number):

                if value < 0:
                    formatted_str += "{}: -${:,.2f}".format(key, -value)
                else:
                    formatted_str += "{}: ${:,.2f}".format(key, value)
            else:
                formatted_str += "{}: {}".format(key, value)
        return formatted_str

    def _update_spinner(self
    ) -> None:
        """Update the spinner text and values depending on which traders are
        active in the simulation.
        """

        if len(self.get_trader_list(self.get_controller())) == 0:
            self.bot_spinner.text = "No bots added"
        else:
            self.bot_spinner.text = self.get_trader_list(self.get_controller())[0]
            self.bot_spinner.values = self.get_trader_list(self.get_controller())


# Imported last to avoid circular dependencies
#from controller.sim_controller import SimController
from model.sim_model import SimModel
from model.trader import Trader
