from opentelemetry.propagators import textmap
from .event import Event


class ContextGetter(textmap.Getter[textmap.CarrierT]):
    def get(self, carrier: Event, key: str) -> list[str] | None:
        if carrier is None:
            return None

        if key == "traceparent":
            return [carrier.meta.trace]

    def keys(self, carrier: textmap.CarrierT) -> list[str]:
        if carrier is None:
            return []
        return [key for (key, value) in carrier]


class ContextSetter(textmap.Setter[textmap.CarrierT]):
    def set(self, carrier: Event, key: str, value: str) -> None:
        if carrier is None or key is None:
            return
        carrier.meta.trace = value
