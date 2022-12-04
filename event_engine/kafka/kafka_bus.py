import logging
from typing import Optional

import msgpack
from aiokafka.errors import KafkaError

from event_engine.event import Event
from .base import KafkaConfig
from .kafka_producer import get_producer
from ..base import BaseSerializer


class KafkaBus:
    def __init__(self, kafka_config: KafkaConfig, serializer: Optional[BaseSerializer] = None):
        self.kafka_config = kafka_config
        self.serializer = serializer
        self.logger = logging.getLogger("kafka.bus")

    async def start(self):
        producer = await get_producer(config=self.kafka_config)
        await producer.start()

    async def send(self, event: Event):
        producer = await get_producer(config=self.kafka_config)
        try:
            # set event published
            event.is_published = True
            if self.serializer is not None:
                event_data = self.serializer.serialize(event)
            else:
                event_data = event.dict(by_alias=True)
            await producer.send_and_wait(topic=event.topic, key=event.event_key, value=msgpack.packb(event_data))
        except KafkaError as e:
            event.is_published = False
            self.logger.exception(e)
