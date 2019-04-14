"""Defines `TraderExample` trading algorithm and supporting classes."""


__copyright__ = 'Copyright © 2019, Erik Anderson, James Abernathy, and Tyler Gerritsen'
__license__ = 'MIT'


import typing

from model.trader import Trader
from model.stock_market import StockMarket




class TraderExample(Trader):
    """An example trader to exercise the `SimModel` stock market simulation.
    """


    @classmethod
    def get_algorithm_name(cls
    ) -> str:
        """Return this `Trader` subclass' identifying algorithm name, unique
        to the `SimModel` that it is registered within.
        """
        return 'Example'

    @classmethod
    def get_algorithm_settings_defaults(cls
    ) -> typing.Dict[str, typing.Any]:
        """Return a default settings `dict` appropriate for this `Trader`
        subclass.
        """
        return {}

    @classmethod
    def get_algorithm_settings_ui_definition(cls
    ) -> typing.Dict[str, typing.Any]:
        """Return a `dict` which defines how the Kivy GUI toolkit can render
        this `Trader` subclass' configuration controls. Its contents mirror the
        expected structure of settings dictionaries. The organization of this
        dictionary is defined by Kivy, and used exclusively within
        `window_view`.
        """
        return {}


    def set_algorithm_settings(self,
        algorithm_settings: typing.Dict[str, typing.Any]
    ) -> None:
        """Replace this trader's algorithm-specific settings `dict` with
        `algorithm_settings`.

        These new settings are validated by the `Trader`'s subclass, and raised
        exceptions extend `TypeError` and `ValueError`.

        Triggers `TRADER_ALGORITHM_SETTINGS_CHANGED` if successful.
        """
        # TODO: Validate algorithm settings

        self._set_algorithm_settings(algorithm_settings)


    def trade(self
    ) -> None:
        """Choose to buy or sell based on updated stock market conditions."""
        # TODO: Implement simple trading logic
        pass
