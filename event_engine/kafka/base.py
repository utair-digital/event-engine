import os
from typing import List, Optional, Union, Dict
from pathlib import Path
from dataclasses import dataclass
from aiokafka.helpers import create_ssl_context
from ssl import SSLContext
from enum import Enum

from .exceptions import ProvideTopicsAndPattern, NotProvidedTopicsOrPattern

class AuthSecProtocol(str, Enum):
    PLAIN_TEXT = "PLAINTEXT"
    SASL_SSL = "SASL_SSL"
    SASL_PLAIN_TEXT = "SASL_PLAINTEXT"

class SaslMechanism(str, Enum):
    PLAIN = "PLAIN"
    SCRAM_SHA_512 = "SCRAM-SHA-512"


@dataclass
class KafkaAuth:
    username: str
    password: str
    tlsCAFile: Optional[str] = None
    project_root: Optional[str] = None

    @property
    def ssl_context(self):
        if not self.tlsCAFile:
            raise ValueError("Unable to create ssl context, certificate was not provided")
        return create_ssl_context(
            cafile=self.get_cert_path
        )

    def validate(self):
        if not all((
            self.username,
            self.password
        )):
            raise ValueError("Unable to authenticate, username or password was not provided")

    @property
    def get_cert_path(self) -> str:
        if os.path.isabs(self.tlsCAFile):
            return self.tlsCAFile
        if not self.project_root:
            raise ValueError("Unable to read certificate, path is not absolute and project_root was not provided")
        proj_root = Path(self.project_root)
        return os.path.abspath(os.path.join(
            proj_root, self.tlsCAFile)
        )


class KafkaConfig:
    servers: List[str] = []
    subscribe_topics: List[str] = []
    subscribe_pattern: Optional[str] = None
    service_name: str = None
    metadata_max_age_ms: int = 10 * 1000
    auth: Optional[KafkaAuth] = None

    def __init__(
        self,
        servers: List[str],
        service_name: str,
        metadata_max_age_ms: int = 10 * 1000,
        subscribe_topics: Optional[List[str]] = None,
        subscribe_pattern: Optional[str] = None,
        auth: Optional[Union[KafkaAuth, Dict]] = None
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
        if subscribe_topics and subscribe_pattern:
            raise ProvideTopicsAndPattern()
        if not subscribe_topics:
            subscribe_topics = list()

        if not (subscribe_topics or subscribe_pattern):
            raise NotProvidedTopicsOrPattern()

        self.servers = servers
        self.subscribe_topics = subscribe_topics
        self.subscribe_pattern = subscribe_pattern
        self.service_name = service_name
        self.metadata_max_age_ms = metadata_max_age_ms

        if auth and isinstance(auth, dict):
            self.auth = KafkaAuth(**auth)
            self.auth.validate()
        elif auth and isinstance(auth, KafkaAuth):
            self.auth = auth
            self.auth.validate()
        else:
            self.auth = auth

    @property
    def should_auth(self) -> bool:
        return bool(self.auth)

    @property
    def security_protocol(self) -> AuthSecProtocol:
        if not self.auth:
            return AuthSecProtocol.PLAIN_TEXT
        if self.auth and self.auth.tlsCAFile:
            return AuthSecProtocol.SASL_SSL
        if self.auth and not self.auth.tlsCAFile:
            return AuthSecProtocol.SASL_PLAIN_TEXT
        raise ValueError("Unable to choose security protocol")

    @property
    def sasl_mechanism(self) -> SaslMechanism:
        return SaslMechanism.PLAIN if not self.should_auth else SaslMechanism.SCRAM_SHA_512

    @property
    def ssl_context(self) -> Optional[SSLContext]:
        if self.security_protocol != AuthSecProtocol.SASL_SSL:
            return None
        return self.auth.ssl_context

    def set_project_root(self, project_root: str):
        if not self.auth:
            return
        self.auth.project_root = project_root
