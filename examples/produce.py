"""
Key is used for preserving the order of events
Handling errors in a loop
Publishing an event inside the application
"""
import uuid
import asyncio
from event_engine import get_event_manager
from event_engine import EventManager, KafkaConfig
from examples.events import DemoObserver, DemoInternalEvent, DemoInternalAndPublishableEvent


async def raise_events():
    kafka_config = KafkaConfig(
        debug_level='DEBUG',
        servers=['localhost:29092'],
        subscribe_topics=['demo_topic'],
        service_name="example_service"
    )

    # Register events
    em: EventManager = get_event_manager(kafka_config)
    em.register(
        events=[DemoInternalEvent, DemoInternalAndPublishableEvent],
        handler=DemoObserver(),
    )

    # Produce Events:
    data = dict(
        event_id=str(uuid.uuid4()),
        who_am_i='raised_event',
    )
    await em.raise_event(DemoInternalEvent(data=data))
    await em.raise_event(DemoInternalAndPublishableEvent(data=data))

try:
    asyncio.run(raise_events())
except KeyboardInterrupt:
    print("Interrupted")
