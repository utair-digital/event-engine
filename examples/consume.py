import logging
from event_engine_async import run_kafka_consumer

from examples.events import register_order_saved_observer
from examples.kafka_settings import KAFKA_CONFIG


log = logging.getLogger("KafkaSubClient")
log.setLevel("INFO")
log.addHandler(logging.StreamHandler())

run_kafka_consumer(
    KAFKA_CONFIG,
    register_order_saved_observer,
    log
)
