from event_engine.kafka.deserializer import LegacyDeserializer
from event_engine.kafka.serializer import LegacySerializer
from tests.fixtures.event import payment_event  # noqa
from tests.fixtures.event import PaymentEvent
from pydantic import ValidationError


def test_event_deserialization():
    event_data = {
        "name": "payment_event",
        "topic": "payments",
        "data": {"payment_id": "we5r24t-okj", "status": "ok"},
        "meta": {"version": "2.0", "trace": None},
        "event_key": "1",
        "is_published": False,
        "is_internal": True,
        "is_publishable": False,
    }

    ev = PaymentEvent(**event_data)

    assert ev.data.payment_id == "we5r24t-okj"
    assert ev.topic == "payments"
    assert ev.name == "payment_event"
    assert ev.is_internal == True
    assert ev.is_publishable == False
    assert ev.is_published == False


def test_event_deserialization_with_not_valid_data():
    event_data = {
        "name": "payment_event",
        "topic": "payments",
        "data": {"payment_id": "we5r24t-okj"},
        "meta": {"version": "2.0", "trace": None},
        "event_key": "1",
        "is_published": False,
        "is_internal": True,
        "is_publishable": False,
    }

    error = None
    try:
        ev = PaymentEvent(**event_data)
    except ValidationError as err:
        error = err

    assert isinstance(error, ValidationError)


def test_event_serialization(payment_event):
    expected_event_data = {
        "name": "payment_event",
        "topic": "payments",
        "data": {"payment_id": "we5r24t-okj", "status": "ok"},
        "meta": {"version": "2.0", "trace": None},
        "event_key": "1",
        "is_published": False,
        "is_internal": True,
        "is_publishable": False,
    }

    event_data = payment_event.dict(by_alias=True)

    assert event_data == expected_event_data


def test_event_legacy_serialization(payment_event):
    expected_legacy_event_data = {
        "type": "payment_event",
        "data": {
            "data": {"payment_id": "we5r24t-okj", "status": "ok"},
            "name": "payment_event",
            "is_published": False,
            "is_publishable": False,
            "is_internal": True,
            "event_key": "1",
            "topic": "payments",
        },
    }

    expected_event_data = {
        "name": "payment_event",
        "topic": "payments",
        "data": {"payment_id": "we5r24t-okj", "status": "ok"},
        "meta": {"version": "2.0", "trace": None},
        "event_key": "1",
        "is_published": False,
        "is_internal": True,
        "is_publishable": False,
    }

    serialized_event_data_2_0 = LegacySerializer.serialize(payment_event)

    payment_event.meta.version = "1.0"
    serialized_event_data_1_0 = LegacySerializer.serialize(payment_event)

    assert serialized_event_data_2_0 == expected_event_data
    assert serialized_event_data_1_0 == expected_legacy_event_data


def test_event_legacy_deserialization(payment_event):
    legacy_event_data = {
        "type": "payment_event",
        "data": {
            "data": {"payment_id": "we5r24t-okj", "status": "ok"},
            "name": "payment_event",
            "is_published": False,
            "is_publishable": False,
            "is_internal": True,
            "event_key": "1",
            "topic": "payments",
        },
    }

    event_data_from_legacy = LegacyDeserializer.deserialize(legacy_event_data)

    event = PaymentEvent(**event_data_from_legacy)

    assert event.topic == "payments"
    assert event.name == "payment_event"
    assert event.data.payment_id == "we5r24t-okj"
