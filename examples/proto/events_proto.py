from event_engine.event import Event
from examples.proto.payment_pb2 import PaymentEventData as PaymentProto


class PaymentProtoEvent(Event[PaymentProto]):
    name: str = "PaymentProtoEvent"
    topic: str = "demo_topic_1"
    is_publishable: bool = True
    is_internal: bool = False
