from typing import Union
from event_engine_async import get_event_manager
from event_engine_async.event import Event
from event_engine_async.observer import Observer
from examples.kafka_settings import KAFKA_CONFIG


class DemoEvent(Event):
    topic = "demo_topic"
    is_internal = False
    is_publishable = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __get_event_key__(self) -> Union[int, None]:
        return None


class DemoObserver(Observer):
    """
    Обработчик события сохранения заказа
    """
    observer_id = '__DemoSubscriber__'

    async def handle_event(self, event: DemoEvent):
        print(f"HANDLED {event.serialize()}")


async def register_order_saved_observer():
    manager = get_event_manager(KAFKA_CONFIG)
    manager.register(
        DemoObserver.observer_id,
        [DemoEvent],
        DemoObserver(),
        is_type_check=True
    )
