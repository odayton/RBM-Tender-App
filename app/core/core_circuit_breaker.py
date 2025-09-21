"""
Core Circuit Breaker Module - Fault Tolerance and Graceful Degradation
"""

import time
import asyncio
import threading
from typing import Dict, Any, Optional, Callable, Union
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta
import structlog
from functools import wraps

logger = structlog.get_logger(__name__)

class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, calls fail fast
    HALF_OPEN = "half_open"  # Testing if service is back

@dataclass
class CircuitBreakerConfig:
    """Configuration for a circuit breaker."""
    failure_threshold: int = 5          # Number of failures before opening
    recovery_timeout: int = 60          # Seconds before trying half-open
    success_threshold: int = 3          # Successes needed to close from half-open
    timeout: int = 30                   # Timeout for individual calls
    expected_exception: type = Exception  # Exception type to count as failures
    fallback_function: Optional[Callable] = None  # Fallback when circuit is open

class CircuitBreakerStats:
    """Statistics for circuit breaker monitoring."""
    
    def __init__(self):
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.circuit_opens = 0
        self.circuit_closes = 0
        self.fallback_calls = 0
        self.last_failure_time = None
        self.last_success_time = None
        self.current_state = CircuitState.CLOSED
        self.state_changes = []
    
    def record_call(self, success: bool):
        """Record a call result."""
        self.total_calls += 1
        if success:
            self.successful_calls += 1
            self.last_success_time = datetime.utcnow()
        else:
            self.failed_calls += 1
            self.last_failure_time = datetime.utcnow()
    
    def record_state_change(self, old_state: CircuitState, new_state: CircuitState):
        """Record a state change."""
        self.current_state = new_state
        self.state_changes.append({
            'timestamp': datetime.utcnow(),
            'from': old_state.value,
            'to': new_state.value
        })
        
        if new_state == CircuitState.OPEN:
            self.circuit_opens += 1
        elif new_state == CircuitState.CLOSED:
            self.circuit_closes += 1
    
    def get_success_rate(self) -> float:
        """Get success rate percentage."""
        if self.total_calls == 0:
            return 100.0
        return (self.successful_calls / self.total_calls) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            'total_calls': self.total_calls,
            'successful_calls': self.successful_calls,
            'failed_calls': self.failed_calls,
            'success_rate': self.get_success_rate(),
            'circuit_opens': self.circuit_opens,
            'circuit_closes': self.circuit_closes,
            'fallback_calls': self.fallback_calls,
            'current_state': self.current_state.value,
            'last_failure_time': self.last_failure_time.isoformat() if self.last_failure_time else None,
            'last_success_time': self.last_success_time.isoformat() if self.last_success_time else None,
            'state_changes': [
                {
                    'timestamp': change['timestamp'].isoformat(),
                    'from': change['from'],
                    'to': change['to']
                }
                for change in self.state_changes[-10:]  # Last 10 changes
            ]
        }

