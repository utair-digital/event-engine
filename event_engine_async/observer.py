from .base import BaseObserver
from .event import Event


class Observer(BaseObserver):
    """
    Класс наблюдателя / Обработчика события.
    Рекомендуется указать observer_id у экземпляра или переопредлить у типа наследника типа, чтобы не использовалась
    идентификация спецификации обработчика/наблюдателя по относительным путям. При использовании идентификации
    по относительным путям все заведенные спецификации для обработчика не найдутся (если БД не обновлялась)
    в случае его перемещнеия, переименования и т.д. в другой модуль.
    """

    observer_id: str = None                         # использовать для типа

    def __init__(self, observer_id: str = None):    # использовать для экземпляра типа
        self.observer_id = observer_id

    async def handle_event(self, event: Event) -> None:
        """Обработать событие"""
        raise NotImplementedError
