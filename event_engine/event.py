from typing import Generic, TypeVar, Optional, Any, Dict

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

from .exceptions import EventBuildingError

T = TypeVar("T", bound=BaseModel)


class EventMeta(BaseModel):
    version: str = "2.0"
    trace: Optional[str] = None


class Event(GenericModel, Generic[T]):
    """
    common event
    """

    name: str = ""
    # fixme: Overriding this field in inherited objects can change the type
    topic: Optional[str] = None
    data: T
    meta: EventMeta = Field(default_factory=EventMeta)

    event_key: Optional[str] = None
    is_published: Optional[bool] = False
    is_internal: Optional[bool] = False
    is_publishable: Optional[bool] = False

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

        if not self.__fields__["name"].default and not kwargs.get("name"):
            kwargs.update({"name": self.__class__.__name__})

        if not self.topic and self.is_published:
            raise EventBuildingError("Publishable event must contain topic")

        if not any([self.is_publishable, self.is_internal]):
            raise EventBuildingError("Event must be at least one of is_internal/is_publishable")

    def _update_kwargs(self, key: Any, kwargs: Dict):
        value = kwargs.get(key, None) or self.__fields__[key].default
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
        return cls.__fields__["name"].default
