from event_engine import Event
from event_engine.base import BaseSerializer


class LegacySerializer(BaseSerializer):
    @classmethod
    def serialize(cls, event: Event) -> dict:
        if event.meta.version == "2.0":
            return event.dict(by_alias=True)

        return dict(
            type=event.name,
            data=dict(
                topic=event.topic,
                event_key=event.event_key,
                is_internal=event.is_internal,
                is_published=event.is_published,
                is_publishable=event.is_publishable,
                name=event.name,
                data=event.data.dict(by_alias=True),
            ),
        )
