import msgpack
import logging
from aiokafka import AIOKafkaConsumer, ConsumerRecord, ConsumerStoppedError
from .exceptions import BaseEventEngineError
from .event_manager import EventManager
from .event import Event
from .base import KafkaConfig
from .log_config import setup_logger
from .shutdownable import ShutDownable


class KafkaSubClient(ShutDownable):

    _consumer: AIOKafkaConsumer

    def __init__(
            self,
            event_manager: EventManager,
            kafka_config: KafkaConfig,
            async_raise: bool = False,
            manager_async_task: callable = None,
            handle_signals: bool = False,
            logger: logging.Logger = logging.getLogger('KafkaSubClient'),
    ):
        """
        :param event_manager: Менеджер событий
        :param async_raise: Каким образом рейзить событие, блокировка/celery
        :param manager_async_task: Таска для обработки менеджером событий асинхронно
        """

        self.ee = event_manager
        self.kafka_config = kafka_config
        self.logger = logger
        self.async_raise = async_raise
        self.manager_async_task = manager_async_task

        if self.async_raise and not self.manager_async_task:
            raise ValueError("Celery async task must be provided for async event raising")
        if handle_signals:
            super().__init__(logger=logger)

    async def _on_shutdown(self):
        await self.stop()

    async def listen(self):
        setup_logger(self.kafka_config)
        self.logger.info("Starting kafka listener...")
        self.logger.info("Registering event handlers...")
        self._consumer = AIOKafkaConsumer(
            *self.kafka_config.subscribe_topics,
            bootstrap_servers=self.kafka_config.servers,
            group_id=self.kafka_config.service_name,
            metadata_max_age_ms=self.kafka_config.metadata_max_age_ms
        )
        # Get cluster layout and topic/partition allocation
        self.logger.info("Getting cluster layout and topic/partition allocation..")
        await self._consumer.start()
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
            # msgpack.UnpackException - deprecated, use Exception to catch all errors
            self.logger.exception(f"Unable to deserialize event byte data: {e}")
            return

        try:
            event: Event = self.ee.deserialize_event(message.value)
        except BaseEventEngineError as e:
            self.logger.exception(f"Unable to deserialize event {e}")
            return

        try:
            assert event.topic == message.topic, "Unable to ensure topic is same as deserialized event topic"
        except AssertionError:
            self.logger.exception(f"Incorrect topic assigned: expected [{event.topic}]  actual [{message.topic}]")
            return

        try:
            if self.async_raise and self.manager_async_task:
                self.logger.info("Event raised")
                return await self.ee.raise_event_celery(event, celery_task=self.manager_async_task)
            self.logger.info("Event raised")
            return await self.ee.raise_event(event)
        except (ValueError, TypeError, BaseEventEngineError) as e:
            self.logger.exception(f"Unable to raise event: {e}")
            return

    async def stop(self):
        self.logger.info("Kafka consumer graceful shutdown...")
        await self._consumer.stop()
