from event_engine_async.kafka_config import KafkaConfig

settings = {
    'servers': ['localhost:29092'],
    'subscribe_topics': ['demo_topic'],
    'service_name': "example_service"
}

KAFKA_CONFIG = KafkaConfig(**settings)
