from .base import BaseObserver
from .event import Event


class Observer(BaseObserver):
    """Event handler"""

    observer_id: str = ""

    def __init__(self):
        self.observer_id = self.observer_id if self.observer_id else self.__class__.__name__

    async def handle_event(self, event: Event) -> None:
        raise NotImplementedError
