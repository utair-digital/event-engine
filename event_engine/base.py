import logging
from abc import ABCMeta
from abc import abstractmethod
from typing import Collection, Callable, Dict, Type, List, Union, Protocol, Optional, runtime_checkable

from .event import Event


@runtime_checkable
class Tracer(Protocol):
    async def get_trace_string(self) -> str:
        ...

    @classmethod
    async def from_trace_string(cls, trace: str) -> "Tracer":
        ...


@runtime_checkable
class Bus(Protocol):
    async def send(self, event: Event):
        ...


class BaseDeserializer:
    @classmethod
    def deserialize(cls, event_data: dict) -> dict:
        raise NotImplementedError


class BaseSerializer:
    @classmethod
    def serialize(cls, event: Event) -> dict:
        raise NotImplementedError


class BaseObserver(metaclass=ABCMeta):
    @abstractmethod
    async def handle_event(self, event: Event) -> None:
        raise NotImplementedError


class BaseObservable(metaclass=ABCMeta):

    __observers__: Collection

    @abstractmethod
    def add_observer(self, observer: BaseObserver) -> None:
        raise NotImplementedError

    @abstractmethod
    def remove_observer(self, observer: BaseObserver) -> None:
        raise NotImplementedError

    @abstractmethod
    async def notify_observers(self, event: Event) -> None:
        raise NotImplementedError

    @abstractmethod
    def __notify__(self, event: Event) -> None:
        raise NotImplementedError


class BaseEventManager:

    _binds: Dict[Type[Event], BaseObservable]

    def __init__(
        self,
        logger: logging.Logger = logging.getLogger("event_manager"),
        tracer: Optional[Tracer] = None,
        bus: Optional[Bus] = None,
    ):
        self._binds: Dict[Type[Event], BaseObservable] = dict()
        self.logger = logger

        if tracer is not None and not isinstance(tracer, Tracer):
            raise Exception("not valid interface of tracer")
        self.tracer = tracer

        if bus is not None and not isinstance(bus, Bus):
            raise Exception("not valid interface of bus")
        self.bus = bus

    @abstractmethod
    def register(
        self,
        events: List[Type[Event]],
        handler: Union[BaseObserver, Callable[[Event], None]],
        is_type_check: bool = False,
    ) -> None:
        """
        Bind events with handler

        Args:
            events (list): Events
            handler (Handler): Handler
            is_type_check (bool): Check duplicate handlers

        """
        raise NotImplementedError

    @abstractmethod
    async def raise_event(self, event: Event) -> None:
        """
        Raise event

        Args:
            event (Event): Event object

        """
        raise NotImplementedError

    @abstractmethod
    async def _raise_event(self, event: Event) -> None:
        """
        Raise event

        Args:
            event (Event): Event object

        """
        raise NotImplementedError

    @abstractmethod
    def un_register(self, event: Event, handler: Union[BaseObserver, Callable[[Event], None]]) -> None:
        raise NotImplementedError

    @abstractmethod
    def _bind(
        self, event: Type[Event], handler: Union[BaseObserver, Callable[[Event], None]], is_type_check: bool = False
    ) -> None:
        """
        Bind event with handler

        Args:
            event (list): Event
            handler (Handler): Handler
            is_type_check (bool): Check duplicate handlers

        """
        raise NotImplementedError
