import json
import asyncio
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from functools import wraps
from app.core.core_database import DatabaseManager, DatabaseError
from app.core.core_logging import logger # Use central app logger

class ChangeTracker:
    """
    Tracks and records database changes with comprehensive auditing.
    Provides decorators and utilities for automatic change tracking.
    """

    # The __init__ is no longer needed as table creation is handled by migrations.
    # def __init__(self):
    #     self._initialize_tracking_tables() # This is now removed.

    def track_changes(self, table_name: str):
        """
        Decorator to automatically track changes to database operations.
        Supports both sync and async functions.
        
        Args:
            table_name: Name of the table being modified
        """
        def decorator(func: Callable):
            if asyncio.iscoroutinefunction(func):
                @wraps(func)
                async def async_wrapper(*args, **kwargs):
                    return await self._execute_tracked_operation(func, table_name, True, *args, **kwargs)
                return async_wrapper
            else:
                @wraps(func)
                def sync_wrapper(*args, **kwargs):
                    # For sync functions, we can't use an async helper.
                    # The logic is duplicated but necessary to avoid event loop issues.
                    context = self._build_context(kwargs)
                    record_id = kwargs.get('id') or kwargs.get('record_id')
                    try:
                        old_data = self._get_current_state(table_name, record_id) if record_id else None
                        result = func(*args, **kwargs)
                        action = self._determine_action(old_data, kwargs)
                        current_id = record_id or result
                        new_data = self._get_new_state(table_name, current_id, kwargs.get('data'))
                        
                        # Fire and forget the logging so it doesn't block the sync function
                        asyncio.ensure_future(self._log_change(
                            table_name, current_id, action, old_data, new_data, context
                        ))
                        return result
                    except Exception as e:
                        logger.error(f"Exception in tracked sync operation for table '{table_name}': {e}", exc_info=True)
                        asyncio.ensure_future(self._log_failed_operation(
                            table_name, record_id, str(e), context
                        ))
                        raise
                return sync_wrapper
        return decorator

    async def _execute_tracked_operation(self, func: Callable, table_name: str, is_async: bool, *args, **kwargs):
        """Helper to contain the core tracking logic for async operations."""
        context = self._build_context(kwargs)
        record_id = kwargs.get('id') or kwargs.get('record_id')
        try:
            old_data = self._get_current_state(table_name, record_id) if record_id else None
            
            if is_async:
                result = await func(*args, **kwargs)
            else:
                # This branch is kept for logical completeness but the sync_wrapper handles sync calls.
                result = func(*args, **kwargs)

            action = self._determine_action(old_data, kwargs)
            current_id = record_id or result
            new_data = self._get_new_state(table_name, current_id, kwargs.get('data'))
            
            await self._log_change(table_name, current_id, action, old_data, new_data, context)
            return result
        except Exception as e:
            logger.error(f"Exception in tracked operation for table '{table_name}': {e}", exc_info=True)
            await self._log_failed_operation(table_name, record_id, str(e), context)
            raise

    def _build_context(self, kwargs: Dict) -> Dict[str, Any]:
        """Build operation context from kwargs"""
        return {
            'user_id': kwargs.get('user_id'),
            'client_ip': kwargs.get('client_ip'),
            'timestamp': datetime.now().isoformat(),
            'additional_context': kwargs.get('context', {})
        }

    def _determine_action(self, old_data: Optional[Dict], kwargs: Dict) -> str:
        """Determine the type of database action"""
        if 'delete' in kwargs or kwargs.get('action') == 'DELETE':
            return 'DELETE'
        return 'UPDATE' if old_data else 'INSERT'

    def _get_current_state(self, table_name: str, record_id: Any) -> Optional[Dict]:
        """Get current state of a database record"""
        try:
            # Assuming primary key columns are consistently named 'id' or passed in kwargs.
            pk_column = 'id' # This might need to be more flexible in a real-world scenario.
            query = f"SELECT * FROM {table_name} WHERE {pk_column} = %s"
            result = DatabaseManager.execute_query(query, (record_id,))
            return dict(result[0]) if result else None
        except Exception as e:
            logger.error(f"Error getting current state for {table_name}:{record_id}: {e}", exc_info=True)
            return None

    def _get_new_state(self, table_name: str, record_id: Any, data: Optional[Dict] = None) -> Optional[Dict]:
        """Get new state of a record after operation"""
        if data:
            return data
        return self._get_current_state(table_name, record_id)

    async def _log_change(
        self, table_name: str, record_id: Any, action: str, 
        old_data: Optional[Dict], new_data: Optional[Dict], context: Dict
    ) -> None:
        """Log a database change with full context"""
        try:
            changed_fields = self._calculate_changed_fields(old_data, new_data)
            if not changed_fields and action == 'UPDATE':
                logger.debug(f"No fields changed for {table_name}:{record_id}. Skipping audit log.")
                return

            query = """
                INSERT INTO change_history (
                    table_name, record_id, action, old_data, new_data,
                    changed_fields, user_id, client_ip, application_context
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                table_name, str(record_id), action,
                json.dumps(old_data) if old_data else None,
                json.dumps(new_data) if new_data else None,
                changed_fields, context.get('user_id'),
                context.get('client_ip'), json.dumps(context.get('additional_context'))
            )
            await asyncio.to_thread(DatabaseManager.execute_query, query, params)
        except Exception as e:
            logger.error(f"CRITICAL: Failed to log change for {table_name}:{record_id}. Error: {e}", exc_info=True)

    async def _log_failed_operation(
        self, table_name: str, record_id: Any, error: str, context: Dict
    ) -> None:
        """Log failed database operations"""
        try:
            query = """
                INSERT INTO failed_operations (
                    table_name, record_id, error_message, operation_context
                ) VALUES (%s, %s, %s, %s)
            """
            params = (
                table_name, str(record_id) if record_id else None,
                error, json.dumps(context)
            )
            await asyncio.to_thread(DatabaseManager.execute_query, query, params)
        except Exception as e:
            logger.error(f"CRITICAL: Failed to log a FAILED OPERATION. Error: {e}", exc_info=True)

    def _calculate_changed_fields(self, old_data: Optional[Dict], new_data: Optional[Dict]) -> List[str]:
        """Calculate which fields changed between versions"""
        if not new_data: return []
        if not old_data: return list(new_data.keys()) # It's an INSERT

        changed_fields = []
        for key, new_value in new_data.items():
            if old_data.get(key) != new_value:
                changed_fields.append(key)
        return changed_fields

    # The get_change_history and get_failed_operations methods belong more in the
    # AuditReporter class, as their job is reporting, not tracking. We can assume
    # they are handled there.