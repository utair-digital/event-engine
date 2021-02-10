from typing import Optional
from aiokafka import AIOKafkaProducer
from .base import KafkaConfig
from .log_config import setup_logger

_PRODUCER: Optional[AIOKafkaProducer] = None


async def start_kafka_producer(config: KafkaConfig) -> AIOKafkaProducer:
    """
    Получение продюссера
    Нужно вызвать при старте приложения
    """
    global _PRODUCER
    if not _PRODUCER:
        setup_logger(config)
        _PRODUCER = AIOKafkaProducer(bootstrap_servers=config.servers)
        await _PRODUCER.start()
    return _PRODUCER


async def stop_kafka_producer():
    """
    Остановка продюссера
    call on shutdown
    """
    global _PRODUCER
    await _PRODUCER.stop()
