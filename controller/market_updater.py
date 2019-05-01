"""Defines `MarketUpdater` and supporting classes."""


__copyright__ = 'Copyright © 2019, Erik Anderson, James Abernathy, and Tyler Gerritsen'
__license__ = 'MIT'


import enum
import typing

from kivy.clock import (
    Clock, ClockEvent)

import dispatch

# Local package imports duplicated at end of file to resolve circular dependencies
if typing.TYPE_CHECKING:
    from controller.market_datasource import MarketDatasource
    from model.sim_model import SimModel




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




class MarketUpdater(dispatch.Dispatcher):
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


    _datasource: 'MarketDatasource'
    """The datasource that this updater draws prices from."""

    _model: 'SimModel'
    """The model that this updater inserts prices into."""

    _state: State
    """Status of this updater controlling its activity."""

    _update_timer: typing.Optional[ClockEvent]
    """A timer updater started by Kivy while playing, or `None` in other
    states.
    """

    EVENTS: typing.ClassVar[typing.FrozenSet[str]] = frozenset([
        'MARKETUPDATER_PAUSED',
        'MARKETUPDATER_PLAYING',
        'MARKETUPDATER_RESET'])
    """Events broadcast by the `MarketDatasource`."""


    def __init__(self,
        datasource: 'MarketDatasource',
        model: 'SimModel'
    ) -> None:
        """Start this new `MarketUpdater` in a reset state."""
        self._datasource = datasource
        self._model = model

        self._state = self.State.RESET
        self._update_timer = None

        datasource.bind(
            MARKETDATASOURCE_UNCONFIRMED=self._on_marketdatasource_unconfirmed)


    def _on_marketdatasource_unconfirmed(self,
        datasource: 'MarketDatasource'
    ):
        """Resets this updater if the datasource gets externally unconfirmed.
        """
        self.reset()


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

        if self.is_paused():
            if not self._datasource.is_confirmed():
                self.reset()
                raise UnexpectedDatasourceUnconfirmError(self.State.PAUSED)
        else:  # Currently reset
            self.reset()
            self._datasource.confirm()

        self._state = self.State.PLAYING
        self.emit('MARKETUPDATER_PLAYING',
            updater=self)

        # Resume periodic updates
        INTERVAL_s = 0.0  # Once per frame
        self._update_timer = Clock.schedule_interval(
            self._add_market_prices_from_datasource, INTERVAL_s)
        # Make first update immediately
        self._add_market_prices_from_datasource(elapsed=0.0)


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
        self.emit('MARKETUPDATER_PAUSED',
            updater=self)


    def reset(self
    ) -> None:
        """Stops any paused or playing updates, resets the `model`'s market and
        trader accounts, and unlocks the datasource.
        """
        if not (self.is_playing() or self.is_paused()):
            # return  # Already reset
            pass

        self.pause()  # Stop updates if playing

        self._state = self.State.RESET
        self.emit('MARKETUPDATER_RESET',
            updater=self)

        self._model.reset_market_and_trader_accounts()
        self._datasource.unconfirm()


    def _add_market_prices_from_datasource(self,
        elapsed: float
    ) -> None:
        """Pass current prices from the datasource to the model's
        `StockMarket`. Called periodically by `kivy.clock`.
        """
        if not self._datasource.is_confirmed():
            self.reset()
            raise UnexpectedDatasourceUnconfirmError(self.State.PLAYING)

        time_and_prices = self._datasource.get_next_prices()
        if not time_and_prices:  # Ran out of data
            self.pause()
            return

        self._model.get_stock_market().add_next_prices(*time_and_prices)




# Imported last to avoid circular dependencies
from controller.market_datasource import MarketDatasource
from model.sim_model import SimModel
