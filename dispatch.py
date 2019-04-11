"""Defines `Dispatcher` and supporting classes."""


__copyright__ = 'Copyright © 2016 Matthew Reid'
__license__ = 'MIT'


import typing




class EventListeners(object):
    """Holds references to event names and subscribed listeners.

    This is used internally by :class:`Dispatcher`.
    """
    __slots__ = ('name', 'listeners')

    name: str

    listeners: typing.List[typing.Callable]


    def __init__(self,
        name: str
    ) -> None:
        self.name = name
        self.listeners = []


    def add_listener(self,
        callback: typing.Callable
    ) -> None:
        self.listeners.append(callback)


    def remove_listener(self,
        callback: typing.Callable
    ) -> None:
        self.listeners.remove(callback)


    def __call__(self,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> bool:
        """Dispatch the event to listeners.

        Called by :meth:`~Dispatcher.emit`
        """
        for callback in self.listeners:
            if callback(*args, **kwargs) is False:
                return False
        return True  # All listeners notified


    def __repr__(self
    ) -> str:
        return '<{}: {}>'.format(self.__class__, self)


    def __str__(self
    ) -> str:
        return self.name




class Dispatcher(object):
    """Core class used to enable all functionality in the library.

    Interfaces with :class:`EventListeners` objects upon instance creation.

    Events can be created by calling :meth:`register_events` or by the subclass
    definition::

        class Foo(Dispatcher):
            EVENTS = ['awesome_event', 'on_less_awesome_event']

    Once defined, an event can be dispatched to listeners by calling :meth:`emit`.
    """
    __initialized_subclasses: typing.ClassVar[typing.Set[typing.Type['Dispatcher']]] = set()

    __events_combined: typing.ClassVar[typing.Set[str]]

    __event_listeners: typing.Dict[str, EventListeners]


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
                    events_combined |= set(base_cls.EVENTS)
                except AttributeError:
                    pass
            cls.__events_combined = events_combined
            Dispatcher.__initialized_subclasses.add(cls)

        instance = super(Dispatcher, cls).__new__(cls, *args, **kwargs)  # type: ignore
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
        self.__event_listeners.update((name, EventListeners(name))
            for name in names if name not in self.__event_listeners)


    def bind(self,
        **event_callbacks: typing.Callable
    ) -> None:
        """Subscribe to events.

        Keyword arguments are used with the event names as keys
        and the callbacks as values::

            class Foo(Dispatcher):
                EVENTS = ['awesome_event']

            foo = Foo()

            foo.bind(awesome_event=my_listener.on_foo_awesome_event)
            foo.bind(awesome_event=other_listener.on_other_awesome_event)

        The callbacks are stored as weak references and their order is not
        maintained relative to the order of binding.
        """
        for name, callback in event_callbacks.items():
            self.__event_listeners[name].add_listener(callback)


    def unbind(self,
        *callbacks: typing.Callable
    ) -> None:
        """Unsubscribe from events.

        Multiple bound methods can be removed at once.
        """
        for listeners in self.__event_listeners.values():
            for callback in callbacks:
                listeners.remove_listener(callback)


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
    ) -> EventListeners:
        """Retrieve an EventListeners object by name.

        Args:
            name (str): The name of the :class:`EventListeners` object to retrieve

        Returns:
            The :class:`EventListeners` instance for the event definition

        .. versionadded:: 0.1.0
        """
        return self.__event_listeners[name]




if __name__ == '__main__':
    # Simple test of event dispatch
    class Test(Dispatcher):
        EVENTS = ['EVENT_A', 'EVENT_B']
        def __init__(self):
            pass

    test = Test()
    test.bind(EVENT_A=print, EVENT_B=print)
    test.emit('EVENT_A', 'Event A fired.')
    test.emit('EVENT_B', 'Event B fired.')
    print('test =', dir(test))
