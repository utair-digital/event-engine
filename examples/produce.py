"""
Ключ для очередности событий
Обработка ошибок в лупе
Публикация события внутри приложения
"""

import uuid
import asyncio
from event_engine import get_event_manager
from event_engine import EventManager, KafkaConfig
from examples.events import DemoObserver, DemoEvent1, DemoEvent2


async def raise_events():
    settings = {
        'servers': ['localhost:29092'],
        'subscribe_topics': ['demo_topic'],
        'service_name': "example_service"
    }

    em: EventManager = get_event_manager(KafkaConfig(**settings))
    em.register(
        events=[DemoEvent1, DemoEvent2],
        handler=DemoObserver(),
        is_type_check=True
    )

    for i in range(1):
        data = dict(
            who_am_i='raised_event',
            event_id=str(uuid.uuid4())
        )
        await em.raise_event(DemoEvent1(data=data))
        await em.raise_event(DemoEvent2(data=data))

asyncio.run(raise_events())
