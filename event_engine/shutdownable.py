import asyncio
import signal
from abc import ABC, abstractmethod


class ShutDownable(ABC):

    def __init__(self, logger):
        self.logger = logger
        self.register_signals()

    def register_signals(self):
        loop = asyncio.get_event_loop()
        signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT, signal.SIGQUIT)
        self.logger.info(f"Started in standalone mode, listening for signals: {signals}")
        for s in signals:
            loop.add_signal_handler(s, lambda s=s: asyncio.create_task(self.shutdown(s)))

    async def shutdown(self, signal):
        self.logger.info(f"Received exit signal {signal.name}...")
        await self._on_shutdown()
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        [task.cancel() for task in tasks]
        self.logger.info(f"Cancelling {len(tasks)} outstanding tasks")
        await asyncio.gather(*tasks)

    @abstractmethod
    async def _on_shutdown(self):
        raise NotImplementedError
