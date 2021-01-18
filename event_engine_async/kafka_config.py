class KafkaConfig:

    servers = []
    subscribe_topics = []
    service_name = None

    def __init__(self, servers: list, subscribe_topics: list, service_name: str):
        self.servers = servers
        self.subscribe_topics = subscribe_topics
        self.service_name = service_name
