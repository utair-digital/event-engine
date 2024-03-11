from ..exceptions import BaseEventEngineError


class BaseKafkaBusError(BaseEventEngineError):
    pass


class ProvideTopicsAndPattern(BaseKafkaBusError):
    pass


class NotProvidedTopicsOrPattern(BaseKafkaBusError):
    pass


class CantUnpackDataFromBus(BaseKafkaBusError):
    pass


class CantRecreateNonExistingProducer(BaseKafkaBusError):
    pass


class CantCloseNonExistingProducer(BaseKafkaBusError):
    pass


class UnableToSendEventToKafka(BaseKafkaBusError):
    pass
