import asyncio
import logging

from event_engine import run_kafka_consumer, get_event_manager
from event_engine import KafkaConfig, EventManager

from examples.events import DemoObserver, DemoEvent1, DemoEvent2

KAFKA_CONFIG = KafkaConfig(**{
    'servers': ['localhost:29092'],
    'subscribe_topics': ['demo_topic'],
    'service_name': "example_service"
})


async def consume():
    log = logging.getLogger("KafkaSubClient")
    log.setLevel("INFO")
    log.addHandler(logging.StreamHandler())

    em: EventManager = get_event_manager(KAFKA_CONFIG)
    em.register(
        [DemoEvent1, DemoEvent2],
        DemoObserver(),
        is_type_check=True
    )

    await run_kafka_consumer(KAFKA_CONFIG)

try:
    asyncio.run(consume())
except KeyboardInterrupt:
    pass
