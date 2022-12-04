import pytest

from event_engine import EventManager, Observer, Event
from tests.fixtures.event import PaymentEvent, payment_event, PaymentHandler, demo_event, DemoEvent, DemoHandler
from unittest.mock import AsyncMock


def test_ee_register_and_lookup_event(payment_event):

    ee = EventManager()

    ee.register([PaymentEvent], PaymentHandler())

    event = ee.lookup_event(payment_event.dict(by_alias=True))

    assert event.name == payment_event.name


@pytest.mark.asyncio
async def test_raise_event(payment_event):
    ee = EventManager()

    mock_event_handler = AsyncMock(spec=PaymentHandler())
    mock_event_handler.observer_id = "payment"

    mock_demo_handler = AsyncMock(spec=DemoHandler())
    mock_demo_handler.observer_id = "demo"

    ee.register([PaymentEvent], mock_event_handler)
    ee.register([DemoEvent], mock_demo_handler)

    await ee.raise_event(payment_event)

    assert mock_event_handler.handle_event.called
    assert not mock_demo_handler.handle_event.called
