"""
Ключ для очередности событий
Обработка ошибок в лупе
Публикация события внутри приложения
"""

import uuid
import asyncio
from event_engine import get_event_manager
from examples.events import register_order_saved_observer, DemoEvent
from examples.kafka_settings import KAFKA_CONFIG

event_engine = get_event_manager(KAFKA_CONFIG)


async def raise_events():
    register_order_saved_observer()

    for i in range(100):
        await event_engine.raise_event(
            DemoEvent(dict(
                who_am_i='raised_event',
                event_id=str(uuid.uuid4())
            ))
        )

asyncio.run(raise_events())
