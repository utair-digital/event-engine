<p align="center">
  <b>Event Engine</b> - event driven framework with kafka bus
</p>

## 🍿Contents

- [Quickstart](#-quickstart)
- [Installation](#-installation)
- [Examples](#-examples)
    - [Basic produce event to kafka](#-basic-produce-event-to-kafka)
    - [Basic consume events from kafka](#-basic-consume-events-from-kafka)
    - [Consume events from kafka by pattern](#-consume-events-from-kafka-by-pattern)
    - [Custom bus](#-custom-bus)
    - [The Easiest way to get configure event manager](#-the-easiest-way-to-get-configure-event-manager)
    - [Protobuf events](#-protobuf-events)

## ⚡️ Quickstart

```python
class PaymentEventData(BaseModel):
    payment_id: str
    status: str


class PaymentEvent(Event[PaymentEventData]):
    topic: str = "demo_topic"

class PaymentObserver(Observer):
    async def handle_event(self, event: PaymentEvent):
        print(f"HANDLED {event.dict()}")


em: EventManager = EventManager()
em.register(
    events=[PaymentEvent],
    handler=PaymentObserver(),
)

# raise events
data = dict(
    payment_id=str(uuid.uuid4()),
    status="ok",
)

# internal event
await em.raise_event(PaymentEvent(data=data))
```

## ⚙️ Installation

https: ````pip install git+https://git@github.com/utair-digital/event-engine.git````

## 👀 Examples

#### 📖 **Basic produce event to kafka**

```python
kafka_config = KafkaConfig(
    servers=["localhost:9092"],
    subscribe_topics=["demo_topic"],
    service_name="example_service",
)
kafka_bus = KafkaBus(kafka_config=kafka_config)
await kafka_bus.start()

em: EventManager = EventManager(bus=kafka_bus)
em.register(
    events=[PaymentEvent1, PaymentEvent2],
    handler=PaymentObserver(),
)

# raise events
data = dict(
    payment_id=str(uuid.uuid4()),
    status="ok",
)

# internal event
await em.raise_event(PaymentEvent1(data=data))

# should be sent to kafka
await em.raise_event(PaymentEvent2(data=data))
```

#### 📖 **Basic consume events from kafka**
```python
kafka_config = KafkaConfig(
    servers=["localhost:9092"],
    subscribe_topics=["demo_topic"],
    service_name="example_service",
)

# register events
em: EventManager = EventManager()
em.register([PaymentEvent1, PaymentEvent2], PaymentObserver(), is_type_check=True)

client = KafkaSubClient(event_manager=em, kafka_config=kafka_config, handle_signals=False)

# listen events
await client.listen()

```

#### 📖 **Consume events from kafka by pattern**

```python
kafka_config = KafkaConfig(
        servers=["localhost:9092"],
        subscribe_pattern="demo.*",
        service_name="example_service",
    )

# register events
em: EventManager = EventManager()
em.register([PaymentEvent1, PaymentEvent2], PaymentObserver(), is_type_check=True)

client = KafkaSubClient(event_manager=em, kafka_config=kafka_config, handle_signals=False)

# listen events
await client.listen()
```

#### 📖 **Custom bus**
if you want to use custom bus, you should implement bus protocol

```python
class Bus(Protocol):
    async def send(self, event: Event):
        ...

custom_bus = Bus()
em: EventManager = EventManager(bus=custom_bus)
```

#### 📖 **The Easiest way to get configure event manager**

You can full configure your event manager

```python
from event_engine import EventManager

_MANAGER = None


async def get_event_manager() -> EventManager:
    global _MANAGER
    if _MANAGER:
        return _MANAGER
    _MANAGER = EventManager()
    return await get_event_manager()
```

#### 📖 **Protobuf events**

You can use generated protobuf messages as event data instead of pydantic models.
Install with proto support:

```bash
pip install event-engine[proto]
```

Define your `.proto` schema and generate Python classes, then use them as `T` in `Event[T]`:

```protobuf
// payment.proto
syntax = "proto3";

message PaymentEventData {
  string payment_id = 1;
  string status = 2;
}
```

```python
from event_engine.event import Event
from event_engine.observer import Observer
from payment_pb2 import PaymentEventData as PaymentProto


class PaymentEvent(Event[PaymentProto]):
    name: str = "PaymentEvent"
    topic: str = "payments"
    is_publishable: bool = True
    is_internal: bool = False


# produce — pass proto object directly
event = PaymentEvent(data=PaymentProto(payment_id="123", status="ok"))
await em.raise_event(event)


# consume — event.data is already a parsed proto object
class PaymentObserver(Observer):
    async def handle_event(self, event: PaymentEvent):
        print(event.data.payment_id)  # "123"
```

Proto data is serialized as a JSON dict on the wire (via `google.protobuf.json_format`) and automatically parsed back to a proto object on the consumer side.