from typing import Dict, List, Any, Optional, Union
import json
from app.core.core_database import DatabaseManager
from app.core.core_errors import DatabaseError
from app.core.core_logging import logger # Use central app logger

class DatabaseAuditor:
    """
    Handles the manual logging of database change events.
    The automatic tracking is handled by the ChangeTracker decorator.
    The reporting is handled by the AuditReporter.
    """

    # The __init__ and _initialize_audit_tables methods are removed.
    # Table creation should be handled by migration scripts.

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
        """
        Manually logs a database change. Fails silently to prevent crashing
        the main application functionality if auditing has an issue.
        """
        try:
            if not self._is_auditing_enabled(table_name):
                logger.debug(f"Auditing is disabled for table '{table_name}'. Skipping log.")
                return

            changed_fields = self._calculate_changed_fields(
                table_name, old_data, new_data
            )

            # Do not log an UPDATE if nothing actually changed.
            if action.upper() == 'UPDATE' and not changed_fields:
                logger.debug(f"No fields changed for {table_name}:{record_id}. Skipping audit log.")
                return

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
            logger.info(f"Successfully logged audit event: {action} on {table_name}:{record_id}")

            # Update metrics
            self._update_metrics(table_name, action)

        except Exception as e:
            logger.error(f"Error logging audit record: {e}", exc_info=True)
            # NOTE: This exception is intentionally not re-raised.
            # Auditing failures should not break main application functionality.

    def _is_auditing_enabled(self, table_name: str) -> bool:
        """Checks if auditing is enabled for a table. Defaults to True if not configured."""
        try:
            query = "SELECT enabled FROM audit_configuration WHERE table_name = %s"
            result = DatabaseManager.execute_query(query, (table_name,))
            # If no config exists, assume it is enabled.
            return result[0]['enabled'] if result else True
        except Exception as e:
            logger.error(f"Could not check audit configuration for '{table_name}'. Defaulting to enabled. Error: {e}", exc_info=True)
            return True


    def _calculate_changed_fields(
        self, table_name: str, old_data: Optional[Dict], new_data: Optional[Dict]
    ) -> List[str]:
        """Calculate which fields changed between versions, respecting exclusions."""
        if not new_data: return []
        if not old_data: return list(new_data.keys())

        try:
            query = "SELECT excluded_fields FROM audit_configuration WHERE table_name = %s"
            result = DatabaseManager.execute_query(query, (table_name,))
            excluded_fields = set(result[0]['excluded_fields']) if result and result[0]['excluded_fields'] else set()
        except Exception as e:
            logger.error(f"Could not retrieve excluded fields for '{table_name}'. Proceeding without exclusions. Error: {e}", exc_info=True)
            excluded_fields = set()

        changed_fields = []
        for field in set(old_data.keys()) | set(new_data.keys()):
            if field in excluded_fields:
                continue
            
            if old_data.get(field) != new_data.get(field):
                changed_fields.append(field)

        return changed_fields


    def _update_metrics(self, table_name: str, action: str) -> None:
        """Update audit metrics. This is a fire-and-forget operation."""
        try:
            # This query uses ON CONFLICT which is PostgreSQL-specific.
            # It atomically increments the count for a given table/action/day.
            query = """
                INSERT INTO audit_metrics (table_name, action, record_count, metric_date)
                VALUES (%s, %s, 1, CURRENT_DATE)
                ON CONFLICT (table_name, action, metric_date)
                DO UPDATE SET record_count = audit_metrics.record_count + 1
            """
            DatabaseManager.execute_query(query, (table_name, action))
        except Exception as e:
            logger.error(f"Error updating audit metrics: {e}", exc_info=True)


# Create a single, importable instance for use throughout the application
db_auditor = DatabaseAuditor()