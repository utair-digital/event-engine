from copy import deepcopy
import pytest

from event_engine import EventManager, Observer
from event_engine.kafka import KafkaSubClient
from tests.fixtures.event import (
    PaymentEvent,
    payment_event_raw_data,
)
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_same_event_from_different_topic(payment_event_raw_data):
    """Test that the same event from different topics is handled correctly."""

    ee = EventManager()

    handler_mock = AsyncMock(spec=Observer)
    handler_mock.observer_id = "PaymentHandler"

    ee.register([PaymentEvent], handler_mock, is_type_check=True)
    kafka_sub = KafkaSubClient(event_manager=ee, kafka_config=AsyncMock(), handle_signals=False)

    event_from_topic_payment = deepcopy(payment_event_raw_data)
    event_from_topic_payment["topic"] = "payments_from_kafka"

    event_from_topic_payment_additional = deepcopy(payment_event_raw_data)
    event_from_topic_payment_additional["topic"] = "payments_from_kafka_additional"

    with patch("msgpack.unpackb") as unpack_patch:
        message_mock = AsyncMock()

        # from topic payments_from_kafka
        message_mock.topic = "payments_from_kafka"
        unpack_patch.return_value = event_from_topic_payment
        await kafka_sub.on_message(message=message_mock)

        handler_mock.handle_event.assert_called_with(PaymentEvent(**event_from_topic_payment))

        # different topic, same event
        unpack_patch.return_value = event_from_topic_payment_additional
        message_mock.topic = "payments_from_kafka_additional"
        await kafka_sub.on_message(message=message_mock)

        handler_mock.handle_event.assert_called_with(PaymentEvent(**event_from_topic_payment_additional))
