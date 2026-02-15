import asyncio
import logging
from typing import Any, Callable, Dict, List


logger = logging.getLogger(__name__)


class EventBus:
    """Simple in-memory event bus for internal communication."""

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._queue = asyncio.Queue()

    def subscribe(self, event_type: str, handler: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        logger.debug(f"Subscribed to {event_type}")

    async def publish(self, event_type: str, data: Any):
        await self._queue.put((event_type, data))
        logger.debug(f"Published event {event_type}")

    async def start(self):
        """Processes events in the background."""
        logger.info("Event Bus started")
        while True:
            event_type, data = await self._queue.get()
            if event_type in self._subscribers:
                for handler in self._subscribers[event_type]:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(data)
                        else:
                            handler(data)
                    except Exception as e:
                        logger.error(f"Error in event handler for {event_type}: {e}")
            self._queue.task_done()
