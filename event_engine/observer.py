from .base import BaseObserver
from .event import Event


class Observer(BaseObserver):
    """
    Класс наблюдателя / Обработчика события.
    """

    observer_id: str = None

    async def handle_event(self, event: Event) -> None:
        """Обработать событие"""
        raise NotImplementedError
