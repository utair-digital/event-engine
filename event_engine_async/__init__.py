"""
Модуль движка соытий
"""
import asyncio
from typing import Callable, Optional

from .event import Event                                # noqa
from .observer import Observer                          # noqa
from .observable import Observable                      # noqa

from .kafka_config import KafkaConfig                   # noqa
from .kafka_consumer import KafkaSubClient              # noqa

from .event_manager import EventManager


__MANAGER: Optional[EventManager] = None


def get_event_manager() -> EventManager:
    global __MANAGER
    if not __MANAGER:
        __MANAGER = EventManager()
    return __MANAGER


def run_kafka_consumer(
        kafka_conf: KafkaConfig,
        register_observers_function: Callable
):
    client = KafkaSubClient(
        event_manager=get_event_manager(),
        event_register_function=register_observers_function,
        kafka_config=kafka_conf
    )
    asyncio.run(client.listen())
