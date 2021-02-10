import logging
from .base import KafkaConfig


def setup_logger(config: KafkaConfig):
    loggers = [
        'aiokafka.consumer',
        'aiokafka.conn',
        'aiokafka.consumer.fetcher',
        'aiokafka.consumer.group_coordinator',
        'aiokafka.cluster',
        'aiokafka',
    ]
    for x in loggers:
        logging.getLogger(x).setLevel(config.debug_level or logging.ERROR)
