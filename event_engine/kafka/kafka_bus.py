import logging
from typing import Optional

import msgpack
from aiokafka.errors import KafkaError, ProducerClosed
from opentelemetry import propagate
from opentelemetry import trace

from event_engine.event import Event
from .base import KafkaConfig
from .exceptions import UnableToSendEventToKafka
from .kafka_producer import get_kafka_producer, _recreate_producer
from ..base import BaseSerializer
from ..telemetry import ContextSetter


class KafkaBus:
    SEND_EVENT_MAX_TRIES = 3

    def __init__(self, kafka_config: KafkaConfig, serializer: Optional[BaseSerializer] = None):
        self.kafka_config = kafka_config
        self.serializer = serializer
        self.logger = logging.getLogger("kafka.bus")

    async def start(self):
        producer = await get_kafka_producer(config=self.kafka_config)
        await producer.start()

    async def send(self, event: Event):
        try:
            with trace.get_tracer("kafka-bus").start_as_current_span(
                f"EE {event.name}", kind=trace.SpanKind.PRODUCER
            ) as span:
                propagate.inject(event, context=trace.set_span_in_context(span), setter=ContextSetter())
                await self._send(event)
        except KafkaError as e:
            self.logger.exception(e)
            raise

    async def _send(self, event: Event, _try: int = 0):
        if _try == self.SEND_EVENT_MAX_TRIES:
            raise UnableToSendEventToKafka()
        producer = await get_kafka_producer(config=self.kafka_config)
        event.is_published = True
        if self.serializer is not None:
            event_data = self.serializer.serialize(event)
        else:
            event_data = event.model_dump(mode="json", by_alias=True)
        try:
            await producer.send_and_wait(topic=event.topic, key=event.event_key, value=msgpack.packb(event_data))
        except ProducerClosed as e:
            event.is_published = False
            await _recreate_producer(config=self.kafka_config)
            _try += 1
            self.logger.exception(e)
            return await self._send(event, _try)
        except KafkaError:
            event.is_published = False
            raise
