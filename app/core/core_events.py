from typing import Any, Callable, Dict, List, Optional, Set
from enum import Enum
import logging
import threading
from dataclasses import dataclass
from datetime import datetime
from functools import wraps
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class EventPriority(Enum):
    """Priority levels for event handlers"""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3

@dataclass
class Event:
    """Base event class containing common event data"""
    name: str
    data: Dict[str, Any]
    timestamp: datetime = datetime.utcnow()
    source: Optional[str] = None
    priority: EventPriority = EventPriority.NORMAL

class EventHandler:
    """Handler for managing event subscriptions and dispatching"""
    
    def __init__(self):
        self._handlers: Dict[str, List[tuple[Callable, EventPriority]]] = {}
        self._async_handlers: Dict[str, List[tuple[Callable, EventPriority]]] = {}
        self._lock = threading.Lock()
        self._executor = ThreadPoolExecutor()
        self._max_retries = 3
        
    def subscribe(self, event_name: str, handler: Callable, 
                 priority: EventPriority = EventPriority.NORMAL,
                 is_async: bool = False) -> None:
        """
        Subscribe a handler to an event
        Args:
            event_name: Name of the event to subscribe to
            handler: Callback function to handle the event
            priority: Priority level for the handler
            is_async: Whether the handler is async
        """
        with self._lock:
            handlers_dict = self._async_handlers if is_async else self._handlers
            if event_name not in handlers_dict:
                handlers_dict[event_name] = []
            handlers_dict[event_name].append((handler, priority))
            # Sort handlers by priority (highest first)
            handlers_dict[event_name].sort(key=lambda x: x[1].value, reverse=True)
    
    def unsubscribe(self, event_name: str, handler: Callable) -> None:
        """
        Unsubscribe a handler from an event
        Args:
            event_name: Name of the event
            handler: Handler to unsubscribe
        """
        with self._lock:
            for handlers_dict in [self._handlers, self._async_handlers]:
                if event_name in handlers_dict:
                    handlers_dict[event_name] = [
                        (h, p) for h, p in handlers_dict[event_name] 
                        if h != handler
                    ]
    
    async def dispatch_async(self, event: Event) -> None:
        """
        Dispatch an event to all async handlers
        Args:
            event: Event to dispatch
        """
        if event.name in self._async_handlers:
            for handler, _ in self._async_handlers[event.name]:
                try:
                    await handler(event)
                except Exception as e:
                    logger.error(
                        f"Error in async handler for event {event.name}: {str(e)}",
                        exc_info=True
                    )

    def dispatch(self, event: Event) -> None:
        """
        Dispatch an event to all synchronous handlers
        Args:
            event: Event to dispatch
        """
        if event.name in self._handlers:
            for handler, _ in self._handlers[event.name]:
                try:
                    self._executor.submit(self._execute_handler, handler, event)
                except Exception as e:
                    logger.error(
                        f"Error dispatching event {event.name}: {str(e)}",
                        exc_info=True
                    )
    
    def _execute_handler(self, handler: Callable, event: Event, 
                        retry_count: int = 0) -> None:
        """
        Execute a handler with retry logic
        Args:
            handler: Handler to execute
            event: Event to handle
            retry_count: Current retry attempt
        """
        try:
            handler(event)
        except Exception as e:
            if retry_count < self._max_retries:
                logger.warning(
                    f"Retrying handler for event {event.name} "
                    f"(attempt {retry_count + 1})"
                )
                self._execute_handler(handler, event, retry_count + 1)
            else:
                logger.error(
                    f"Handler failed after {self._max_retries} retries "
                    f"for event {event.name}: {str(e)}",
                    exc_info=True
                )

# Global event handler instance
event_handler = EventHandler()

def event_publisher(event_name: str, priority: EventPriority = EventPriority.NORMAL):
    """
    Decorator for publishing events from methods
    Args:
        event_name: Name of the event to publish
        priority: Priority level for the event
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            # Create and dispatch event
            event = Event(
                name=event_name,
                data={'result': result, 'args': args, 'kwargs': kwargs},
                priority=priority
            )
            event_handler.dispatch(event)
            return result
        return wrapper
    return decorator

# Specific Event Classes for the application

class PumpEvent(Event):
    """Event class for pump-related events"""
    def __init__(self, pump_id: str, action: str, data: Dict[str, Any],
                 priority: EventPriority = EventPriority.NORMAL):
        super().__init__(
            name=f"pump.{action}",
            data={'pump_id': pump_id, **data},
            source="pump_module",
            priority=priority
        )

class QuoteEvent(Event):
    """Event class for quote-related events"""
    def __init__(self, quote_id: str, action: str, data: Dict[str, Any],
                 priority: EventPriority = EventPriority.NORMAL):
        super().__init__(
            name=f"quote.{action}",
            data={'quote_id': quote_id, **data},
            source="quote_module",
            priority=priority
        )

class AuditEvent(Event):
    """Event class for audit logging"""
    def __init__(self, user_id: str, action: str, data: Dict[str, Any]):
        super().__init__(
            name="audit.log",
            data={'user_id': user_id, 'action': action, **data},
            source="audit_module",
            priority=EventPriority.HIGH
        )