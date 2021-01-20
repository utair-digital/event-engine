import msgpack
import logging
from typing import Callable
from aiokafka import AIOKafkaConsumer, ConsumerRecord
from .exceptions import BaseEventEngineError
from .event_manager import EventManager
from .event import Event
from .kafka_config import KafkaConfig


class KafkaSubClient:

    def __init__(
            self,
            event_manager: EventManager,
            event_register_function: Callable,
            kafka_config: KafkaConfig,
            async_raise: bool = False,
            manager_async_task: callable = None,
            logger: logging.Logger = logging.getLogger('KafkaSubClient'),
    ):
        """
        :param event_register_function: Функция регистрации обработчик, на которые будет реагировать EventManager
        если обработчик не зарегистрирован или на этапе инициализации и регистрации произошла ошибка - такое событие
        не сможет обработать EventManager
        :param event_manager: Менеджер событий
        :param async_raise: Каким образом рейзить событие, блокировка/celery
        :param manager_async_task: Таска для обработки менеджером событий асинхронно
        """

        self.ee = event_manager
        self.kafka_config = kafka_config
        self.ee_register = event_register_function
        self.logger = logger
        self.async_raise = async_raise
        self.manager_async_task = manager_async_task

        if self.async_raise and not self.manager_async_task:
            raise ValueError("Celery async task must be provided for async event raising")

    async def listen(self):
        self.logger.info("Starting kafka listener...")
        self.ee_register()
        self.logger.info("Registering event handlers...")
        consumer = AIOKafkaConsumer(
            *self.kafka_config.subscribe_topics,
            bootstrap_servers=self.kafka_config.servers,
            group_id=self.kafka_config.service_name
        )
        # Get cluster layout and topic/partition allocation
        self.logger.info("Getting cluster layout and topic/partition allocation..")
        await consumer.start()
        try:
            self.logger.info("Waiting for new messages..")
            async for msg in consumer:
                try:
                    self.logger.info("Got a new message")
                    await self.on_message(msg)
                except BaseEventEngineError:
                    pass
        except KeyboardInterrupt:
            await consumer.stop()

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
                return await self.ee.raise_event_async(event, async_task=self.manager_async_task)
            self.logger.info("Event raised")
            return await self.ee.raise_event(event)
        except (ValueError, TypeError, BaseEventEngineError) as e:
            self.logger.exception(f"Unable to raise event: {e}")
            return
