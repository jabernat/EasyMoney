import types
import typing

from pydispatch.utils import (
    WeakMethodContainer
)


class Event(object):
    """Holds references to event names and subscribed listeners

    This is used internally by :class:`Dispatcher`.
    """
    __slots__ = ('name', 'listeners')
    def __init__(self, name):
        self.name = name
        self.listeners = WeakMethodContainer()
    def add_listener(self, callback):
        self.listeners.add_method(callback)
    def remove_listener(self, obj):
        if isinstance(obj, (types.MethodType, types.FunctionType)):
            self.listeners.del_method(obj)
        else:
            self.listeners.del_instance(obj)
    def __call__(self, *args, **kwargs):
        """Dispatches the event to listeners

        Called by :meth:`~Dispatcher.emit`
        """
        for m in self.listeners.iter_methods():
            r = m(*args, **kwargs)
            if r is False:
                return r
    def __repr__(self):
        return '<{}: {}>'.format(self.__class__, self)
    def __str__(self):
        return self.name

class Dispatcher(object):
    """Core class used to enable all functionality in the library

    Interfaces with :class:`Event` objects upon instance creation.

    Events can be created by calling :meth:`register_event` or by the subclass
    definition::

        class Foo(Dispatcher):
            _events_ = ['awesome_event', 'on_less_awesome_event']

    Once defined, an event can be dispatched to listeners by calling :meth:`emit`.
    """
    __initialized_subclasses = set()
    __skip_initialized = True
    def __new__(cls, *args, **kwargs):
        def iter_bases(_cls):
            if _cls is not object:
                yield _cls
                for b in _cls.__bases__:
                    for _cls_ in iter_bases(b):
                        yield _cls_
        skip_initialized = Dispatcher._Dispatcher__skip_initialized
        if not skip_initialized or cls not in Dispatcher._Dispatcher__initialized_subclasses:
            events = set()
            for _cls in iter_bases(cls):
                for attr in dir(_cls):
                    _events = getattr(_cls, '_events_', [])
                    events |= set(_events)
            cls._EVENTS_ = events
            if skip_initialized:
                Dispatcher._Dispatcher__initialized_subclasses.add(cls)
        obj = super(Dispatcher, cls).__new__(cls)
        obj._Dispatcher__init_events()
        return obj
    def __init__(self, *args, **kwargs):
        # Everything is handled by __new__
        # This is only here to prevent exceptions being raised
        pass
    def __init_events(self):
        if hasattr(self, '_Dispatcher__events'):
            return
        self.__events = {}
        for name in self._EVENTS_:
            self.__events[name] = Event(name)
    def register_event(self, *names):
        """Registers new events after instance creation

        Args:
            *names (str): Name or names of the events to register
        """
        for name in names:
            if name in self.__events:
                continue
            self.__events[name] = Event(name)
    def bind(self, **kwargs):
        """Subscribes to events.

        Keyword arguments are used with the Event names as keys
        and the callbacks as values::

            class Foo(Dispatcher):
                _events_ = ['awesome_event']

            foo = Foo()

            foo.bind(awesome_event=my_listener.on_foo_awesome_event)
            foo.bind(awesome_event=other_listener.on_other_awesome_event)

        The callbacks are stored as weak references and their order is not
        maintained relative to the order of binding.
        """
        for name, cb in kwargs.items():
            self.__events[name].add_listener(cb)
    def unbind(self, *args):
        """Unsubscribes from events.

        Multiple arguments can be given. Each of which can be either the method
        that was used for the original call to :meth:`bind` or an instance
        object.

        If an instance of an object is supplied, any previously bound Events
        will be 'unbound'.
        """
        for e in self.__events.values():
            for arg in args:
                e.remove_listener(arg)
    def emit(self, name, *args, **kwargs):
        """Dispatches an event to any subscribed listeners

        Note:
            If a listener returns :obj:`False`, the event will stop dispatching to
            other listeners. Any other return value is ignored.

        Args:
            name (str): The name of the :class:`Event` to dispatch
            *args (Optional): Positional arguments to be sent to listeners
            **kwargs (Optional): Keyword arguments to be sent to listeners
        """
        return self.__events[name](*args, **kwargs)
    def get_dispatcher_event(self, name):
        """Retrieves an Event object by name

        Args:
            name (str): The name of the :class:`Event` object to retrieve

        Returns:
            The :class:`Event` instance for the event definition

        .. versionadded:: 0.1.0
        """
        return self.__events[name]
