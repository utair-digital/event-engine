import types
from typing import List, Type, Dict, Callable, Union
from aiokafka.errors import KafkaError

from .base import BaseEventManager, KafkaConfig
from .event import Event
from .observable import Observable
from .observer import Observer
from .exceptions import (
    InvalidObserverIDError,
    EventNotRegisteredError,
    InvalidEventType,
    InvalidObserverType,
)
from .kafka_producer import start_kafka_producer


class EventManager(BaseEventManager):
    """
    Класс менеджера событий
    Отвечает за байндинг событий и обработчиков
    """

    def __init__(self, kafka_config: KafkaConfig):
        super().__init__(kafka_config)

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
            events: List[Type[Event]],
            handler: Observer,
            is_type_check: bool = False,
    ) -> None:
        """
        Байндинг события и его обработчика
        :param events: События
        :param handler: Обработчик
        :param is_type_check: Флаг проверки, что два экземпляра одного класса не обрабатывают событие
        :return: None
        """
        observer_id = handler.observer_id

        if not observer_id or not isinstance(observer_id, str):
            # observer_id должен быть указан при регистрации
            raise InvalidObserverIDError('Некорректный observer_id: {}'.format(observer_id))

        # если handler не потомок BaseObserver (а просто def функция) - создаем фейколвый объект налюдателя
        if not isinstance(handler, Observer) and callable(handler):
            handler = self.FakeObserver(handler)
            handler.observer_id = observer_id

        for event in events:
            if not issubclass(event, Event):
                err = InvalidEventType("Invalid event type")
                self.logger.exception(err)
                raise err
            if not (isinstance(handler, Observer) or callable(handler)):
                err = InvalidObserverType("Invalid handler type")
                self.logger.exception(err)
                raise err
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
        await self.__raise_event__(event=event, celery=False, silent=silent)

    async def raise_event_celery(
            self,
            event: Event,
            silent: bool = True,
            celery_task: Callable = None
    ) -> None:
        """
        Вызов обработчиков подписанных на событие (обработка событий запустится в celery с помощью celery_task)
        :param event: Событие
        :param celery_task: Celery task функция, в которой запускается обработка события
        :param silent: Игнорирование незарегистрированного события. Если значение False и событие незарегистрированно -
            будет брошено исключение, Если значение True отсутсвие незарегистрированного события будет проигнорированно
        """
        await self.__raise_event__(event=event, celery=True, silent=silent, celery_task=celery_task)

    async def __raise_event__(
            self,
            event: Event,
            celery: bool = False,
            silent: bool = True,
            celery_task: Callable = None
    ) -> None:
        """
         Вызов обработчиков подписанных на событие
        :param event: Событие
        :param celery: Флаг запуска обработки событий в celery task
        :param celery_task: Celery task функция, в которой запускается обработка события
        :param silent: Игнорирование незарегистрированного события. Если значение False и событие незарегистрированно -
            будет брошено исключение, Если значение True отсутсвие незарегистрированного события будет проигнорированно
        """
        event_type = type(event)

        async def __raise__():
            if all([celery, celery_task]):
                # отправка события в селери таску
                await self.__binds__[event_type].notify_observers_async(event, celery_task)
            else:
                # вызов обработчика в текущем потоке
                await self.__binds__[event_type].notify_observers(event)

        if event_type not in self.__binds__.keys() and not silent:
            err = EventNotRegisteredError("Raised event is not registered")
            self.logger.exception(err)
            raise err

        if event_type in self.__binds__.keys():
            if event.is_published:
                # Опубликованное событие прилетело из кафки, в этом случае его нужно зарейзить внутри приложения
                return await __raise__()

            if all([event.is_publishable, not event.is_published]):
                try:
                    await self.__send_to_kafka_bus(event)
                except Exception as e:
                    self.logger.exception(e)
            if not event.is_internal:
                # обработчик не нуждается в вызове внутри приложения
                return
            await __raise__()

    async def __send_to_kafka_bus(self, event: Event) -> None:
        producer = await start_kafka_producer(config=self.kafka_config)
        try:
            # Ставим флаг, что событие было опубликовано в кафке,
            # таким образом оно не будет опубликовано на клиете еще раз
            event.is_published = True
            await producer.send_and_wait(**event.kafka_message.build())
        except KafkaError as e:
            event.is_published = False
            self.logger.exception(e)

    def un_register(self, event: Event, handler: Union[Observer, Callable]) -> None:
        """Удаление байндинга обработчика и события"""
        raise NotImplementedError  # TODO: добавить имплементацию

    def deserialize_event(self, event: Dict) -> Event:
        """Среди зарегестрированных событий ищет тип serialized_event-а
        и возвращает его десериализованный экземпляр (объект)"""
        for event_instance in list(self.__binds__.keys()):
            if str(event_instance.__name__) == event['type']:
                return event_instance.deserialize(event)
        err = EventNotRegisteredError('Event "{}" is not registered'.format(event['type']))
        self.logger.exception(err)
        raise err
