from event_engine_async.kafka_config import KafkaConfig
from event_engine_async import run_kafka_consumer

from examples.events import register_order_saved_observer

KAFKA_CONFIG = {
    'servers': ['localhost:29092'],
    'subscribe_topics': ['demo_topic'],
    'service_name': "example_service"
}


run_kafka_consumer(
    KafkaConfig(**{
        'servers': ['localhost:29092'],
        'subscribe_topics': ['demo_topic'],
        'service_name': "example_service"
        }),
    register_order_saved_observer
)
