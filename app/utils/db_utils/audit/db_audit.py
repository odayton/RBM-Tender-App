# app/utils/db_utils/audit/db_audit.py

from typing import Dict, List, Any, Optional, Union
import logging
from datetime import datetime
import json
from app.core.core_database import DatabaseManager
from app.core.core_errors import DatabaseError
from app.app_logging import app_logger

logger = logging.getLogger(__name__)

class DatabaseAudit:
    """
    Centralized database audit system that combines functionality from multiple audit implementations.
    Handles all database audit logging, tracking, and reporting.
    """

    def __init__(self):
        self._initialize_audit_tables()
        self.logger = app_logger

    def _initialize_audit_tables(self) -> None:
        """Initialize all required audit tables"""
        try:
            queries = [
                # Main audit log table
                """
                CREATE TABLE IF NOT EXISTS audit_log (
                    id SERIAL PRIMARY KEY,
                    table_name TEXT NOT NULL,
                    record_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    old_data JSONB,
                    new_data JSONB,
                    changed_fields TEXT[],
                    user_id TEXT,
                    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    client_ip TEXT,
                    application_context JSONB
                );

                CREATE INDEX IF NOT EXISTS idx_audit_table_action 
                ON audit_log(table_name, action);
                
                CREATE INDEX IF NOT EXISTS idx_audit_timestamp 
                ON audit_log(timestamp);
                """,

                # Audit configuration table
                """
                CREATE TABLE IF NOT EXISTS audit_configuration (
                    table_name TEXT PRIMARY KEY,
                    enabled BOOLEAN DEFAULT true,
                    track_changes BOOLEAN DEFAULT true,
                    excluded_fields TEXT[],
                    retention_days INTEGER DEFAULT 365,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """,

                # Audit metrics table
                """
                CREATE TABLE IF NOT EXISTS audit_metrics (
                    id SERIAL PRIMARY KEY,
                    table_name TEXT NOT NULL,
                    action TEXT NOT NULL,
                    record_count INTEGER NOT NULL,
                    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    details JSONB
                );
                """
            ]

            for query in queries:
                DatabaseManager.execute_query(query)
            logger.info("Audit tables initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing audit tables: {str(e)}")
            raise DatabaseError(f"Failed to initialize audit tables: {str(e)}")

    def log_change(
        self, 
        table_name: str,
        record_id: Union[str, int],
        action: str,
        old_data: Optional[Dict] = None,
        new_data: Optional[Dict] = None,
        user_id: Optional[str] = None,
        client_ip: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> None:
        """Log a database change with comprehensive tracking"""
        try:
            if not self._is_auditing_enabled(table_name):
                return

            changed_fields = self._calculate_changed_fields(
                table_name, old_data, new_data
            )

            audit_data = {
                'table_name': table_name,
                'record_id': str(record_id),
                'action': action,
                'old_data': json.dumps(old_data) if old_data else None,
                'new_data': json.dumps(new_data) if new_data else None,
                'changed_fields': changed_fields,
                'user_id': user_id,
                'client_ip': client_ip,
                'application_context': json.dumps(context) if context else None
            }

            query = """
                INSERT INTO audit_log (
                    table_name, record_id, action, old_data, new_data,
                    changed_fields, user_id, client_ip, application_context
                )
                VALUES (
                    %(table_name)s, %(record_id)s, %(action)s, %(old_data)s,
                    %(new_data)s, %(changed_fields)s, %(user_id)s,
                    %(client_ip)s, %(application_context)s
                )
            """
            DatabaseManager.execute_query(query, audit_data)

            # Update metrics
            self._update_metrics(table_name, action)

        except Exception as e:
            logger.error(f"Error logging audit record: {str(e)}")
            # Don't raise - auditing should not break main functionality
            logger.exception("Audit logging failed but operation continues")

    def _is_auditing_enabled(self, table_name: str) -> bool:
        """Check if auditing is enabled for a table"""
        query = """
            SELECT enabled 
            FROM audit_configuration 
            WHERE table_name = %s
        """
        result = DatabaseManager.execute_query(query, (table_name,))
        return result[0]['enabled'] if result else True

    def _calculate_changed_fields(
        self,
        table_name: str,
        old_data: Optional[Dict],
        new_data: Optional[Dict]
    ) -> List[str]:
        """Calculate which fields changed between versions"""
        if not old_data or not new_data:
            return []

        query = """
            SELECT excluded_fields 
            FROM audit_configuration 
            WHERE table_name = %s
        """
        result = DatabaseManager.execute_query(query, (table_name,))
        excluded_fields = result[0]['excluded_fields'] if result else []

        changed_fields = []
        for field in set(old_data.keys()) | set(new_data.keys()):
            if field in excluded_fields:
                continue

            old_value = old_data.get(field)
            new_value = new_data.get(field)

            if old_value != new_value:
                changed_fields.append(field)

        return changed_fields

    def _update_metrics(self, table_name: str, action: str) -> None:
        """Update audit metrics"""
        try:
            query = """
                INSERT INTO audit_metrics (
                    table_name, action, record_count, details
                )
                VALUES (
                    %s, %s, 1, 
                    jsonb_build_object('timestamp', CURRENT_TIMESTAMP)
                )
                ON CONFLICT (table_name, action, DATE(timestamp))
                DO UPDATE SET record_count = audit_metrics.record_count + 1
            """
            DatabaseManager.execute_query(query, (table_name, action))
        except Exception as e:
            logger.error(f"Error updating audit metrics: {str(e)}")

    def get_changes(
        self,
        table_name: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Get audit history with filters"""
        try:
            query = "SELECT * FROM audit_log WHERE 1=1"
            params = []

            if table_name:
                query += " AND table_name = %s"
                params.append(table_name)

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
            logger.error(f"Error retrieving audit history: {str(e)}")
            raise DatabaseError(f"Failed to retrieve audit history: {str(e)}")

    def get_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get audit metrics"""
        try:
            query = """
                SELECT 
                    table_name,
                    action,
                    SUM(record_count) as total_records,
                    COUNT(*) as operation_count,
                    MIN(timestamp) as first_operation,
                    MAX(timestamp) as last_operation
                FROM audit_metrics
                WHERE 1=1
            """
            params = []

            if start_date:
                query += " AND timestamp >= %s"
                params.append(start_date)

            if end_date:
                query += " AND timestamp <= %s"
                params.append(end_date)

            query += " GROUP BY table_name, action"

            return DatabaseManager.execute_query(query, tuple(params))

        except Exception as e:
            logger.error(f"Error retrieving audit metrics: {str(e)}")
            raise DatabaseError(f"Failed to retrieve audit metrics: {str(e)}")

# Create global audit instance
db_audit = DatabaseAudit()