from event_engine.base import KafkaConfig

settings = {
    'servers': ['localhost:29092'],
    'subscribe_topics': ['demo_topic'],
    'service_name': "example_service"
}

# settings = {
#     'servers': ['srv01.kafka-dev.utair.io:9094'],
#     'subscribe_topics': ['demo_topic'],
#     'service_name': "example_service"
# }

KAFKA_CONFIG = KafkaConfig(**settings)
