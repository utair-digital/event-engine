class BaseEventEngineError(Exception):
    pass


class ObserverAlreadyRegistered(BaseEventEngineError):
    pass


class InvalidObserverIDError(BaseEventEngineError):
    pass


class EventNotRegisteredError(BaseEventEngineError):
    pass


class InvalidObserverType(BaseEventEngineError):
    pass


class InvalidEventType(BaseEventEngineError):
    pass


class EventBuildingError(BaseEventEngineError):
    pass


class BusNotDefinedError(BaseEventEngineError):
    pass


class EventWasNotSentToBus(BaseEventEngineError):
    pass
