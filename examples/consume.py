import asyncio
import logging.config

from event_engine import EventManager
from event_engine.kafka import KafkaConfig
from event_engine.kafka import KafkaSubClient

from examples.events import PaymentObserver, PaymentEvent1, PaymentEvent2


async def consume():
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
                "kafka.sub.client": {
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

    # register events
    em: EventManager = EventManager()
    em.register([PaymentEvent1, PaymentEvent2], PaymentObserver(), is_type_check=True)

    client = KafkaSubClient(event_manager=em, kafka_config=kafka_config, handle_signals=False)

    # listen events
    await client.listen()


try:
    asyncio.run(consume())
except KeyboardInterrupt:
    pass
