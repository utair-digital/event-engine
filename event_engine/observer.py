from .base import BaseObserver
from .event import Event


class Observer(BaseObserver):
    """
    Класс наблюдателя / Обработчика события.
    """

    observer_id: str = None

    def __init__(self):
        self.observer_id = self.observer_id if self.observer_id else self.__class__.__name__

    async def handle_event(self, event: Event) -> None:
        """Обработать событие"""
        raise NotImplementedError
