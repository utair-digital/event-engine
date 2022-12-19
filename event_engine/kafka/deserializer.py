from event_engine.base import BaseDeserializer


class LegacyDeserializer(BaseDeserializer):
    @classmethod
    def deserialize(cls, event_data: dict) -> dict:
        """
        Deserialize event data
        Args:
            event_data (dict): event data

        Returns:
            dict
        """
        _event_data = event_data
        if event_data.get("meta", {}).get("version") != "2.0":
            _event_data = {
                "name": event_data.get("type"),
                "topic": event_data.get("data", {}).get("topic"),
                "is_internal": event_data.get("data", {}).get("is_internal", True),
                "is_published": event_data.get("data", {}).get("is_published", True),
                "event_key": event_data.get("data", {}).get("event_key", None),
                "data": event_data.get("data", {}).get("data")
            }

        return _event_data
