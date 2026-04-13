from examples.proto.payment_pb2 import (
    Currency,
    Money,
    PassengerInfo,
    PaymentEventData as PaymentProto,
    PAYMENT_STATUS_SUCCESS,
    PAYMENT_STATUS_FAILED,
)
from event_engine.event import Event


class PaymentProtoEvent(Event[PaymentProto]):
    name: str = "PaymentProtoEvent"
    topic: str = "demo_topic"
    is_publishable: bool = True
    is_internal: bool = False


def test_proto_event_accepts_proto_object():
    """Event[ProtoMessage] should accept a proto instance as data"""
    proto_msg = PaymentProto(payment_id="123", status=PAYMENT_STATUS_SUCCESS)
    event = PaymentProtoEvent(data=proto_msg)
    assert event.data.payment_id == "123"
    assert event.data.status == PAYMENT_STATUS_SUCCESS



def test_existing_pydantic_event_unaffected():
    """Existing Event[BaseModel] must still work after changes"""
    from tests.fixtures.event import PaymentEvent
    event = PaymentEvent(
        name="payment_event",
        topic="payments",
        data={"payment_id": "we5r24t-okj", "status": "ok"},
        meta={"version": "2.0", "trace": None},
        event_key="1",
        is_published=False,
        is_internal=True,
        is_publishable=False,
    )
    assert event.data.payment_id == "we5r24t-okj"


def test_proto_event_serializes_data_as_dict():
    """LegacySerializer must serialize proto data as JSON dict"""
    from event_engine.kafka.serializer import LegacySerializer

    proto_msg = PaymentProto(payment_id="123", status=2)  # 2 = PAYMENT_STATUS_SUCCESS
    event = PaymentProtoEvent(data=proto_msg)

    result = LegacySerializer.serialize(event)

    assert isinstance(result["data"], dict)
    assert result["data"]["payment_id"] == "123"


def test_proto_event_auto_parses_dict():
    """Event[ProtoMessage] should auto-parse dict → proto (from Kafka JSON deserialization)"""
    event = PaymentProtoEvent(
        name="PaymentProtoEvent",
        topic="demo_topic",
        data={"payment_id": "dict-roundtrip", "status": "PAYMENT_STATUS_SUCCESS"},
        is_publishable=True,
        is_internal=False,
    )

    assert isinstance(event.data, PaymentProto)
    assert event.data.payment_id == "dict-roundtrip"


def test_proto_event_full_roundtrip():
    """Simulate full Kafka path: Event → serialize → reconstruct Event from dict"""
    from event_engine.kafka.serializer import LegacySerializer

    original = PaymentProtoEvent(
        data=PaymentProto(payment_id="roundtrip-123", status=PAYMENT_STATUS_SUCCESS),
    )

    # продюсер: serialize → dict (уходит в Kafka как JSON)
    serialized = LegacySerializer.serialize(original)

    # консьюмер: dict из Kafka → Event (model_validator парсит data обратно в proto)
    restored = PaymentProtoEvent(**serialized)

    assert isinstance(restored.data, PaymentProto)
    assert restored.data.payment_id == "roundtrip-123"
    assert restored.data.status == PAYMENT_STATUS_SUCCESS
    assert restored.name == original.name
    assert restored.topic == original.topic


def test_proto_event_complex_fields_roundtrip():
    """Roundtrip with nested messages, enum, repeated and map fields"""
    from event_engine.kafka.serializer import LegacySerializer

    original = PaymentProtoEvent(
        data=PaymentProto(
            payment_id="complex-456",
            status=PAYMENT_STATUS_FAILED,
            order_id="ORD-001",
            amount=Money(amount=99900, currency=Currency.CURRENCY_RUB),
            passenger=PassengerInfo(
                first_name="Ivan",
                last_name="Ivanov",
                email="ivan@example.com",
                phone="+79001234567",
            ),
            ticket_numbers=["SU-1", "SU-2", "SU-3"],
            metadata={"channel": "web", "promo": "SALE"},
        ),
    )

    serialized = LegacySerializer.serialize(original)
    restored = PaymentProtoEvent(**serialized)

    assert isinstance(restored.data, PaymentProto)
    assert restored.data.payment_id == "complex-456"
    assert restored.data.status == PAYMENT_STATUS_FAILED
    assert restored.data.order_id == "ORD-001"
    assert restored.data.amount.amount == 99900
    assert restored.data.amount.currency == Currency.CURRENCY_RUB
    assert restored.data.passenger.first_name == "Ivan"
    assert restored.data.passenger.email == "ivan@example.com"
    assert list(restored.data.ticket_numbers) == ["SU-1", "SU-2", "SU-3"]
    assert restored.data.metadata["channel"] == "web"
    assert restored.data.metadata["promo"] == "SALE"


def test_pydantic_event_serialization_unchanged():
    """LegacySerializer must not change behaviour for pydantic events"""
    from event_engine.kafka.serializer import LegacySerializer
    from tests.fixtures.event import PaymentEvent

    event = PaymentEvent(
        name="payment_event",
        topic="payments",
        data={"payment_id": "we5r24t-okj", "status": "ok"},
        meta={"version": "2.0", "trace": None},
        event_key="1",
        is_published=False,
        is_internal=True,
        is_publishable=False,
    )

    result = LegacySerializer.serialize(event)
    assert result["data"] == {"payment_id": "we5r24t-okj", "status": "ok"}
