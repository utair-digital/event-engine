from typing import Generic, TypeVar, Optional, Any, Dict

from pydantic import BaseModel, Field

from .exceptions import EventBuildingError

T = TypeVar("T", bound=BaseModel)


class EventMeta(BaseModel):
    version: str = "2.0"
    trace: str | None = None


class Event(BaseModel, Generic[T]):
    """
    common event
    """

    name: str = ""
    # fixme: Overriding this field in inherited objects can change the type
    topic: str | None = None
    data: T
    meta: EventMeta = Field(default_factory=EventMeta)

    event_key: str | None = None
    is_published: bool = False
    is_internal: bool = False
    is_publishable: bool = False

    def __init__(self, **kwargs):
        """

        Args:
            **kwargs:

        Raises:
             EventBuildingError:

        """
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
            raise EventBuildingError("Event must be at least one of is_internal/is_publishable")

    def _update_kwargs(self, key: Any, kwargs: Dict):
        value = kwargs.get(key, None) or self.model_fields[key].default
        if value is None:
            return
        kwargs[key] = value

    def get_event_key(self) -> Optional[bytes]: # noqa
        """
        event unique id key
        """
        return None

    @classmethod
    def get_default_name(cls) -> str:
        return cls.model_fields["name"].default

