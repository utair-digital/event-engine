import asyncio

from event_engine import EventManager
from event_engine.kafka import KafkaConfig, KafkaBus
from event_engine.kafka.kafka_consumer import KafkaSubClient
from event_engine.observer import Observer
from examples.proto.events_proto import PaymentProtoEvent
from examples.proto.payment_pb2 import PaymentEventData as PaymentProto


class PaymentProtoObserver(Observer):
    async def handle_event(self, event: PaymentProtoEvent):
        # event.data is already a PaymentProto instance — no manual parsing needed
        proto: PaymentProto = event.data
        print(f"payment_id={proto.payment_id} status={proto.status}")


async def consume():
    kafka_config = KafkaConfig(
        servers=["localhost:9092"],
        subscribe_topics=["demo_topic_1"],
        service_name="example_proto_service",
    )

    kafka_bus = KafkaBus(kafka_config=kafka_config)
    em: EventManager = EventManager(bus=kafka_bus)
    em.register(
        events=[PaymentProtoEvent],
        handler=PaymentProtoObserver(),
    )

    sub = KafkaSubClient(
        event_manager=em,
        kafka_config=kafka_config,
        handle_signals=True,
    )
    await sub.listen()


try:
    asyncio.run(consume())
except KeyboardInterrupt:
    print("Interrupted")
