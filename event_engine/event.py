from typing import Generic, TypeVar, Optional, Any, Dict

from pydantic import BaseModel, ConfigDict, Field, field_serializer, model_validator

from .exceptions import EventBuildingError

try:
    from google.protobuf import json_format
    from google.protobuf.message import Message as ProtoMessage
except ImportError:
    json_format = None  # type: ignore[assignment]

    class ProtoMessage:  # type: ignore[no-redef]
        pass

T = TypeVar("T", bound=BaseModel | ProtoMessage)


class EventMeta(BaseModel):
    version: str = "2.0"
    trace: str | None = None


class Event(BaseModel, Generic[T]):
    """
    common event
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = ""
    # fixme: Overriding this field in inherited objects can change the type
    topic: str | None = None
    data: T
    meta: EventMeta = Field(default_factory=EventMeta)

    event_key: str | bytes | None = None
    is_published: bool = False
    is_internal: bool = False
    is_publishable: bool = False

    @model_validator(mode='before')
    @classmethod
    def _parse_proto_data(cls, values: Any) -> Any:
        if not isinstance(values, dict):
            return values
        t_type = cls.model_fields.get('data', None)
        if t_type is None:
            return values
        t_type = t_type.annotation
        if isinstance(t_type, type) and issubclass(t_type, ProtoMessage):
            data = values.get('data')
            if isinstance(data, dict):
                try:
                    values['data'] = json_format.ParseDict(data, t_type())
                except Exception as e:
                    raise ValueError(f"Failed to parse proto data for {t_type.__name__}: {e}") from e
        return values

    @field_serializer("data")
    def _serialize_data(self, value: Any) -> Any:
        if isinstance(value, ProtoMessage):
            return json_format.MessageToDict(value, preserving_proto_field_name=True)
        return value

    def __init__(self, **kwargs):
        self._update_kwargs("topic", kwargs)
        self._update_kwargs("is_internal", kwargs)
        self._update_kwargs("is_publishable", kwargs)
        self._update_kwargs("is_published", kwargs)
        super().__init__(**kwargs)

        if not self.model_fields["name"].default and not kwargs.get("name"):
            kwargs.update({"name": self.__class__.__name__})

        if not self.topic and self.is_published:
            raise EventBuildingError("Publishable event must contain topic")

        if not any([self.is_publishable, self.is_internal]):
            raise EventBuildingError(
                "Event must be at least one of is_internal/is_publishable"
            )

    def _update_kwargs(self, key: Any, kwargs: Dict):
        value = kwargs.get(key) if kwargs.get(key) is not None else self.model_fields[key].default
        if value is None:
            return
        kwargs[key] = value

    def get_event_key(self) -> Optional[bytes]:  # noqa
        """
        event unique id key
        partition key for kafka bus
        """
        if not self.event_key:
            return None
        if isinstance(self.event_key, str):
            return self.event_key.encode("utf-8")
        return self.event_key

    @classmethod
    def get_default_name(cls) -> str:
        return cls.model_fields["name"].default
