"""Defines `Dispatcher` and supporting classes."""


__copyright__ = 'Original python-dispatch 0.1.2 Copyright © 2016 Matthew Reid'
__license__ = 'MIT'


import typing




class RecursiveDispatchError(Exception):
    """An exception raised when attempting to dispatch an event while it is
    already dispatching.
    """

    event: '_EventListeners'
    """The event that was recursively dispatched."""

    def __init__(self,
        event: '_EventListeners'
    ) -> None:
        self.event = event
        super().__init__('Invalid attempt to recursively emit event {}.'.format(
            event))




_Callback = typing.Callable[..., typing.Optional[bool]]
"""Type for all event listener callbacks.
Callbacks can return `False` to halt dispatching to further listeners.
"""




def _remove_if_found(collection, entry):
    try:
        collection.remove(entry)
    except (KeyError, ValueError):
        pass  # Ignore if not found




class _EventListeners(object):
    """Holds references to event names and subscribed listeners.

    This is used internally by :class:`Dispatcher`.
    """
    __slots__ = ('name', '_callbacks',
        '_calling',
        '_pending_additions', '_pending_removals')

    name: str

    _callbacks: typing.List[_Callback]
    """All registered callbacks, preserving registration order."""

    _calling: bool
    """`True` while this event dispatches to its listeners."""

    _pending_additions: typing.List[_Callback]
    """Callbacks to add after `_calling` becomes `False`, preserving
    registration order.
    """

    _pending_removals: typing.Set[_Callback]
    """Callbacks to remove after `_calling` becomes `False`."""


    def __init__(self,
        name: str
    ) -> None:
        self.name = name
        self._callbacks = []

        self._calling = False
        self._pending_additions = []
        self._pending_removals = set()


    def add(self,
        callback: _Callback
    ) -> None:
        if not self._calling:
            if callback not in self._callbacks:
                self._callbacks.append(callback)

        elif callback not in self._pending_additions:
            # Add after done calling
            _remove_if_found(self._pending_removals, callback)
            if callback not in self._callbacks:
                self._pending_additions.append(callback)


    def remove(self,
        callback: _Callback
    ) -> None:
        if not self._calling:
            _remove_if_found(self._callbacks, callback)

        elif callback not in self._pending_removals:
            # Remove after done calling
            _remove_if_found(self._pending_additions, callback)
            if callback in self._callbacks:
                self._pending_removals.add(callback)


    def remove_all(self,
    ) -> None:
        if not self._calling:
            self._callbacks.clear()

        else:  # Remove all after done calling
            self._pending_additions.clear()
            self._pending_removals.update(self._callbacks)


    def _apply_pending(self
    ) -> None:
        """Applies pending callback additions and removals."""
        assert not self._calling, \
            'Cannot apply pending callbacks while calling.'

        for callback in self._pending_removals:
            self._callbacks.remove(callback)
        self._pending_removals.clear()

        self._callbacks.extend(self._pending_additions)
        self._pending_additions.clear()


    def __call__(self,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> bool:
        """Dispatch the event to listeners.

        Called by :meth:`~Dispatcher.emit`
        """
        if self._calling:
            raise RecursiveDispatchError(self)

        self._calling = True
        try:
            cancelled = False
            for callback in self._callbacks:
                if callback(*args, **kwargs) is False:
                    # Don't notify any more listeners
                    cancelled = True
                    break
            return not cancelled
        finally:
            self._calling = False
            self._apply_pending()


    def __repr__(self
    ) -> str:
        return '<{}: {}>'.format(self.__class__.__name__, self)


    def __str__(self
    ) -> str:
        return self.name




class Dispatcher(object):
    """Core class used to enable all functionality in the library.

    Interfaces with :class:`_EventListeners` objects upon instance creation.

    Events can be created by calling :meth:`register_events` or by the subclass
    definition::

        class Foo(Dispatcher):
            EVENTS = frozenset(['awesome_event', 'on_less_awesome_event'])

    Once defined, an event can be dispatched to listeners by calling :meth:`emit`.
    """
    __initialized_subclasses: typing.ClassVar[typing.Set[typing.Type['Dispatcher']]] = set()

    __events_combined: typing.ClassVar[typing.Set[str]]

    __event_listeners: typing.Dict[str, _EventListeners]

    EVENTS: typing.ClassVar[typing.FrozenSet[str]]
    """Set of event names broadcast by `Dispatcher` subclasses."""


    def __new__(cls,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> 'Dispatcher':
        def iter_bases(cls_):
            if cls_ is not object:
                yield cls_
                for base in cls_.__bases__:
                    for base_cls in iter_bases(base):
                        yield base_cls

        if cls not in Dispatcher.__initialized_subclasses:
            events_combined: typing.Set[str] = set()
            for base_cls in iter_bases(cls):
                try:
                    events_combined |= base_cls.EVENTS
                except AttributeError:
                    pass
            cls.__events_combined = events_combined
            Dispatcher.__initialized_subclasses.add(cls)

        new = super(Dispatcher, cls).__new__
        if new is object.__new__:
            instance = new(cls)  # No other arguments allowed for object
        else:
            instance = new(cls, *args, **kwargs)  # type: ignore

        instance.__event_listeners = {}
        instance.register_events(*cls.__events_combined)
        return instance


    def __init__(self,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        # Everything is handled by __new__
        pass


    def register_events(self,
        *names: str
    ) -> None:
        """Register new events after instance creation.

        Args:
            *names (str): Name or names of the events to register
        """
        self.__event_listeners.update((name, _EventListeners(name))
            for name in names if name not in self.__event_listeners)


    def bind(self,
        **event_callbacks: _Callback
    ) -> None:
        """Subscribe to events.

        Keyword arguments are used with the event names as keys
        and the callbacks as values::

            class Foo(Dispatcher):
                EVENTS = frozenset(['awesome_event'])

            foo = Foo()

            foo.bind(awesome_event=my_listener.on_foo_awesome_event)
            foo.bind(awesome_event=other_listener.on_other_awesome_event)

        The callbacks are stored as weak references and their order is not
        maintained relative to the order of binding.
        """
        for name, callback in event_callbacks.items():
            self.__event_listeners[name].add(callback)


    def unbind(self,
        *callbacks: _Callback
    ) -> None:
        """Unsubscribe from events.

        Multiple bound methods can be removed at once.
        """
        for listeners in self.__event_listeners.values():
            for callback in callbacks:
                listeners.remove(callback)


    def emit(self,
        name: str,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> bool:
        """Dispatch an event to any subscribed listeners.

        Note:
            If a listener returns :obj:`False`, the event will stop dispatching to
            other listeners. Any other return value is ignored.

        Args:
            name (str): The name of the event to dispatch
            *args (Optional): Positional arguments to be sent to listeners
            **kwargs (Optional): Keyword arguments to be sent to listeners
        """
        return self.__event_listeners[name](*args, **kwargs)


    def get_event_listeners(self,
        name: str
    ) -> _EventListeners:
        """Retrieve an _EventListeners object by name.

        Args:
            name (str): The name of the :class:`_EventListeners` object to retrieve

        Returns:
            The :class:`_EventListeners` instance for the event definition

        .. versionadded:: 0.1.0
        """
        return self.__event_listeners[name]




if __name__ == '__main__':
    # Simple test of event dispatch
    class Test(Dispatcher):
        EVENTS = frozenset([
            'EVENT_A',
            'EVENT_B'])
        def __init__(self):
            pass

    test = Test()

    def b_listener_3(
        msg: str
    ) -> None:
        print('b_listener_3', msg)

    def b_listener_1(
        msg: str
    ) -> None:
        print('b_listener_1', msg)
        test.unbind(b_listener_1)
        test.bind(EVENT_B=b_listener_3)

    def b_listener_2(
        msg: str
    ) -> None:
        print('b_listener_2', msg)

    test.bind(EVENT_A=print)
    test.bind(EVENT_B=b_listener_1)
    test.bind(EVENT_B=b_listener_2)
    test.emit('EVENT_A', 'Event A fired.')
    test.emit('EVENT_B', 'Event B-1 fired.')
    test.emit('EVENT_B', 'Event B-2 fired.')
