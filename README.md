# Asynchronous EventEngine with kafka bus

# Requirements

- `aiokafka==0.7.0`
- `msgpack`

## [Usage Examples](examples)

### Event Producing example:
``` python

    async def raise_events():
        kafka_config = KafkaConfig(
            debug_level='DEBUG',
            servers=['localhost:29092'],
            subscribe_topics=['demo_topic'],
            service_name="example_service"
        )
    
        # Register events
        em: EventManager = get_event_manager(kafka_config)
        em.register(
            events=[DemoInternalEvent, DemoInternalAndPublishableEvent],
            handler=DemoObserver(),
        )
    
        # Produce Events:
        data = dict(
            event_id=str(uuid.uuid4()),
            who_am_i='raised_event',
        )
        await em.raise_event(DemoInternalEvent(data=data))
        await em.raise_event(DemoInternalAndPublishableEvent(data=data))
    
    try:
        asyncio.run(raise_events())
    except KeyboardInterrupt:
        print("Interrupted")

```

### Standalone event consumer w/ signal listener:
``` python

    kafka_config = KafkaConfig(
        debug_level='DEBUG',
        servers=["yourkafka.server:9094"],
        subscribe_topics=['demo_topic'],
        service_name="example_service"
    )

    # Register events
    em: EventManager = get_event_manager(kafka_config)
    em.register(
        [DemoInternalEvent, DemoInternalAndPublishableEvent],
        DemoObserver(),
        is_type_check=True
    )

    # Listen and handle events
    await run_kafka_consumer(kafka_config, handle_signals=True)
```

### Application Embedded consumer:
``` python

    kafka_config = KafkaConfig(
        debug_level='DEBUG',
        servers=["srv01.kafka-dev.utair.io:9094"],
        subscribe_topics=['demo_topic'],
        service_name="example_service"
    )

    # Register events
    em: EventManager = get_event_manager(kafka_config)
    em.register(
        [DemoInternalEvent, DemoInternalAndPublishableEvent],
        DemoObserver(),
        is_type_check=True
    )
    
    client = KafkaSubClient(
        event_manager=get_event_manager(kafka_conf),
        kafka_config=kafka_conf,
    )
    
    application.on_startup.append(client.listen)
    application.on_cleanup.append(client.stop)
```