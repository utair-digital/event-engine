from typing import Optional
from aiokafka import AIOKafkaProducer
from .kafka_config import KafkaConfig

_PRODUCER: Optional[AIOKafkaProducer] = None


async def get_kafka_producer(config: KafkaConfig) -> AIOKafkaProducer:
    global _PRODUCER
    if not _PRODUCER:
        _PRODUCER = AIOKafkaProducer(bootstrap_servers=config.servers)
        await _PRODUCER.start()
    return _PRODUCER


async def stop_kafka_producer():
    global _PRODUCER
    await _PRODUCER.stop()
