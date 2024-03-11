from typing import Dict, List

from .base import BaseObservable
from .event import Event
from .exceptions import (
    ObserverAlreadyRegistered,
    InvalidObserverType,
    InvalidEventType,
)
from .observer import Observer


class Observable(BaseObservable):
    __observers__: List[Dict]

    def __init__(self, is_type_check: bool = False):
        """ "
        :param is_type_check: Check duplicate handlers
        """
        self.is_type_check = is_type_check
        self.__observers__ = list()

    def add_observer(
        self,
        observer: Observer,
    ) -> None:
        """
        Add observer
        Args:
            observer (Observer): observer

        """
        if not isinstance(observer, Observer):
            raise InvalidObserverType("Invalid observer type")
        if self.__get_first_observer_instance_index__(observer) != -1:
            raise ObserverAlreadyRegistered("Observer already added")
        if (
            self.is_type_check
            and self.__get_first_observer_type_index__(observer) != -1
        ):
            raise ObserverAlreadyRegistered(
                "Observer with type {} already added".format(str(type(observer)))
            )
        self.__observers__.append(dict(observer=observer))

    def remove_observer(self, observer: Observer) -> None:
        """
        Remove observer
        Args:
            observer (Observer):

        """
        if not isinstance(observer, Observer):
            raise InvalidObserverType("Invalid observer type")
        observer_index = self.__get_first_observer_instance_index__(observer)
        if observer_index != -1:
            self.__observers__.pop(observer_index)

    async def notify_observers(self, event: Event) -> None:
        """
        Send event to observers
        Args:
            event (Event): event object

        """
        if not isinstance(event, Event):
            raise InvalidEventType("Invalid event type")
        await self.__notify__(event)

    async def __notify__(self, event: Event) -> None:
        """
        Send event to observers
        Args:
            event (Event): event object

        """
        for observer in self.__observers__:
            await observer["observer"].handle_event(event)

    def __get_first_observer_instance_index__(self, observer: Observer) -> int:
        """
        Look up firs observer
        Args:
            observer (Observer):

        Returns:
            int
        """
        observers = list(
            filter(lambda x: x["observer"] == observer, self.__observers__)
        )
        if observers:
            return self.__observers__.index(observers[0])
        else:
            return -1

    def __get_first_observer_type_index__(self, observer: Observer) -> int:
        """
        Look up firs observer
        Args:
            observer (Observer):

        Returns:
            int
        """
        observers = list(
            filter(
                lambda x: type(x["observer"]) == type(observer)
                and getattr(x["observer"], "observer_id", None)
                == getattr(observer, "observer_id", None),
                self.__observers__,
            )
        )
        if observers:
            return self.__observers__.index(observers[0])
        else:
            return -1