class CircuitBreaker:
    """Circuit breaker implementation with configurable thresholds and timeouts."""
    
    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.stats = CircuitBreakerStats()
        self._lock = threading.Lock()
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True
        
        time_since_failure = time.time() - self.last_failure_time
        return time_since_failure >= self.config.recovery_timeout
    
    def _record_success(self):
        """Record a successful call."""
        with self._lock:
            self.success_count += 1
            self.failure_count = 0
            self.stats.record_call(True)
            
            if self.state == CircuitState.HALF_OPEN and self.success_count >= self.config.success_threshold:
                self._transition_to(CircuitState.CLOSED)
    
    def _record_failure(self):
        """Record a failed call."""
        with self._lock:
            self.failure_count += 1
            self.success_count = 0
            self.last_failure_time = time.time()
            self.stats.record_call(False)
            
            if self.state == CircuitState.CLOSED and self.failure_count >= self.config.failure_threshold:
                self._transition_to(CircuitState.OPEN)
            elif self.state == CircuitState.HALF_OPEN:
                self._transition_to(CircuitState.OPEN)
    
    def _transition_to(self, new_state: CircuitState):
        """Transition to a new state."""
        if self.state != new_state:
            old_state = self.state
            self.state = new_state
            self.stats.record_state_change(old_state, new_state)
            
            logger.info("Circuit breaker state changed",
                       circuit_name=self.name,
                       from_state=old_state.value,
                       to_state=new_state.value)
    
    def _call_fallback(self, *args, **kwargs):
        """Call the fallback function if available."""
        if self.config.fallback_function:
            self.stats.fallback_calls += 1
            logger.info("Circuit breaker fallback called", circuit_name=self.name)
            return self.config.fallback_function(*args, **kwargs)
        else:
            raise Exception(f"Circuit breaker '{self.name}' is open and no fallback function provided")
    
    def call(self, func: Callable, *args, **kwargs):
        """Execute a function with circuit breaker protection."""
        with self._lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._transition_to(CircuitState.HALF_OPEN)
                    self.success_count = 0
                else:
                    return self._call_fallback(*args, **kwargs)
        
        try:
            # Execute the function with timeout
            if asyncio.iscoroutinefunction(func):
                # For async functions, we need to handle them differently
                result = asyncio.run(asyncio.wait_for(func(*args, **kwargs), timeout=self.config.timeout))
            else:
                # For sync functions, use threading timeout
                result = self._execute_with_timeout(func, *args, **kwargs)
            
            self._record_success()
            return result
            
        except self.config.expected_exception as e:
            self._record_failure()
            logger.warning("Circuit breaker failure recorded",
                          circuit_name=self.name,
                          error=str(e),
                          failure_count=self.failure_count)
            raise
        except asyncio.TimeoutError:
            self._record_failure()
            logger.warning("Circuit breaker timeout",
                          circuit_name=self.name,
                          timeout=self.config.timeout)
            raise Exception(f"Circuit breaker '{self.name}' timeout after {self.config.timeout}s")
        except Exception as e:
            self._record_failure()
            logger.error("Circuit breaker unexpected error",
                        circuit_name=self.name,
                        error=str(e))
            raise
    
    def _execute_with_timeout(self, func: Callable, *args, **kwargs):
        """Execute a function with timeout using threading."""
        result = [None]
        exception = [None]
        
        def target():
            try:
                result[0] = func(*args, **kwargs)
            except Exception as e:
                exception[0] = e
        
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout=self.config.timeout)
        
        if thread.is_alive():
            raise asyncio.TimeoutError(f"Function timed out after {self.config.timeout}s")
        
        if exception[0]:
            raise exception[0]
        
        return result[0]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics."""
        return self.stats.to_dict()
    
    def reset(self):
        """Manually reset the circuit breaker to closed state."""
        with self._lock:
            self._transition_to(CircuitState.CLOSED)
            self.failure_count = 0
            self.success_count = 0
            self.last_failure_time = None
            logger.info("Circuit breaker manually reset", circuit_name=self.name)

class CircuitBreakerManager:
    """Manages multiple circuit breakers."""
    
    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {}
        self._lock = threading.Lock()
    
    def create_breaker(self, name: str, config: CircuitBreakerConfig) -> CircuitBreaker:
        """Create a new circuit breaker."""
        with self._lock:
            if name in self.breakers:
                logger.warning("Circuit breaker already exists", name=name)
                return self.breakers[name]
            
            breaker = CircuitBreaker(name, config)
            self.breakers[name] = breaker
            logger.info("Circuit breaker created", name=name)
            return breaker
    
    def get_breaker(self, name: str) -> Optional[CircuitBreaker]:
        """Get a circuit breaker by name."""
        return self.breakers.get(name)
    
    def remove_breaker(self, name: str) -> bool:
        """Remove a circuit breaker."""
        with self._lock:
            if name in self.breakers:
                del self.breakers[name]
                logger.info("Circuit breaker removed", name=name)
                return True
            return False
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all circuit breakers."""
        return {
            name: breaker.get_stats()
            for name, breaker in self.breakers.items()
        }
    
    def reset_all(self):
        """Reset all circuit breakers."""
        for breaker in self.breakers.values():
            breaker.reset()
        logger.info("All circuit breakers reset")

# Global circuit breaker manager
circuit_manager = CircuitBreakerManager()

