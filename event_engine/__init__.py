"""
Модуль движка соытий
"""
from typing import Callable, Optional

from .event import Event                                # noqa
from .observer import Observer                          # noqa
from .observable import Observable                      # noqa

from .base import KafkaConfig                           # noqa
from .kafka_consumer import KafkaSubClient              # noqa

from .event_manager import EventManager


__MANAGER: Optional[EventManager] = None


def get_event_manager(kafka_conf: KafkaConfig) -> EventManager:
    global __MANAGER
    if not __MANAGER:
        __MANAGER = EventManager(kafka_config=kafka_conf)
    return __MANAGER


async def run_kafka_consumer(
        kafka_conf: KafkaConfig,
):
    client = KafkaSubClient(
        event_manager=get_event_manager(kafka_conf),
        kafka_config=kafka_conf,
    )
    await client.listen()
