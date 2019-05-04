"""Defines `WindowView` and supporting classes."""


__copyright__ = 'Copyright © 2019, Erik Anderson, James Abernathy, and Tyler Gerritsen'
__license__ = 'MIT'


import typing

from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.lang import Builder

from view.trading_bots_tab import TradingBotsTab
from view.stock_symbols_tab import StockSymbolsTab
from view.simulation_tab import SimulationTab
from view.statistics_tab import StatisticsTab

# Local package imports duplicated at end of file to resolve circular dependencies
if typing.TYPE_CHECKING:
    from controller.sim_controller import SimController




class RootWidget(TabbedPanel):
    """Class associated with the `<RootWidget>` remplate defined within
    `window_view.kv`.
    """
    pass




class WindowView(App):
    """Kivy application serving as a view for EasyMoney's MVC architecture."""


    _sim_controller: 'SimController'
    """MVC controller tied to an underlying model and driven by this view."""


    @classmethod
    def load_templates(cls
    ) -> None:
        """Loads Kivy UI template files (`*.kv`) for all widgets."""
        TradingBotsTab.load_templates()
        StockSymbolsTab.load_templates()
        SimulationTab.load_templates()
        StatisticsTab.load_templates()

        Builder.load_file('view/window_view.kv')


    def __init__(self,
        sim_controller: 'SimController'
    ) -> None:
        """Prepare to build and run this window by loading UI templates."""
        super().__init__()

        self._sim_controller = sim_controller

        self.load_templates()


    def get_controller(self
    ) -> 'SimController':
        """Return the MVC controller driven by this view, which allows access
        to the underlying MVC model.
        """
        return self._sim_controller


    def build(self
    ) -> RootWidget:
        """Construct widget classes based on loaded `*.kv` template
        definitions.
        """
        return RootWidget()


    def run(self
    ) -> None:
        """Start this application by showing its window, and block until the
        window closes.
        """
        # This method doesn't add anything to the superclass method other than
        # highlighting it for programmers.
        super().run()




# Imported last to avoid circular dependencies
from controller.sim_controller import SimController
