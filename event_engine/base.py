import msgpack
import logging
from abc import ABCMeta
from abc import abstractmethod
from typing import Collection, Callable, Dict, Type, List, Union


class KafkaConfig:
    servers = []
    subscribe_topics = []
    service_name = None

    def __init__(self, servers: list, subscribe_topics: list, service_name: str):
        self.servers = servers
        self.subscribe_topics = subscribe_topics
        self.service_name = service_name


class KafkaMessage:
    """
    DTO для producer.send(**KafkaMessage.build()) / send_and_wait
    """
    def __init__(
            self,
            topic: str,
            key: str,
            data: bytes
    ):
        self.topic = topic
        self.key = key
        self.data = data

    def build(self):
        return dict(
            topic=self.topic,
            key=self.key,
            value=self.data
        )


class BaseEvent:
    """
    Базовый класс события.
    Отвечает за передачу данных обработчику события
    """
    name: str = 'Anonymous event'
    code: int = 0
    data: object = None

    is_internal: bool = True        # Флаг, обозначающий, что сообщение должно быть отправлено внутри приложения

    is_published: bool = False      # Флаг, обозначающий, что сообщение было отправлено через шину
    is_publishable: bool = False    # Флаг, обозначающий, что сообщение должно быть отправлено в кафку

    event_key: str = None           # Ключ события требуется для обработки события по порядку,
    # события с одинаковым ключем попадут в одну partition в кафке и будут обработаны последовательно

    topic: str = None               # Топик события, на которое должен быть подписан клиент, чтобы его получить

    def serialize(self) -> Dict:
        raise NotImplementedError()

    def deserialize(self, event: Dict) -> "BaseEvent":
        raise NotImplementedError()

    def __get_event_key__(self) -> Union[str, None]:
        """
        Функция генерации ключа события
        По дефолту ключа нет, кафка будет посылать события по разным partition round-robin
        """
        return None

    @property
    def kafka_message(self) -> KafkaMessage:
        """
        Собирает сообщения для kafka.send()
        """
        return KafkaMessage(
            topic=self.topic,
            key=self.event_key,
            data=msgpack.packb(self.serialize())
        )


class BaseObserver(metaclass=ABCMeta):
    """
    Абстрактный класс наблюдателя
    """

    @abstractmethod
    async def handle_event(self, event: BaseEvent) -> None:
        """Обработать событие"""
        raise NotImplementedError


class BaseObservable(metaclass=ABCMeta):
    """
    Абстрактный класс наблюдаемого объекта
    """

    __observers__: Collection

    @abstractmethod
    def add_observer(
            self,
            observer: BaseObserver
    ) -> None:
        """
        Добавить наблюдателя
        :param observer: Наблюдатель
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def remove_observer(self, observer: BaseObserver) -> None:
        """Удалить наблюдателя"""
        raise NotImplementedError

    @abstractmethod
    async def notify_observers(self, event: BaseEvent) -> None:
        """Сообщить наблюдателю о наступлении события"""
        raise NotImplementedError

    @abstractmethod
    async def notify_observers_async(self, event: BaseEvent, async_task: Callable) -> None:
        """Сообщить наблюдателю о наступлении события (обработка событий запустится в celery)"""
        raise NotImplementedError

    @abstractmethod
    def __notify__(self, event: BaseEvent) -> None:
        """Оповещаем наблюдателей"""
        raise NotImplementedError


class BaseEventManager:
    """
    Абстрактный класс менеджера событий
    Отвечает за байндинг событий и обработчиков
    """

    __binds__: Union[Dict, Collection]

    def __init__(
            self,
            kafka_config: KafkaConfig,
            logger: logging.Logger = logging.getLogger('event_manager')
    ):
        self.kafka_config = kafka_config
        self.__binds__ = dict()
        self.logger = logger

    @abstractmethod
    def register(
            self,
            events: List[Type[BaseEvent]],
            handler: Union[BaseObserver, Callable[[BaseEvent], None]],
            is_type_check: bool = False,
    ) -> None:
        """
        Байндинг события и его обработчика
        :param events: События
        :param handler: Обработчик
        :param is_type_check: Флаг проверки, что два экземпляра одного класса не обрабатывают событие
        :return:None
        """
        raise NotImplementedError

    @abstractmethod
    async def raise_event(self, event: BaseEvent, silent: bool = True) -> None:
        """
        Вызов обработчиков подписанных на событие
        :param event: Событие
        :param silent: Игнорирование незарегистрированного события. Если значение False и событие незарегистрированно -
            будет брошено исключение, Если значение True отсутсвие незарегистрированного события будет проигнорированно
        """
        raise NotImplementedError

    @abstractmethod
    async def raise_event_celery(self, event: BaseEvent, silent: bool = True, celery_task: Callable = None) -> None:
        """
        Вызов обработчиков подписанных на событие (обработка событий запустится в celery с помощью celery_task)
        :param event: Событие
        :param celery_task: Асинхронная функция, в которой запускается обработка события
        :param silent: Игнорирование незарегистрированного события. Если значение False и событие незарегистрированно -
            будет брошено исключение, Если значение True отсутсвие незарегистрированного события будет проигнорированно
        """
        raise NotImplementedError

    @abstractmethod
    async def __raise_event__(self, event: BaseEvent, is_async: bool = False, silent: bool = True) -> None:
        """
         Вызов обработчиков подписанных на событие
        :param event: Событие
        :param is_async: Флаг запуска обработки событий в асинхронном режиме
        :param silent: Игнорирование незарегистрированного события. Если значение False и событие незарегистрированно -
            будет брошено исключение, Если значение True отсутсвие незарегистрированного события будет проигнорированно
        """
        raise NotImplementedError

    @abstractmethod
    def un_register(
            self,
            event: BaseEvent,
            handler: Union[BaseObserver, Callable[[BaseEvent], None]]
    ) -> None:
        """Удаление байндинга обработчика и события"""
        raise NotImplementedError

    @abstractmethod
    def __bind__(
            self,
            event: Type[BaseEvent],
            handler: Union[BaseObserver, Callable[[BaseEvent], None]],
            is_type_check: bool = False
    ) -> None:
        """
        Байндинг события и его обработчика
        :param event: Событие
        :param handler: Обработчик
        :param is_type_check: Флаг проверки, что два экземпляра одного класса не обрабатывают событие
        :return: None
        """
        raise NotImplementedError
