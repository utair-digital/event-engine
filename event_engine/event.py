from typing import Generic, TypeVar, Optional

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
        topic = kwargs.get("topic", None) or self.__fields__["topic"].default
        is_internal = kwargs.get("is_internal", None) or self.__fields__["is_internal"].default
        is_publishable = kwargs.get("is_publishable", None) or self.__fields__["is_publishable"].default

        is_published = kwargs.get("is_published", None) or self.__fields__["is_published"].default

        if not self.__fields__["name"].default and not kwargs.get("name"):
            kwargs.update({"name": self.__class__.__name__})

        if not topic and is_published:
            raise EventBuildingError("Publishable event must contain topic")

        if not any([is_publishable, is_internal]):
            raise EventBuildingError("Event must be at least one of is_internal/is_publishable")

        super().__init__(**kwargs)

    def get_event_key(self) -> Optional[bytes]:
        """
        event uniquid key
        """
        return None

    @classmethod
    def get_default_name(cls) -> str:
        return cls.__fields__["name"].default
