from typing import Any, Callable, Dict, List, Optional
from enum import Enum
import threading
from dataclasses import dataclass, field
from datetime import datetime
from functools import wraps
import asyncio
from concurrent.futures import ThreadPoolExecutor
from flask import Flask
from .core_logging import logger # Use central app logger

class EventPriority(Enum):
    """Priority levels for event handlers."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3

@dataclass
class Event:
    """Base event class containing common event data."""
    name: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: Optional[str] = None
    priority: EventPriority = EventPriority.NORMAL

class EventHandler:
    """Manages event subscriptions and dispatching using a thread pool."""
    
    def __init__(self):
        self._handlers: Dict[str, List[tuple[Callable, EventPriority]]] = {}
        self._async_handlers: Dict[str, List[tuple[Callable, EventPriority]]] = {}
        self._lock = threading.Lock()
        self._executor: Optional[ThreadPoolExecutor] = None
        self.app: Optional[Flask] = None

    def init_app(self, app: Flask):
        """Initialize the event handler with the Flask app."""
        self.app = app
        # Create a thread pool executor with a name for easier debugging
        self._executor = ThreadPoolExecutor(max_workers=5, thread_name_prefix='EventHandler')
        logger.info("EventHandler initialized with ThreadPoolExecutor.")

    def subscribe(self, event_name: str, handler: Callable, priority: EventPriority = EventPriority.NORMAL):
        """
        Subscribe a handler to an event. Determines if handler is async automatically.
        """
        is_async = asyncio.iscoroutinefunction(handler)
        with self._lock:
            handlers_dict = self._async_handlers if is_async else self._handlers
            if event_name not in handlers_dict:
                handlers_dict[event_name] = []
            
            # Avoid duplicate subscriptions
            if any(h == handler for h, p in handlers_dict[event_name]):
                logger.warning(f"Handler {handler.__name__} is already subscribed to event {event_name}.")
                return

            handlers_dict[event_name].append((handler, priority))
            # Sort handlers by priority (highest first)
            handlers_dict[event_name].sort(key=lambda x: x[1].value, reverse=True)
            logger.info(f"Handler '{handler.__name__}' subscribed to event '{event_name}' with priority {priority.name}.")

    def dispatch(self, event: Event):
        """Dispatch an event to all subscribed handlers."""
        logger.debug(f"Dispatching event '{event.name}' with data: {event.data}")
        # Dispatch to sync handlers in the thread pool
        if event.name in self._handlers:
            for handler, _ in self._handlers[event.name]:
                if self._executor:
                    self._executor.submit(handler, event)
        
        # Dispatch to async handlers in the event loop
        if event.name in self._async_handlers:
            async def run_async_handlers():
                tasks = [handler(event) for handler, _ in self._async_handlers[event.name]]
                await asyncio.gather(*tasks, return_exceptions=True)

            # Fire and forget
            asyncio.ensure_future(run_async_handlers())

# --- Global Instance and Decorators ---

# Create a single instance to be imported and initialized in the app factory.
event_manager = EventHandler()

def event_publisher(event_name: str, priority: EventPriority = EventPriority.NORMAL):
    """Decorator for automatically publishing an event after a function call."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            event = Event(
                name=event_name,
                data={'result': result, 'args': args, 'kwargs': kwargs},
                priority=priority,
                source=func.__name__
            )
            event_manager.dispatch(event)
            return result
        return wrapper
    return decorator

# --- Specific Event Classes ---

class UserEvent(Event):
    """Event class for user-related events (e.g., login, logout)."""
    def __init__(self, user_id: Any, action: str, data: Optional[Dict] = None, priority: EventPriority = EventPriority.NORMAL):
        super().__init__(
            name=f"user.{action}",
            data={'user_id': user_id, **(data or {})},
            source="user_module",
            priority=priority
        )

class DealEvent(Event):
    """Event class for deal-related events."""
    def __init__(self, deal_id: Any, action: str, data: Optional[Dict] = None, priority: EventPriority = EventPriority.NORMAL):
        super().__init__(
            name=f"deal.{action}",
            data={'deal_id': deal_id, **(data or {})},
            source="deal_module",
            priority=priority
        )

class SystemEvent(Event):
    """Event class for system-level events (e.g., startup, shutdown)."""
    def __init__(self, action: str, data: Optional[Dict] = None, priority: EventPriority = EventPriority.CRITICAL):
        super().__init__(
            name=f"system.{action}",
            data=data or {},
            source="system",
            priority=priority
        )