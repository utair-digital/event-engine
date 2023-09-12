import logging
from typing import Optional

import msgpack
from aiokafka import AIOKafkaConsumer, ConsumerRecord, ConsumerStoppedError

from event_engine.event import Event
from event_engine.event_manager import EventManager
from event_engine.exceptions import BaseEventEngineError
from event_engine.shutdownable import ShutDownable
from .base import KafkaConfig
from .exceptions import CantUnpackDataFromBus
from ..base import BaseDeserializer


class KafkaSubClient(ShutDownable):

    _consumer: AIOKafkaConsumer

    def __init__(
        self,
        event_manager: EventManager,
        kafka_config: KafkaConfig,
        handle_signals: bool = False,
        deserializer: Optional[BaseDeserializer] = None,
        logger: logging.Logger = logging.getLogger("event_engine.bus.kafka.subscriber"),
    ):
        """

        Args:
            event_manager:
            kafka_config:
            handle_signals:
            deserializer:
            logger:
        """

        self.ee = event_manager
        self.kafka_config = kafka_config
        self.logger = logger
        self.deserializer = deserializer

        if handle_signals:
            super().__init__(logger=logger)

    async def _on_shutdown(self):
        await self.stop()

    async def listen(self):
        self.logger.info("Starting kafka listener...")
        self.logger.info("Registering event handlers...")

        self._consumer = AIOKafkaConsumer(
            bootstrap_servers=self.kafka_config.servers,
            group_id=self.kafka_config.service_name,
            metadata_max_age_ms=self.kafka_config.metadata_max_age_ms,
            ssl_context=self.kafka_config.ssl_context,
            security_protocol=self.kafka_config.security_protocol.value,
            sasl_plain_password=self.kafka_config.auth.password if self.kafka_config.should_auth else None,
            sasl_plain_username=self.kafka_config.auth.username if self.kafka_config.should_auth else None,
            sasl_mechanism=self.kafka_config.sasl_mechanism.value
        )
        # Get cluster layout and topic/partition allocation
        self.logger.info("Getting cluster layout and topic/partition allocation..")
        await self._consumer.start()

        if self.kafka_config.subscribe_pattern:
            self._consumer.subscribe(pattern=self.kafka_config.subscribe_pattern)

        if self.kafka_config.subscribe_topics:
            self._consumer.subscribe(topics=self.kafka_config.subscribe_topics)

        self.logger.info("Waiting for new messages..")

        try:
            async for msg in self._consumer:
                try:
                    self.logger.info("Got a new message")
                    await self.on_message(msg)
                except BaseEventEngineError:
                    pass
        except ConsumerStoppedError:
            self.logger.info("Kafka consumer stopped!")

    async def on_message(self, message: ConsumerRecord):
        try:
            message.value = msgpack.unpackb(message.value)
        except Exception as e:
            self.logger.exception(f"Unable to deserialize event byte data: {e}")
            raise CantUnpackDataFromBus()

        event_data = message.value
        if self.deserializer is not None:
            event_data = self.deserializer.deserialize(event_data)
        event: Event = self.ee.lookup_event(event_data)

        try:
            assert event.topic == message.topic, "Unable to ensure topic is same as deserialized event topic"
        except AssertionError:
            self.logger.exception(f"Incorrect topic assigned: expected [{event.topic}]  actual [{message.topic}]")
            return

        try:
            event.is_published = True
            return await self.ee.raise_event(event)
        except (ValueError, TypeError, BaseEventEngineError) as e:
            self.logger.exception(f"Unable to raise event: {e}")
            return

    async def stop(self):
        self.logger.info("Kafka consumer graceful shutdown...")
        await self._consumer.stop()