# Predefined circuit breaker configurations
DEFAULT_CONFIGS = {
    'database': CircuitBreakerConfig(
        failure_threshold=5,
        recovery_timeout=30,
        success_threshold=3,
        timeout=10,
        expected_exception=Exception
    ),
    'external_api': CircuitBreakerConfig(
        failure_threshold=3,
        recovery_timeout=60,
        success_threshold=2,
        timeout=15,
        expected_exception=Exception
    ),
    'file_operations': CircuitBreakerConfig(
        failure_threshold=3,
        recovery_timeout=30,
        success_threshold=2,
        timeout=20,
        expected_exception=OSError
    ),
    'email_service': CircuitBreakerConfig(
        failure_threshold=3,
        recovery_timeout=120,
        success_threshold=2,
        timeout=30,
        expected_exception=Exception
    ),
    'pdf_generation': CircuitBreakerConfig(
        failure_threshold=2,
        recovery_timeout=60,
        success_threshold=2,
        timeout=45,
        expected_exception=Exception
    )
}

# Decorator for circuit breaker protection
def circuit_breaker(name: str, config: Optional[CircuitBreakerConfig] = None, 
                   fallback: Optional[Callable] = None):
    """Decorator to add circuit breaker protection to functions."""
    def decorator(func):
        # Get or create circuit breaker
        breaker_config = config or DEFAULT_CONFIGS.get(name, CircuitBreakerConfig())
        if fallback:
            breaker_config.fallback_function = fallback
        
        breaker = circuit_manager.get_breaker(name)
        if not breaker:
            breaker = circuit_manager.create_breaker(name, breaker_config)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return breaker.call(func, *args, **kwargs)
        
        return wrapper
    return decorator

# Specific circuit breaker decorators
def database_circuit_breaker(fallback: Optional[Callable] = None):
    """Circuit breaker for database operations."""
    return circuit_breaker('database', DEFAULT_CONFIGS['database'], fallback)

def external_api_circuit_breaker(fallback: Optional[Callable] = None):
    """Circuit breaker for external API calls."""
    return circuit_breaker('external_api', DEFAULT_CONFIGS['external_api'], fallback)

def file_operations_circuit_breaker(fallback: Optional[Callable] = None):
    """Circuit breaker for file operations."""
    return circuit_breaker('file_operations', DEFAULT_CONFIGS['file_operations'], fallback)

def email_service_circuit_breaker(fallback: Optional[Callable] = None):
    """Circuit breaker for email service."""
    return circuit_breaker('email_service', DEFAULT_CONFIGS['email_service'], fallback)

def pdf_generation_circuit_breaker(fallback: Optional[Callable] = None):
    """Circuit breaker for PDF generation."""
    return circuit_breaker('pdf_generation', DEFAULT_CONFIGS['pdf_generation'], fallback)

# Utility functions
def init_circuit_breakers():
    """Initialize default circuit breakers."""
    for name, config in DEFAULT_CONFIGS.items():
        circuit_manager.create_breaker(name, config)
    
    logger.info("Circuit breakers initialized", 
                count=len(DEFAULT_CONFIGS),
                breakers=list(DEFAULT_CONFIGS.keys()))

def get_circuit_breaker_stats():
    """Get statistics for all circuit breakers."""
    return circuit_manager.get_all_stats()

def reset_circuit_breaker(name: str):
    """Reset a specific circuit breaker."""
    breaker = circuit_manager.get_breaker(name)
    if breaker:
        breaker.reset()
        return True
    return False

def reset_all_circuit_breakers():
    """Reset all circuit breakers."""
    circuit_manager.reset_all()

# Health check integration
def check_circuit_breaker_health() -> Dict[str, Any]:
    """Check the health of all circuit breakers."""
    stats = get_circuit_breaker_stats()
    unhealthy_breakers = []
    
    for name, breaker_stats in stats.items():
        if breaker_stats['current_state'] == CircuitState.OPEN.value:
            unhealthy_breakers.append({
                'name': name,
                'state': breaker_stats['current_state'],
                'failure_count': breaker_stats['failed_calls'],
                'last_failure': breaker_stats['last_failure_time']
            })
    
    return {
        'status': 'unhealthy' if unhealthy_breakers else 'healthy',
        'total_breakers': len(stats),
        'unhealthy_breakers': unhealthy_breakers,
        'stats': stats
    }


