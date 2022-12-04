from event_engine import EventManager

_MANAGER = None


async def get_event_manager() -> EventManager:
    global _MANAGER
    if _MANAGER:
        return _MANAGER
    _MANAGER = EventManager()
    return await get_event_manager()
