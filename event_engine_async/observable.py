import json
import sys
import typing
from os import path

from .base import BaseObservable
from .event import Event
from .observer import Observer

from .exceptions import (
    BaseEventEngineError,
    ObserverAlreadyRegistered,
    InvalidObserverType,
    InvalidEventType,
)


class Observable(BaseObservable):
    """
    Класс наблюдаемого объекта
    """

    __observers__: typing.List

    def __init__(self, is_type_check: bool = False):
        """"
        :param is_type_check: Флаг проверки, что два экземпляра одного класса не обрабатывают событие
        """
        self.is_type_check = is_type_check
        self.__observers__ = list()

    def add_observer(
            self,
            observer: Observer,
    ) -> None:
        """
        Добавить наблюдателя
        :param observer: Наблюдатель
        :return:
        """
        if not isinstance(observer, Observer):
            raise InvalidObserverType("Invalid observer type")
        if self.__get_first_observer_instance_index__(observer) != -1:
            raise ObserverAlreadyRegistered("Observer already added")
        if self.is_type_check and self.__get_first_observer_type_index__(observer) != -1:
            raise ObserverAlreadyRegistered("Observer with type {} already added".format(str(type(observer))))
        self.__observers__.append(dict(observer=observer))

    def remove_observer(self, observer: Observer) -> None:
        """Удалить наблюдателя"""
        if not isinstance(observer, Observer):
            raise InvalidObserverType("Invalid observer type")
        observer_index = self.__get_first_observer_instance_index__(observer)
        if observer_index != -1:
            self.__observers__.pop(observer_index)

    async def notify_observers(self, event: Event) -> None:
        """Сообщить наблюдателю о наступлении события"""
        if not isinstance(event, Event):
            raise InvalidEventType("Invalid event type")
        await self.__notify__(event)

    async def notify_observers_async(self, event: Event, async_task: typing.Callable) -> None:
        """Сообщить наблюдателю о наступлении события (обработка событий запустится в celery)"""
        if not isinstance(event, Event):
            raise InvalidEventType("Invalid event type")
        if not callable(async_task):
            raise BaseEventEngineError("Invalid async function: {}".format(async_task))

        async_task.delay(json.dumps(event.serialize()))

    async def __notify__(self, event: Event) -> None:
        """Оповещаем наблюдателей"""
        for observer in self.__observers__:
            await observer['observer'].handle_event(event)

    def __get_first_observer_instance_index__(self, observer: Observer) -> int:
        """Поиск первого попавшегося наблюдателя в коллекции по экземпляру класса"""
        observers = list(filter(lambda x: x["observer"] == observer, self.__observers__))
        if observers:
            return self.__observers__.index(observers[0])
        else:
            return -1

    def __get_first_observer_type_index__(self, observer: Observer) -> int:
        """Поиск первого попавшегося наблюдателя в коллекции по типу класса"""
        observers = list(filter(
            lambda x:
            type(x["observer"]) == type(observer) and
            getattr(x["observer"], 'observer_id', None) == getattr(observer, 'observer_id', None), self.__observers__)
        )
        if observers:
            return self.__observers__.index(observers[0])
        else:
            return -1

    @staticmethod
    def get_relative_observer_id(observer: typing.Union[Observer, typing.Callable[[Event], None]]) -> str:
        """
        Возвращает относительный путь (отностиельно папки core/modules/event_engine) к модулю обработчика.
        Если вы наследуетесь от текущего класса (Observable) - знайте, этот метод (get_relative_observer_id)
        НЕЛЬЗЯ переопределять. Он используется как идентификатор для поиска необходимой спецификации в БД.
        """
        # относительный путь к обработчику используется чтобы не "светить" структуру проекта.
        relative_observer_module_path = path.splitext(
            # получаем относительный путь от пакета event_engine к *.py-файлу обработчика
            path.relpath(
                sys.modules[observer.__module__].__file__,  # полный путь к модулю (*.py файлу) обработчика
                path.dirname(__file__)  # полный путь к ПАПКЕ текущего файла, т.е./path/to/core/modules/event_engine
            )
        )[0]  # убираем '.py' расширение файла обработчика

        if callable(observer):
            observer_name = observer.__name__
        else:
            observer_name = observer.__class__.__name__

        return '{}.{}'.format(relative_observer_module_path, observer_name)
