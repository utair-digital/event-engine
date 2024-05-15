from event_engine.event import Event
from event_engine.observer import Observer
from pydantic import BaseModel


class PaymentEventData(BaseModel):
    payment_id: str
    status: str


class PaymentEvent(Event[PaymentEventData]):
    topic: str = "demo_topic"


class PaymentEvent1(PaymentEvent):
    name: str = "PaymentEvent1"
    is_internal: bool = True
    is_publishable: bool = False


class PaymentEvent2(PaymentEvent):
    name: str = "PaymentEvent2"
    is_internal: bool = True
    is_publishable: bool = True


class PaymentObserver(Observer):
    async def handle_event(self, event: PaymentEvent):
        print(f"HANDLED {event.model_dump()}")
