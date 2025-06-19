# app/utils/db_utils/audit/change_tracker.py

import logging
import json
import asyncio
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from functools import wraps
from app.core.core_database import DatabaseManager, DatabaseError

logger = logging.getLogger(__name__)

class ChangeTracker:
    """
    Tracks and records database changes with comprehensive auditing.
    Provides decorators and utilities for automatic change tracking.
    """

    def __init__(self):
        self._initialize_tracking_tables()

    def _initialize_tracking_tables(self) -> None:
        """Initialize tracking tables"""
        try:
            queries = [
                # Change history table
                """
                CREATE TABLE IF NOT EXISTS change_history (
                    id SERIAL PRIMARY KEY,
                    table_name TEXT NOT NULL,
                    record_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    old_data JSONB,
                    new_data JSONB,
                    changed_fields TEXT[],
                    user_id TEXT,
                    client_ip TEXT,
                    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    application_context JSONB
                );

                CREATE INDEX IF NOT EXISTS idx_change_history_table 
                ON change_history(table_name, record_id);
                
                CREATE INDEX IF NOT EXISTS idx_change_history_timestamp 
                ON change_history(timestamp);
                """,
                
                # Failed operations table
                """
                CREATE TABLE IF NOT EXISTS failed_operations (
                    id SERIAL PRIMARY KEY,
                    table_name TEXT NOT NULL,
                    record_id TEXT,
                    error_message TEXT,
                    operation_context JSONB,
                    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """
            ]

            for query in queries:
                DatabaseManager.execute_query(query)

        except Exception as e:
            logger.error(f"Error initializing tracking tables: {str(e)}")
            raise DatabaseError(f"Failed to initialize tracking tables: {str(e)}")

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
                    # Extract operation context
                    context = self._build_context(kwargs)
                    record_id = kwargs.get('id') or kwargs.get('record_id')

                    try:
                        # Get original state if updating
                        old_data = None
                        if record_id:
                            old_data = self._get_current_state(table_name, record_id)

                        # Execute the async function
                        result = await func(*args, **kwargs)

                        # Log the change after function completion
                        action = self._determine_action(old_data, kwargs)
                        new_data = self._get_new_state(
                            table_name,
                            record_id or result,
                            kwargs.get('data')
                        )

                        await self._log_change(
                            table_name=table_name,
                            record_id=record_id or result,
                            action=action,
                            old_data=old_data,
                            new_data=new_data,
                            context=context
                        )

                        return result

                    except Exception as e:
                        # Log failed operation
                        await self._log_failed_operation(
                            table_name,
                            record_id,
                            str(e),
                            context
                        )
                        raise

                return async_wrapper
            else:
                @wraps(func)
                def sync_wrapper(*args, **kwargs):
                    # Extract operation context
                    context = self._build_context(kwargs)
                    record_id = kwargs.get('id') or kwargs.get('record_id')

                    try:
                        # Get original state if updating
                        old_data = None
                        if record_id:
                            old_data = self._get_current_state(table_name, record_id)

                        # Execute the sync function
                        result = func(*args, **kwargs)

                        # Log the change after function completion
                        action = self._determine_action(old_data, kwargs)
                        new_data = self._get_new_state(
                            table_name,
                            record_id or result,
                            kwargs.get('data')
                        )

                        self._log_change(
                            table_name=table_name,
                            record_id=record_id or result,
                            action=action,
                            old_data=old_data,
                            new_data=new_data,
                            context=context
                        )

                        return result

                    except Exception as e:
                        # Log failed operation
                        self._log_failed_operation(
                            table_name,
                            record_id,
                            str(e),
                            context
                        )
                        raise

                return sync_wrapper

        return decorator

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
        if old_data:
            return 'UPDATE'
        return 'INSERT'

    def _get_current_state(self, table_name: str, record_id: Any) -> Optional[Dict]:
        """Get current state of a database record"""
        try:
            query = f"SELECT * FROM {table_name} WHERE id = %s"
            result = DatabaseManager.execute_query(query, (record_id,))
            return dict(result[0]) if result else None
        except Exception as e:
            logger.error(f"Error getting current state: {str(e)}")
            return None

    def _get_new_state(
        self,
        table_name: str,
        record_id: Any,
        data: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Get new state of a record after operation"""
        if data:
            return data
        return self._get_current_state(table_name, record_id)

    async def _log_change(
        self,
        table_name: str,
        record_id: Any,
        action: str,
        old_data: Optional[Dict],
        new_data: Optional[Dict],
        context: Dict
    ) -> None:
        """Log a database change with full context"""
        try:
            changed_fields = self._calculate_changed_fields(old_data, new_data)
            
            query = """
                INSERT INTO change_history (
                    table_name, record_id, action, old_data, new_data,
                    changed_fields, user_id, client_ip, application_context
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            params = (
                table_name,
                str(record_id),
                action,
                json.dumps(old_data) if old_data else None,
                json.dumps(new_data) if new_data else None,
                changed_fields,
                context.get('user_id'),
                context.get('client_ip'),
                json.dumps(context.get('additional_context'))
            )

            await DatabaseManager.execute_query(query, params)

        except Exception as e:
            logger.error(f"Error logging change: {str(e)}")
            logger.exception("Change logging failed but continuing")

    async def _log_failed_operation(
        self,
        table_name: str,
        record_id: Any,
        error: str,
        context: Dict
    ) -> None:
        """Log failed database operations"""
        try:
            query = """
                INSERT INTO failed_operations (
                    table_name, record_id, error_message,
                    operation_context
                ) VALUES (%s, %s, %s, %s)
            """
            
            params = (
                table_name,
                str(record_id) if record_id else None,
                error,
                json.dumps(context)
            )

            await DatabaseManager.execute_query(query, params)

        except Exception as e:
            logger.error(f"Error logging failed operation: {str(e)}")
            logger.exception("Failed operation logging failed")

    def _calculate_changed_fields(
        self,
        old_data: Optional[Dict],
        new_data: Optional[Dict]
    ) -> List[str]:
        """Calculate which fields changed between versions"""
        if not old_data or not new_data:
            return []

        changed_fields = []
        for key in old_data:
            if key in new_data and old_data[key] != new_data[key]:
                changed_fields.append(key)

        return changed_fields

    def get_change_history(
        self,
        table_name: Optional[str] = None,
        record_id: Optional[Any] = None,
        action: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Get change history with filters"""
        try:
            query = "SELECT * FROM change_history WHERE 1=1"
            params = []

            if table_name:
                query += " AND table_name = %s"
                params.append(table_name)

            if record_id:
                query += " AND record_id = %s"
                params.append(str(record_id))

            if action:
                query += " AND action = %s"
                params.append(action)

            if start_date:
                query += " AND timestamp >= %s"
                params.append(start_date)

            if end_date:
                query += " AND timestamp <= %s"
                params.append(end_date)

            query += " ORDER BY timestamp DESC LIMIT %s"
            params.append(limit)

            return DatabaseManager.execute_query(query, tuple(params))

        except Exception as e:
            logger.error(f"Error getting change history: {str(e)}")
            raise DatabaseError(f"Failed to get change history: {str(e)}")

    def get_failed_operations(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Get failed operations history"""
        try:
            query = "SELECT * FROM failed_operations WHERE 1=1"
            params = []

            if start_date:
                query += " AND timestamp >= %s"
                params.append(start_date)

            if end_date:
                query += " AND timestamp <= %s"
                params.append(end_date)

            query += " ORDER BY timestamp DESC LIMIT %s"
            params.append(limit)

            return DatabaseManager.execute_query(query, tuple(params))

        except Exception as e:
            logger.error(f"Error getting failed operations: {str(e)}")
            raise DatabaseError(f"Failed to get failed operations: {str(e)}")