import logging
from typing import Optional

import msgpack
from aiokafka.errors import KafkaError, ProducerClosed

from event_engine.event import Event
from .base import KafkaConfig
from .kafka_producer import get_kafka_producer, _recreate_producer
from ..base import BaseSerializer


class KafkaBus:
    def __init__(self, kafka_config: KafkaConfig, serializer: Optional[BaseSerializer] = None):
        self.kafka_config = kafka_config
        self.serializer = serializer
        self.logger = logging.getLogger("kafka.bus")

    async def start(self):
        producer = await get_kafka_producer(config=self.kafka_config)
        await producer.start()

    async def send(self, event: Event):
        try:
            await self._send(event)
        except KafkaError as e:
            self.logger.exception(e)
            raise

    async def _send(self, event: Event, _try: int = 0):
        producer = await get_kafka_producer(config=self.kafka_config)
        if self.serializer is not None:
            event_data = self.serializer.serialize(event)
        else:
            event_data = event.dict(by_alias=True)
        try:
            await producer.send_and_wait(
                topic=event.topic,
                key=event.event_key,
                value=msgpack.packb(event_data)
            )
            # set event published
            event.is_published = True
        except ProducerClosed as e:
            await _recreate_producer(config=self.kafka_config)
            _try += 1
            self.logger.exception(e)
            return await self._send(event, _try)
