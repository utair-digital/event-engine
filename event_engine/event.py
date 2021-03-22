from typing import Union, Dict
from .base import BaseEvent
from .exceptions import EventBuildingError


class Event(BaseEvent):
    """
    Класс события.
    Отвечает за передачу данных обработчику события, либо в шину кафки
    """

    def __init__(
            self,
            data: object,
            event_key: str = None,
            is_published: bool = False,
            is_internal: bool = False,
            name: str = None,
            code: int = None
    ):
        self.data = data
        self.name = name
        self.code = code
        if not self.topic and self.is_published:
            raise EventBuildingError("Publishable event must contain topic")
        self.is_published = is_published
        self.is_internal = is_internal or self.is_internal
        self.event_key = event_key if event_key else self.__get_event_key__()

        if not any([
            self.is_publishable,
            self.is_internal
        ]):
            raise EventBuildingError("Event must be at least one of is_internal/is_publishable")

    def serialize(self) -> Dict:
        return {
            'type': str(self.__class__.__name__),
            'data': self.__dict__,
        }

    @classmethod
    def deserialize(cls, event: Dict):
        ev = cls(**event['data'])
        return ev

    def __get_event_key__(self) -> Union[bytes, None]:
        """
        Ключ события позволяет обрабатывать эвенты с одинаковым ключём по порядку
        """
        return bytes(1)
