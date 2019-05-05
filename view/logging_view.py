"""Defines `LoggingView` and supporting classes."""


__copyright__ = 'Copyright © 2019, Erik Anderson, James Abernathy, and Tyler Gerritsen'
__license__ = 'MIT'


import logging
import pprint
import typing

import dispatch

# Local package imports duplicated at end of file to resolve circular dependencies
if typing.TYPE_CHECKING:
    from controller.sim_controller import SimController
    from model.sim_model import SimModel
    from model.trader import Trader
    from model.trader_account import TraderAccount




class _LazyPPrinter(object):
    """Delays pretty-printing until a string representation is requested.
    This avoids formatting unused strings when messages are filtered out.
    """
    __slots__ = ('_pprinter', '_data', '_string')

    _pprinter: pprint.PrettyPrinter
    """The pretty-printer to use if necessary."""

    _data: typing.Any
    """Data to pretty-print if necessary."""

    _string: typing.Optional[str]
    """The pretty-printed version of `_data` once requested."""

    def __init__(self,
        pprinter: pprint.PrettyPrinter,
        data: typing.Any
    ) -> None:
        self._pprinter = pprinter
        self._data = data
        self._string = None

    def __str__(self
    ) -> str:
        """Return a lazily pretty-printed version of `_data`."""
        if self._string is None:  # Can't be lazy anymore
            self._string = self._pprinter.pformat(self._data)
        return self._string




class LoggingView(object):
    """MVC view that logs all EasyMoney model and controller events."""


    _pprinter: pprint.PrettyPrinter
    """Pretty printer for formatting objects as nicely-aligned text."""


    _sim_controller: 'SimController'
    """MVC controller tied to an underlying model, both logged by this view."""


    def __init__(self,
        sim_controller: 'SimController'
    ) -> None:
        """Binds all of `sim_controller`'s events for logging."""
        self._pprinter = pprint.PrettyPrinter(indent=4)
        self._logger = logging.getLogger().getChild(self.__module__)
        self._sim_controller = sim_controller


        self._log_all_events(sim_controller.get_datasource())
        self._log_all_events(sim_controller.get_updater())

        model = sim_controller.get_model()
        self._log_all_events(model)
        self._log_all_events(model.get_stock_market())
        model.bind(
            SIMMODEL_TRADER_ADDED=self._on_simmodel_trader_added)

    def _on_simmodel_trader_added(self,
        model: 'SimModel',
        trader: 'Trader'
    )-> None:
        """Register to log a newly-added `trader`'s events."""
        self._log_all_events(trader)
        trader.bind(
            TRADER_ACCOUNT_CREATED=self._on_trader_account_created)

    def _on_trader_account_created(self,
        trader: 'Trader',
        account: 'TraderAccount'
    )-> None:
        """Register to log account events when a trader creates one."""
        self._log_all_events(account)


    def _create_event_logger(self,
        event_name: str
    ) -> typing.Callable[..., None]:
        """Create an event callback function for the specified `event_name`.
        """
        def event_logger(*args, **kwargs):
            # Combine positional and keyword args
            kwargs.update(enumerate(args))

            exception = False
            if 'exception' in kwargs:
                exception = kwargs['exception'] or False

            self._logger.info('%s:\n%s',
                event_name, _LazyPPrinter(self._pprinter, kwargs),
                exc_info=exception)

        return event_logger

    def _log_all_events(self,
        dispatcher: dispatch.Dispatcher
    ) -> None:
        """Bind to all of `dispatcher`'s emitted events to log them."""
        dispatcher.bind(**{event_name: self._create_event_logger(event_name)
            for event_name in dispatcher.EVENTS})




# Imported last to avoid circular dependencies
from controller.sim_controller import SimController
from model.sim_model import SimModel
from model.trader import Trader
from model.trader_account import TraderAccount
