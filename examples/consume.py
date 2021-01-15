import asyncio
from event_engine_async.kafka_consumer import KafkaSubClient
from event_engine_async.kafka_config import KafkaConfig
from event_engine_async import get_event_manager

from examples.events import register_order_saved_observer

KAFKA_CONFIG = {
    'servers': ['localhost:29092'],
    'subscribe_topics': ['demo_topic'],
    'service_name': "example_service"
}


def run_kafka_consumer():
    client = KafkaSubClient(
        event_manager=get_event_manager(),
        event_register_function=register_order_saved_observer,
        kafka_config=KafkaConfig(**KAFKA_CONFIG)
    )
    asyncio.run(client.listen())


run_kafka_consumer()
