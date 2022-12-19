from typing import List, Optional

from .exceptions import ProvideTopicsAndPattern, NotProvidedTopicsOrPattern


class KafkaConfig:
    servers: List[str] = []
    subscribe_topics: List[str] = []
    subscribe_pattern: Optional[str] = None
    service_name: str = None
    metadata_max_age_ms: int = 10 * 1000

    def __init__(
        self,
        servers: List[str],
        service_name: str,
        metadata_max_age_ms: int = 10 * 1000,
        subscribe_topics: List[str] = [],
        subscribe_pattern: Optional[str] = None,
    ):
        """
        kafka configs

        Args:
            servers (list):  list of
                ``host[:port]`` strings that the consumer should contact to bootstrap
                initial cluster metadata.
            service_name (str): Name of the consumer group to join for dynamic
                partition assignment (if enabled), and to use for fetching and
                committing offsets. If None, auto-partition assignment (via
                group coordinator) and offset commits are disabled.
            metadata_max_age_ms (int): The period of time in milliseconds after
                which we force a refresh of metadata even if we haven't seen any
                partition leadership changes to proactively discover any new
                brokers or partitions. Default: 300000
            subscribe_topics (list): List of topics for subscription.
            subscribe_pattern (str): Pattern to match available topics. You must provide
                either topics or pattern, but not both.
        Raises:
             ProvideTopicsAndPattern: If topics and pattern are provided
             NotProvidedTopicsOrPattern: If neither topics or pattern is provided
        """
        if not (subscribe_topics or subscribe_pattern):
            raise NotProvidedTopicsOrPattern()
        if subscribe_topics and subscribe_pattern:
            raise ProvideTopicsAndPattern()
        self.servers = servers
        self.subscribe_topics = subscribe_topics
        self.subscribe_pattern = subscribe_pattern
        self.service_name = service_name
        self.metadata_max_age_ms = metadata_max_age_ms
