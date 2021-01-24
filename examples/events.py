from event_engine.event import Event
from event_engine.observer import Observer


class DemoEvent(Event):
    topic = "demo_topic"


class DemoEvent1(DemoEvent):
    is_internal = True
    is_publishable = False


class DemoEvent2(DemoEvent):
    is_internal = True
    is_publishable = True


class DemoObserver(Observer):
    """
    Обработчик события
    """
    async def handle_event(self, event: DemoEvent):
        print(f"HANDLED {event.serialize()}")
