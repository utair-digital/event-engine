import msgpack
from typing import Union, Dict
from .base import BaseEvent
from .exceptions import EventBuildingError


class Event(BaseEvent):
    """
    Класс события.
    Отвечает за передачу данных обработчику события, либо в шину кафки
    По сути обычный Data Transfer Object (DTO)
    """

    name: str = 'Unnamed event'
    code: int = 0
    data: object = None

    is_internal: bool = True        # Флаг, обозначающий, что сообщение должно быть отправлено внутри приложения

    is_published: bool = False      # Флаг, обозначающий, что сообщение было отправлено через шину
    is_publishable: bool = False    # Флаг, обозначающий, что сообщение должно быть отправлено в кафку

    event_key: str = None           # Ключ события требуется для обработки события по порядку,
    # события с одинаковым ключем попадут в одну partition в кафке и будут обработаны последовательно

    topic: str = None               # Топик события, на которое должен быть подписан клиент, чтобы его получить

    def __init__(
            self,
            data: object = None,
            topic: str = None,
            event_key: str = None,
            is_published: bool = False,
            is_internal: bool = False,
            name: str = None,
            code: int = None
    ):
        self.data = data
        if name:
            self.name = name
        if code:
            self.code = code
        self.topic = topic or self.topic
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

    def __get_event_key__(self) -> Union[str, None]:
        """
        Функция генерации ключа события
        По дефолту ключа нет, кафка будет посылать события по разным
        partition round-robin
        """
        return None

    def build_for_kafka(self) -> Dict:
        """
        Собирает сообщения для kafka.send(**build_for_kafka)
        """
        return dict(
            topic=self.topic,
            key=self.event_key,
            value=msgpack.dumps(self.serialize()),
        )
