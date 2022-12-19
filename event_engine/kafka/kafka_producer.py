from typing import Optional
from aiokafka import AIOKafkaProducer
from .base import KafkaConfig

_PRODUCER: Optional[AIOKafkaProducer] = None


async def get_producer(config: KafkaConfig) -> AIOKafkaProducer:
    global _PRODUCER
    if _PRODUCER:
        return _PRODUCER
    _PRODUCER = AIOKafkaProducer(bootstrap_servers=config.servers, metadata_max_age_ms=config.metadata_max_age_ms)
    return await get_producer(config)


async def stop_kafka_producer():
    """
    stop producer
    call on shutdown
    """
    global _PRODUCER
    await _PRODUCER.stop()
