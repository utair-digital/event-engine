from typing import List


class KafkaConfig:
    servers: List[str] = []
    subscribe_topics: List[str] = []
    service_name: str = None
    metadata_max_age_ms: int = 10 * 1000

    def __init__(
        self,
        servers: List[str],
        subscribe_topics: List[str],
        service_name: str,
        metadata_max_age_mx: int = 10 * 1000,
    ):
        self.servers = servers
        self.subscribe_topics = subscribe_topics
        self.service_name = service_name
        self.metadata_max_age_ms = metadata_max_age_mx
