from typing import Optional
from aiokafka import AIOKafkaProducer
from .base import KafkaConfig
from .exceptions import (
    CantRecreateNonExistingProducer,
    CantCloseNonExistingProducer
)

_PRODUCER: Optional[AIOKafkaProducer] = None


async def get_kafka_producer(config: KafkaConfig) -> AIOKafkaProducer:
    global _PRODUCER
    if _PRODUCER:
        return _PRODUCER
    _PRODUCER = AIOKafkaProducer(
        bootstrap_servers=config.servers,
        metadata_max_age_ms=config.metadata_max_age_ms,
        security_protocol=config.security_protocol.value,
        ssl_context=config.ssl_context,
        sasl_plain_username=config.auth.username if config.should_auth else None,
        sasl_plain_password=config.auth.password if config.should_auth else None,
        sasl_mechanism=config.sasl_mechanism.value
    )
    return await get_kafka_producer(config)


async def stop_kafka_producer():
    """
    stop producer
    call on shutdown
    """
    global _PRODUCER
    if not _PRODUCER:
        raise CantCloseNonExistingProducer()
    await _PRODUCER.stop()


async def _recreate_producer(config: KafkaConfig):
    """
    Recreate producer in case of aiokafka.errors.ProducerClosed during send
    """
    global _PRODUCER
    if not _PRODUCER:
        raise CantRecreateNonExistingProducer()
    await stop_kafka_producer()  # will stop if not _closed
    _PRODUCER = None
    _PRODUCER = await get_kafka_producer(config)
    await _PRODUCER.start()
