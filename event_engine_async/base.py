from abc import ABCMeta
from abc import abstractmethod
from typing import Collection, Callable, Dict, Type, List, Union


class BaseEvent(metaclass=ABCMeta):
    """
    Абстрактный класс события.
    Отвечает за передачу данных обработчику события, по сути обычный Data Transfer Object (DTO)
    """
    name: str
    code: int
    data: object


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
    def __get_first_observer_instance_index__(self, observer: BaseObserver) -> int:
        """Поиск первого попавшегося наблюдателя в коллекции по экземпляру класса"""
        raise NotImplementedError

    @abstractmethod
    async def notify_observers_async(self, event: BaseEvent, async_task: Callable) -> None:
        """Сообщить наблюдателю о наступлении события (обработка событий запустится в celery)"""
        raise NotImplementedError

    @abstractmethod
    def __notify__(self, event: BaseEvent) -> None:
        """Оповещаем наблюдателей"""
        raise NotImplementedError


class BaseEventManager(metaclass=ABCMeta):
    """
    Абстрактный класс менеджера событий
    Отвечает за байндинг событий и обработчиков
    """

    __binds__: Union[Dict, Collection]

    @abstractmethod
    def register(
            self,
            observer_id: str,
            events: List[Type[BaseEvent]],
            handler: Union[BaseObserver, Callable[[BaseEvent], None]],
            is_type_check: bool = False,
    ) -> None:
        """
        Байндинг события и его обработчика
        :param observer_id: Идентификатор обработчика
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
    async def raise_event_async(self, event: BaseEvent, silent: bool = True, async_task: Callable = None) -> None:
        """
        Вызов обработчиков подписанных на событие (обработка событий запустится в background)
        :param event: Событие
        :param async_task: Асинхронная функция, в которой запускается обработка события
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

    @abstractmethod
    def event_handler(
            self,
            observer_id: str,
            events: List[Type[BaseEvent]],
            is_type_check: bool = False,
    ):
        """
        Декоратор, шорткат для байндинга события и обработчика
        :param events: События
        :param is_type_check: Флаг проверки, что два экземпляра одного класса не обрабатывают событие
        :param observer_id: Индентификатор обработчика
        :return: None
        """
        raise NotImplementedError
