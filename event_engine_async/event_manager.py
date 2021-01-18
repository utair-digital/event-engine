import logging

import types
from typing import List, Type, Dict, Callable, Union

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

from .base import BaseEventManager
from .event import Event
from .observable import Observable
from .observer import Observer
from .kafka_config import KafkaConfig
from .exceptions import (
    InvalidObserverIDError,
    EventNotRegisteredError,
    InvalidEventType,
    InvalidObserverType,
)

logger = logging.getLogger('event_manager')


class EventManager(BaseEventManager):
    """
    Класс менеджера событий
    Отвечает за байндинг событий и обработчиков
    """

    __binds__ = dict()

    def __init__(
            self,
            kafka_config: KafkaConfig
    ):
        self.kafka_config = kafka_config
        self.__binds__ = dict()

    class FakeObserver(Observer):
        """
        Ложный класс наблюдателя
        Для того чтобы единым интерфейсом использовать обработчики событий являющиеся методом класса и отдельные функии,
        для последних создается мок объект
        """

        def __init__(self, handle_event: Callable[[Event], None]):
            super().__init__()
            self.handle_event = types.MethodType(handle_event, self)

        async def handle_event(self, event: Event) -> None:
            """
            Будет переопределен динамически из handle_event параметра
            """
            pass

    def register(
            self,
            observer_id: str,
            events: List[Type[Event]],
            handler: Union[Observer, Callable[[Event], None]],
            is_type_check: bool = False,
    ) -> None:
        """
        Байндинг события и его обработчика
        :param observer_id: Идентификатор обработчика. Используется для поиска спецификации для этого обработчика. Если
            observer_id не передан - будет использоваться идентификация на релятивные путях. Данный параметр будет
            обрабатываться только если для переданного handler-a справедливо callable(handler) == True, т.е.
            handler - обычная def функция. Если handler экземпляр класса Observer, в качестве observer_id будет
            использоваться handler.observer_id
        :param events: События
        :param handler: Обработчик
        :param is_type_check: Флаг проверки, что два экземпляра одного класса не обрабатывают событие
        :return: None
        """

        if not observer_id or not isinstance(observer_id, str):
            # observer_id должен быть указан при регистрации
            raise InvalidObserverIDError('Некорректный observer_id: {}'.format(observer_id))

        # если handler не потомок BaseObserver (а просто def функция) - создаем фейколвый объект налюдателя
        if not isinstance(handler, Observer) and callable(handler):
            handler = self.FakeObserver(handler)
            handler.observer_id = observer_id

        for event in events:
            if not issubclass(event, Event):
                raise InvalidEventType("Invalid event type")
            if not (isinstance(handler, Observer) or callable(handler)):
                raise InvalidObserverType("Invalid handler type")
            self.__bind__(event, handler, is_type_check)

    def __bind__(
            self,
            event: Type[Event],
            handler: Union[Observer, Callable[[Event], None]],
            is_type_check: bool = False,
    ) -> None:
        """
        Байндинг события и его обработчика
        :param event: Событие
        :param handler: Обработчик
        :param is_type_check: Флаг проверки, что два экземпляра одного класса не обрабатывают событие
        :return: None
        """
        if event not in self.__binds__.keys():
            self.__binds__[event] = Observable(is_type_check)
        self.__binds__[event].add_observer(handler)

    async def raise_event(self, event: Event, silent: bool = True) -> None:
        """
        Вызов обработчиков подписанных на событие
        :param event: Событие
        :param silent: Игнорирование незарегистрированного события. Если значение False и событие незарегистрированно -
            будет брошено исключение, Если значение True отсутсвие незарегистрированного события будет проигнорированно
        :return:
        """
        await self.__raise_event__(event=event, is_async=False, silent=silent)

    async def raise_event_async(
            self,
            event: Event,
            silent: bool = True,
            async_task: Callable = None
    ) -> None:
        """
        Вызов обработчиков подписанных на событие (обработка событий запустится в background)
        :param event: Событие
        :param async_task: Асинхронная функция, в которой запускается обработка события
        :param silent: Игнорирование незарегистрированного события. Если значение False и событие незарегистрированно -
            будет брошено исключение, Если значение True отсутсвие незарегистрированного события будет проигнорированно
        """
        await self.__raise_event__(event=event, is_async=True, silent=silent, async_task=async_task)

    async def __raise_event__(
            self,
            event: Event,
            is_async: bool = False,
            silent: bool = True,
            async_task: Callable = None
    ) -> None:
        """
         Вызов обработчиков подписанных на событие
        :param event: Событие
        :param is_async: Флаг запуска обработки событий в асинхронном режиме
        :param async_task: Асинхронная функция, в которой запускается обработка события
        :param silent: Игнорирование незарегистрированного события. Если значение False и событие незарегистрированно -
            будет брошено исключение, Если значение True отсутсвие незарегистрированного события будет проигнорированно
        """
        event_type = type(event)

        async def __raise__():
            if all([is_async, async_task]):
                # отправка события в селери таску
                self.__binds__[event_type].notify_observers_async(event, async_task)
            else:
                # вызов обработчика в текущем потоке
                await self.__binds__[event_type].notify_observers(event)

        if event_type not in self.__binds__.keys() and not silent:
            raise EventNotRegisteredError("Raised event is not registered")

        if event_type in self.__binds__.keys():
            if event.is_published:
                # Опубликованное событие прилетело из кафки, в этом случае его нужно зарейзить внутри приложения
                return await __raise__()

            if all([event.is_publishable, not event.is_published]):
                await self.__send_to_kafka_bus(event)

            if not event.is_internal:
                # обработчик не нуждается в вызове внутри приложения
                return
            await __raise__()

    async def __send_to_kafka_bus(self, event: Event) -> None:
        # TODO не создавать продюссера каждый раз?
        # продюссер должен быть создан с эвент лупе
        producer = AIOKafkaProducer(bootstrap_servers=self.kafka_config.servers)
        await producer.start()
        try:
            # Ставим флаг, что событие было опубликовано в кафке, таким образом оно не будет опубликовано
            # на клиете еще раз
            event.is_published = True
            await producer.send(**event.build_for_kafka())
        except KafkaError:
            event.is_published = False
        finally:
            await producer.stop()

    def un_register(self, event: Event, handler: Union[Observer, Callable]) -> None:
        """Удаление байндинга обработчика и события"""
        raise NotImplementedError  # TODO: добавить имплементацию

    def event_handler(
            self,
            observer_id: str,
            events: List[Type[Event]],
            is_type_check: bool = True,
    ):
        """
        Декоратор, шорткат для байндинга события и обработчика
        :param observer_id: Идентификатор обработчика. Используется для поиска спецификации для этого обработчика. Если
            observer_id не передан - будет использоваться идентификация на релятивные путях.
        :param events: События
        :param is_type_check: Флаг проверки, что два экземпляра одного класса не обрабатывают событие. Т.к.
            event_handler - это декоратор, is_type_check по умолчанию для него True
        :return: None
        """
        if not observer_id or not isinstance(observer_id, str):
            # observer_id должен быть указан при регистрации
            raise InvalidObserverIDError('Некорректный observer_id: {}'.format(observer_id))

        def handler_wrapper(handler: Callable[[Event], None]):
            if not callable(handler):
                raise InvalidObserverType("Invalid handler type")
            self.register(observer_id, events, handler, is_type_check)
            return handler

        return handler_wrapper

    def deserialize_event(self, event: Dict) -> Event:
        """Среди зарегестрированных событий ищет тип serialized_event-а
        и возвращает его десериализованный экземпляр (объект)"""
        for event_instance in list(self.__binds__.keys()):
            if str(event_instance.__name__) == event['type']:
                return event_instance.deserialize(event)
        raise EventNotRegisteredError('Event "{}" is not registered'.format(event['type']))
