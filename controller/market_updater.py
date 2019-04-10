"""Defines `MarketUpdater` and supporting classes."""


__copyright__ = 'Copyright © 2019, Erik Anderson, James Abernathy, and Tyler Gerritsen'
__license__ = 'MIT'


import enum
import typing

from kivy.clock import (
    Clock, ClockEvent)

# Local package imports at end of file to resolve circular dependencies




class UnexpectedDatasourceUnconfirmError(RuntimeError):
    """An exception raised when the `MarketDatasource` becomes unconfirmed
    while the `MarketUpdater` is playing or paused.
    """

    updater_state: 'MarketUpdater.State'
    """The state of the `MarketUpdater` when the datasource unconfirmed."""

    def __init__(self,
        updater_state: 'MarketUpdater.State'
    ) -> None:
        self.updater_state = updater_state
        super().__init__('The market datasource was unexpectedly unconfirmed '
            'while its market updater was in the {!r} state.'.format(
                updater_state.name))




class MarketUpdater(object):
    """Periodically gets data from a price datasource and channels it into the
    `model.StockMarket`. The data flow starts out stopped (called reset), and
    can be started with `.play()` and paused with `.pause()`.
    """


    class State(enum.Enum):
        """Enumeration of all possible `MarketUpdater` states."""
        RESET = 0
        """State of `MarketUpdater` when stopped."""

        PLAYING = 1
        """State of `MarketUpdater` when periodically feeding prices into the
        `model.StockMarket`.
        """

        PAUSED = 2
        """State of the `MarketUpdater` when temporarilly halted after having
        fed some data into the `model.StockMarket`.
        """


    _parent_controller: 'SimController'
    """This updater's owning simulation controller."""

    _state: MarketUpdater.State
    """Status of this updater controlling its activity."""

    _update_timer: typing.Optional[ClockEvent]
    """A timer updater started by Kivy while playing, or `None` in other
    states.
    """

    #TODO: Events:
    #   MARKET_UPDATER_PAUSED
    #   MARKET_UPDATER_PLAYING
    #   MARKET_UPDATER_RESET


    def __init__(self,
        controller: 'SimController'
    ) -> None:
        """Start this new `MarketUpdater` in a paused state."""
        self._parent_controller = controller
        self._state = self.State.RESET
        self._update_timer = None


    def is_playing(self
    ) -> bool:
        """Return `True` if this `MarketUpdater` is updating."""
        return self._state == self.State.PLAYING

    def play(self
    ) -> None:
        """Start or resume periodically delivering prices to the
        `model.StockMarket` from the `_controller`'s `MarketDatasource`.
        """
        if self.is_playing():
            return  # Already playing

        datasource = self._parent_controller.get_datasource()
        if self.is_paused():
            if not datasource.is_confirmed():
                self.reset()
                raise UnexpectedDatasourceUnconfirmError(self.State.PAUSED)
        else:  # Currently reset
            datasource.confirm()

        self._state = self.State.PLAYING
        # TODO MARKET_UPDATER_PLAYING

        # Resume periodic updates
        self._update_timer = Clock.schedule_interval(
            self._add_market_prices_from_datasource, 1.0)
        # Make first update immediately
        self._add_market_prices_from_datasource()


    def is_paused(self
    ) -> bool:
        """Return `True` if this `MarketUpdater` was playing but was then
        paused.
        """
        return self._state == self.State.PAUSED

    def pause(self
    ) -> None:
        """Pause this `MarketUpdater`, halting the flow of prices from
        `MarketDatasource` to `model.StockMarket`.
        """
        if not self.is_playing():
            return  # No activity to pause

        if self._update_timer is not None:
            self._update_timer.cancel()
            self._update_timer = None

        self._state = self.State.PAUSED
        # TODO MARKET_UPDATER_PAUSED


    def reset(self
    ) -> None:
        """Stops any paused or playing updates, resets the `model`'s market and
        trader accounts, and unlocks the datasource.
        """
        if not (self.is_playing() or self.is_paused()):
            return  # Already reset

        self.pause()  # Stop updates if playing

        self._state = self.State.RESET
        #TODO MARKET_UPDATER_RESET

        self._parent_controller.get_model().clear()
        self._parent_controller.get_datasource().unconfirm()


    def _add_market_prices_from_datasource(self
    ) -> None:
        """Get the current prices from the datasource if an update is
        confirmed, and call appropriate simulation module functions to update
        those prices.
        """
        if not self._parent_controller.is_confirmed():
            self.reset()
            raise UnexpectedDatasourceUnconfirmError(self.State.PLAYING)

        time_and_prices = self._parent_controller.get_datasource().get_next_prices()
        if not time_and_prices:  # Ran out of data
            self.pause()
            return

        market = self._parent_controller.get_model().get_stock_market()
        market.add_next_prices(*time_and_prices)




# Imported last to avoid circular dependencies
from controller.sim_controller import SimController
