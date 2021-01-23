"""
Модуль движка соытий
"""
import asyncio
import logging
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


def run_kafka_consumer(
        kafka_conf: KafkaConfig,
        register_observers_function: Callable,
        logger: logging.Logger
):
    client = KafkaSubClient(
        event_manager=get_event_manager(kafka_conf),
        event_register_function=register_observers_function,
        kafka_config=kafka_conf,
        logger=logger
    )
    asyncio.run(client.listen())
