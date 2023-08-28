from event_engine import Event
from event_engine.base import BaseSerializer


class LegacySerializer(BaseSerializer):
    @classmethod
    def serialize(cls, event: Event) -> dict:
        """
        Serialize event object to dict
        Args:
            event (Event): event object

        Returns:
            dict

        """
        if event.meta.version == "2.0":
            # fixme: unserializable python objects datetime/uuid etc
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
                # fixme: unserializable python objects datetime/uuid etc
                data=event.data.dict(by_alias=True),
            ),
        )
