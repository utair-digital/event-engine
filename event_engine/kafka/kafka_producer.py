from typing import Optional
from aiokafka import AIOKafkaProducer
from .base import KafkaConfig

_PRODUCER: Optional[AIOKafkaProducer] = None


async def start_kafka_producer(config: KafkaConfig):
    """
    Получение продюссера
    Нужно вызвать при старте приложения
    """
    prod = await get_producer(config)
    await prod.start()


async def get_producer(config: KafkaConfig) -> AIOKafkaProducer:
    global _PRODUCER
    if _PRODUCER:
        return _PRODUCER
    _PRODUCER = AIOKafkaProducer(bootstrap_servers=config.servers, metadata_max_age_ms=config.metadata_max_age_ms)
    return await get_producer(config)


async def stop_kafka_producer():
    """
    Остановка продюссера
    call on shutdown
    """
    global _PRODUCER
    await _PRODUCER.stop()
