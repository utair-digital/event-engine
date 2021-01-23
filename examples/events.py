from typing import Union
from event_engine import get_event_manager
from event_engine.event import Event
from event_engine.observer import Observer
from examples.kafka_settings import KAFKA_CONFIG


class DemoEvent(Event):
    topic = "demo_topic"
    is_internal = True
    is_publishable = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __get_event_key__(self) -> Union[int, None]:
        return None


class DemoObserver(Observer):
    """
    Обработчик события
    """
    observer_id = '__DemoSubscriber__'

    async def handle_event(self, event: DemoEvent):
        print(f"HANDLED {event.serialize()}")


def register_order_saved_observer():
    manager = get_event_manager(KAFKA_CONFIG)
    manager.register(
        [DemoEvent],
        DemoObserver(),
        is_type_check=True
    )
