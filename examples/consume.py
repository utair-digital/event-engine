import asyncio

from event_engine import run_kafka_consumer, get_event_manager
from event_engine import KafkaConfig, EventManager

from examples.events import DemoObserver, DemoEvent1, DemoEvent2


async def consume():
    kafka_config = KafkaConfig(
        debug_level='DEBUG',
        servers=['localhost:29092'],
        subscribe_topics=['demo_topic'],
        service_name="example_service"
    )

    # Регистрируем
    em: EventManager = get_event_manager(kafka_config)
    em.register(
        [DemoEvent1, DemoEvent2],
        DemoObserver(),
        is_type_check=True
    )

    # Обрабатываем
    await run_kafka_consumer(kafka_config)

try:
    asyncio.run(consume())
except KeyboardInterrupt:
    pass
