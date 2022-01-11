from event_engine.event import Event
from event_engine.observer import Observer


class DemoEvent(Event):
    """
    is_internal by default
    """
    topic = "demo_topic"


class DemoInternalEvent(DemoEvent):
    is_internal = True
    is_publishable = False


class DemoInternalAndPublishableEvent(DemoEvent):
    is_internal = True
    is_publishable = True


class DemoObserver(Observer):
    """
    Обработчик события
    """
    async def handle_event(self, event: DemoEvent):
        print(f"HANDLED {event.serialize()}")
