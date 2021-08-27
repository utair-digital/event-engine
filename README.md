# Asynchronous EventEngine with kafka buss

## Примеры использования в папке examples

# Requirements

- `aiokafka==0.7.0`
- `msgpack`

# Install

- https: ``pip install git+https://gitlab.utair.ru/digital/repository/event-engine-async.git@1.0.0#egg=event_engine_async``
- ssh: ``pip install git+ssh://git@gitlab.utair.ru/digital/repository/event-engine-async.git@1.0.0#egg=event_engine_async
``
  
## Usage (см. examples)

### Standalone (слушать сигналы, Graceful Shutdown):
``` python

    kafka_config = KafkaConfig(
        debug_level='DEBUG',
        servers=["srv01.kafka-dev.utair.io:9094"],
        subscribe_topics=['demo_topic'],
        service_name="example_service"
    )

    Регистрируем события
    em: EventManager = get_event_manager(kafka_config)
    em.register(
        [DemoEvent1, DemoEvent2],
        DemoObserver(),
        is_type_check=True
    )

    # Обрабатываем события
    await run_kafka_consumer(kafka_config, handle_signals=True)
```

### Embedded (внутри приложения):
``` python

    kafka_config = KafkaConfig(
        debug_level='DEBUG',
        servers=["srv01.kafka-dev.utair.io:9094"],
        subscribe_topics=['demo_topic'],
        service_name="example_service"
    )
    
    Регистрируем события
    em: EventManager = get_event_manager(kafka_config)
    em.register(
        [DemoEvent1, DemoEvent2],
        DemoObserver(),
        is_type_check=True
    )
    
    client = KafkaSubClient(
        event_manager=get_event_manager(kafka_conf),
        kafka_config=kafka_conf,
    )
    
    application.on_startup.append(client.listen())
    application.on_startup.append(client.stop())
```