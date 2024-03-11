from typing import List, Type, Dict, Callable, Union

from opentelemetry import trace

from .base import BaseEventManager
from .event import Event
from .exceptions import (
    InvalidObserverIDError,
    EventNotRegisteredError,
    InvalidEventType,
    InvalidObserverType,
    BusNotDefinedError,
    EventWasNotSentToBus,
)
from .observable import Observable
from .observer import Observer


class EventManager(BaseEventManager):
    """
    Event manager
    """

    def register(
            self,
            events: List[Type[Event]],
            handler: Observer,
            is_type_check: bool = False,
    ) -> None:
        """
        Bind events with handler

        Args:
            events (list): Events
            handler (Handler): Handler
            is_type_check (bool): Check duplicate handlers

        """
        observer_id = handler.observer_id

        if not observer_id or not isinstance(observer_id, str):
            raise InvalidObserverIDError("not valid observer_id: {}".format(observer_id))

        for event in events:
            if not issubclass(event, Event):
                err = InvalidEventType("Invalid event type")
                self.logger.exception(err)
                raise err
            if not (isinstance(handler, Observer) or callable(handler)):
                err = InvalidObserverType("Invalid handler type")
                self.logger.exception(err)
                raise err
            self._bind(event, handler, is_type_check)

    def _bind(
            self,
            event: Type[Event],
            handler: Union[Observer, Callable[[Event], None]],
            is_type_check: bool = False,
    ) -> None:
        """
        Bind event with handler

        Args:
            event (list): Event
            handler (Handler): Handler
            is_type_check (bool): Check duplicate handlers

        """
        if event not in self._binds.keys():
            self._binds[event] = Observable(is_type_check)
        self._binds[event].add_observer(handler)

    async def raise_event(self, event: Event) -> None:
        """
        Raise event

        Args:
            event (Event): Event object

        Raises:
            EventWasNotSentToBus: If there are problems with the bus
            BusNotDefinedError: If you try to send an event to a bus that is not defined

        """
        with trace.get_tracer("event-engine").start_as_current_span(f"EE {event.name}"):
            await self._raise_event(event=event)

    async def _raise_event(
            self,
            event: Event
    ) -> None:
        """
        Raise events

        Args:
            event: Event

        Raises:
            EventWasNotSentToBus: If there are problems with the bus
            BusNotDefinedError: If you try to send an event to a bus that is not defined

        """
        event_type = event.__class__

        if event_type not in self._binds.keys():
            err = EventNotRegisteredError("Raised event is not registered")
            self.logger.exception(err)
            raise err

        if event_type in self._binds.keys():
            if event.is_published:
                # event from bus, must be raising in app
                return await self._binds[event_type].notify_observers(event)

            if all([event.is_publishable, not event.is_published]):
                if self.bus is None:
                    err = BusNotDefinedError("Bus is not defined")
                    self.logger.exception(err)
                    raise err
                try:
                    await self.bus.send(event)
                except Exception as e:
                    self.logger.exception(e)
                    raise EventWasNotSentToBus()
            if not event.is_internal:
                # without raising event in app
                return
            await self._binds[event_type].notify_observers(event)

    def un_register(self, event: Event, handler: Union[Observer, Callable]) -> None:
        """remove handler from event"""
        raise NotImplementedError

    def lookup_event(self, event: Dict) -> Event:
        """
        look up the registered event and return it
        Args:
            event (dict): event data

        Returns:
            event (Event): event object

        Raises
            EventNotRegisteredError: If event is not registered in event engine
        """
        for event_instance in list(self._binds.keys()):
            if str(event_instance.get_default_name()) == event["name"]:
                return event_instance(**event)
        err = EventNotRegisteredError('Event "{}" is not registered'.format(event["type"]))
        self.logger.exception(err)
        raise err
