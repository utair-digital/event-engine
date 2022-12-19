from ..exceptions import BaseEventEngineError


class ProvideTopicsAndPattern(BaseEventEngineError):
    pass


class NotProvidedTopicsOrPattern(BaseEventEngineError):
    pass


class CantUnpackDataFromBus(BaseEventEngineError):
    pass
