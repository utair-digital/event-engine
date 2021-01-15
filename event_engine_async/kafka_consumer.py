import msgpack
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
            kafka_config: KafkaConfig
    ):
        self.ee = event_manager
        self.kafka_config = kafka_config
        self.ee_register = event_register_function

    async def listen(self):
        await self.ee_register()
        consumer = AIOKafkaConsumer(
            *self.kafka_config.subscribe_topics,
            bootstrap_servers=self.kafka_config.servers,
            group_id=self.kafka_config.service_name
        )
        # Get cluster layout and topic/partition allocation
        await consumer.start()
        try:
            async for msg in consumer:
                try:
                    await self.on_message(msg)
                except BaseEventEngineError:
                    pass
        except KeyboardInterrupt:
            await consumer.stop()

    async def on_message(self, message: ConsumerRecord):
        try:
            message.value = msgpack.loads(message.value)
        except Exception as e:
            # TODO залогировать
            # msgpack.UnpackException - deprecated, use Exception to catch all errors
            return

        try:
            event: Event = self.ee.deserialize_event(message.value)
            print(event.serialize())
        except BaseEventEngineError:
            # TODO залогировать
            return

        try:
            assert event.topic == message.topic, "Unable to ensure topic is same as deserialized event topic"
        except AssertionError:
            # TODO залогировать
            return

        # TODO зарейзить событие
