from typing import Optional
from aiokafka import AIOKafkaProducer
from .base import KafkaConfig

_PRODUCER: Optional[AIOKafkaProducer] = None


async def get_producer(config: KafkaConfig) -> AIOKafkaProducer:
    global _PRODUCER
    if _PRODUCER:
        return _PRODUCER
    _PRODUCER = AIOKafkaProducer(
        bootstrap_servers=config.servers,
        metadata_max_age_ms=config.metadata_max_age_ms,
        security_protocol=config.security_protocol,
        ssl_context=config.ssl_context,
        sasl_plain_username=config.auth.username if config.should_auth else None,
        sasl_plain_password=config.auth.password if config.should_auth else None,
        sasl_mechanism=config.sasl_mechanism
    )
    return await get_producer(config)


async def stop_kafka_producer():
    """
    stop producer
    call on shutdown
    """
    global _PRODUCER
    await _PRODUCER.stop()
