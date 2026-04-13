import asyncio
import uuid

from event_engine import EventManager
from event_engine.kafka import KafkaConfig, KafkaBus
from event_engine.observer import Observer
from examples.proto.events_proto import PaymentProtoEvent
from examples.proto.payment_pb2 import (
    Currency,
    Money,
    PassengerInfo,
    PaymentEventData as PaymentProto,
    PAYMENT_STATUS_SUCCESS,
)


class _NoOpObserver(Observer):
    async def handle_event(self, event):
        pass


async def raise_proto_event():
    kafka_config = KafkaConfig(
        servers=["localhost:9092"],
        subscribe_topics=["demo_topic_1"],
        service_name="example_proto_service_1",
    )

    kafka_bus = KafkaBus(kafka_config=kafka_config)
    await kafka_bus.start()
    em: EventManager = EventManager(bus=kafka_bus)
    em.register(events=[PaymentProtoEvent], handler=_NoOpObserver())

    proto_msg = PaymentProto(
        payment_id=str(uuid.uuid4()),
        status=PAYMENT_STATUS_SUCCESS,
        order_id="ORD-2026-001",
        amount=Money(amount=150000, currency=Currency.CURRENCY_RUB),
        passenger=PassengerInfo(
            first_name="Ivan",
            last_name="Ivanov",
            email="ivan@example.com",
            phone="+79001234567",
        ),
        ticket_numbers=["SU-1234", "SU-1235"],
        metadata={"channel": "web", "promo": "SUMMER25"},
    )

    # data is a proto object — serialized as base64 inside JSON envelope
    await em.raise_event(PaymentProtoEvent(data=proto_msg))
    print("Event sent!")


try:
    asyncio.run(raise_proto_event())
except KeyboardInterrupt:
    print("Interrupted")
