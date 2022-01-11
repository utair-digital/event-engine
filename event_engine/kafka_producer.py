from typing import Optional
from aiokafka import AIOKafkaProducer
from .base import KafkaConfig
from .log_config import setup_logger

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
    setup_logger(config)
    _PRODUCER = AIOKafkaProducer(
        bootstrap_servers=config.servers,
        metadata_max_age_ms=config.metadata_max_age_ms
    )
    return await get_producer(config)


async def stop_kafka_producer():
    """
    Остановка продюссера
    call on shutdown
    """
    global _PRODUCER
    await _PRODUCER.stop()
