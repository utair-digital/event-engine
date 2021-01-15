from .event_manager import EventManager

manager = None


def get_event_manager() -> EventManager:
    global manager
    if not manager:
        manager = EventManager()
    return manager
