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
    kafka_config = KafkaConfig(
        debug_level='DEBUG',
        servers=['localhost:29092'],
        subscribe_topics=['demo_topic'],
        service_name="example_service"
    )

    # Регистрируем
    em: EventManager = get_event_manager(kafka_config)
    em.register(
        events=[DemoEvent1, DemoEvent2],
        handler=DemoObserver(),
    )

    # Сообщаем:
    data = dict(
        event_id=str(uuid.uuid4()),
        who_am_i='raised_event',
    )
    await em.raise_event(DemoEvent1(data=data))
    await em.raise_event(DemoEvent2(data=data))

try:
    asyncio.run(raise_events())
except KeyboardInterrupt:
    print("Interrupted")
