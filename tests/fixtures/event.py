import pytest
from pydantic import BaseModel
from event_engine.event import Event
from event_engine.observer import Observer


class PaymentEventData(BaseModel):
    payment_id: str
    status: str


class PaymentEvent(Event[PaymentEventData]):
    topic: str = "payments"
    is_internal: bool = True

    name: str = "payment_event"


class PaymentHandler(Observer):
    async def handle_event(self, event: PaymentEvent):
        print(f"HANDLED {event.dict()}")


class DemoEventData(BaseModel):
    status: str


class DemoEvent(Event[PaymentEventData]):
    topic: str = "demo"
    is_internal: bool = True

    name: str = "demo_event"


class DemoHandler(Observer):
    async def handle_event(self, event: PaymentEvent):
        print(f"HANDLED {event.dict()}")


@pytest.fixture
def payment_event() -> PaymentEvent:
    return PaymentEvent(
        **{
            "name": "payment_event",
            "topic": "payments",
            "data": {"payment_id": "we5r24t-okj", "status": "ok"},
            "meta": {"version": "2.0", "trace": None},
            "event_key": "1",
            "is_published": False,
            "is_internal": True,
            "is_publishable": False,
        }
    )


@pytest.fixture
def demo_event() -> DemoEvent:
    return DemoEvent(
        **{
            "name": "payment_event",
            "topic": "payments",
            "data": {"status": "ok"},
            "meta": {"version": "2.0", "trace": None},
            "event_key": "1",
            "is_published": False,
            "is_internal": True,
            "is_publishable": False,
        }
    )


@pytest.fixture
def payment_event_raw_data() -> dict:
    return {
        "name": "payment_event",
        "topic": "payments",
        "data": {"status": "ok", "payment_id": "we5r24t-okj"},
        "meta": {"version": "2.0", "trace": None},
        "event_key": "1",
        "is_published": False,
        "is_internal": True,
        "is_publishable": False,
    }
