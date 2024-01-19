import asyncio
import logging.config
import uuid

from event_engine import EventManager
from event_engine.kafka import KafkaConfig, KafkaBus
from examples.events import PaymentObserver, PaymentEvent1, PaymentEvent2


async def raise_events():
    logging.config.dictConfig(
        {
            "version": 1,
            "formatters": {"verbose": {"format": "%(name)s: %(message)s"}},
            "handlers": {
                "console": {
                    "level": "DEBUG",
                    "class": "logging.StreamHandler",
                    "formatter": "verbose",
                },
            },
            "loggers": {
                "kafka.bus": {
                    "level": "DEBUG",
                    "propagate": True,
                    "handlers": ["console"],
                },
                "KafkaSubClient": {
                    "level": "DEBUG",
                    "propagate": True,
                    "handlers": ["console"],
                },
            },
        }
    )

    kafka_config = KafkaConfig(
        servers=["localhost:9092"],
        subscribe_topics=["demo_topic"],
        service_name="example_service",
    )

    kafka_bus = KafkaBus(kafka_config=kafka_config)
    await kafka_bus.start()
    em: EventManager = EventManager(bus=kafka_bus)
    em.register(
        events=[PaymentEvent1, PaymentEvent2],
        handler=PaymentObserver(),
    )

    # raise events
    data = dict(
        payment_id=str(uuid.uuid4()),
        status="ok",
    )

    # internal event
    await em.raise_event(PaymentEvent1(data=data))

    # should be sent to kafka
    await em.raise_event(PaymentEvent2(data=data))


try:
    asyncio.run(raise_events())
except KeyboardInterrupt:
    print("Interrupted")
