from event_engine.event import Event
from event_engine.observer import Observer
from pydantic import BaseModel


class PaymentEventData(BaseModel):
    payment_id: str
    status: str


class PaymentEvent(Event[PaymentEventData]):
    topic = "demo_topic"


class PaymentEvent1(PaymentEvent):
    name = "PaymentEvent1"
    is_internal = True
    is_publishable = False


class PaymentEvent2(PaymentEvent):
    name = "PaymentEvent2"
    is_internal = True
    is_publishable = True


class PaymentObserver(Observer):
    async def handle_event(self, event: PaymentEvent):
        print(f"HANDLED {event.dict()}")
