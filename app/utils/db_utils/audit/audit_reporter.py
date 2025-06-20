from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import pandas as pd
from io import BytesIO
from app.core.core_database import DatabaseManager, DatabaseError
from .db_audit import DatabaseAuditor
from app.core.core_logging import logger # Use central app logger

class AuditReporter:
    """Generates comprehensive audit reports and analytics"""

    @staticmethod
    def generate_activity_report(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        table_names: Optional[List[str]] = None,
        users: Optional[List[str]] = None,
        format: str = 'excel'
    ) -> bytes:
        """
        Generate a detailed activity report for the specified period.
        """
        try:
            logger.info(f"Generating activity report for format: {format}")
            # Build base query
            query = """
                SELECT 
                    al.id, al.table_name, al.record_id, al.action,
                    al.changed_fields, al.user_id, al.client_ip, al.timestamp,
                    al.application_context, ac.enabled as auditing_enabled,
                    ac.track_changes as tracking_enabled
                FROM audit_log al
                LEFT JOIN audit_configuration ac ON al.table_name = ac.table_name
                WHERE 1=1
            """
            params = []

            # Apply filters
            if start_date:
                query += " AND al.timestamp >= %s"
                params.append(start_date)
            
            if end_date:
                query += " AND al.timestamp <= %s"
                params.append(end_date)
            
            if table_names:
                query += " AND al.table_name = ANY(%s)"
                params.append(table_names)
            
            if users:
                query += " AND al.user_id = ANY(%s)"
                params.append(users)

            query += " ORDER BY al.timestamp DESC"

            results = DatabaseManager.execute_query(query, tuple(params))
            report_data = AuditReporter._process_activity_data(results)
            
            if format == 'excel':
                return AuditReporter._generate_excel_report(report_data)
            elif format == 'csv':
                return AuditReporter._generate_csv_report(report_data)
            else:
                raise ValueError(f"Unsupported format: {format}")

        except Exception as e:
            logger.error(f"Error generating activity report: {e}", exc_info=True)
            raise DatabaseError(f"Failed to generate activity report: {e}")

    @staticmethod
    def generate_change_history(
        table_name: str,
        record_id: Union[str, int],
        include_context: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Generate detailed change history for a specific record.
        """
        try:
            logger.info(f"Generating change history for {table_name}:{record_id}")
            query = """
                SELECT 
                    timestamp, action, changed_fields, old_data, new_data,
                    user_id, client_ip, application_context
                FROM audit_log
                WHERE table_name = %s AND record_id = %s
                ORDER BY timestamp DESC
            """
            changes = DatabaseManager.execute_query(query, (table_name, str(record_id)))
            
            processed_changes = []
            for change in changes:
                processed_change = {
                    'timestamp': change['timestamp'],
                    'action': change['action'],
                    'user_id': change['user_id'],
                    'changes': AuditReporter._format_field_changes(
                        change['old_data'],
                        change['new_data'],
                        change['changed_fields']
                    )
                }
                if include_context:
                    processed_change.update({
                        'client_ip': change['client_ip'],
                        'context': change['application_context']
                    })
                processed_changes.append(processed_change)
            
            return processed_changes

        except Exception as e:
            logger.error(f"Error generating change history: {e}", exc_info=True)
            raise DatabaseError(f"Failed to generate change history: {e}")

    @staticmethod
    def generate_user_activity_summary(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Generate summary of user activities"""
        try:
            logger.info("Generating user activity summary.")
            # This query uses json_object_agg which is PostgreSQL specific.
            query = """
                WITH user_stats AS (
                    SELECT 
                        user_id,
                        COUNT(*) as total_actions,
                        COUNT(DISTINCT table_name) as tables_accessed,
                        MIN(timestamp) as first_action,
                        MAX(timestamp) as last_action,
                        json_object_agg(action, (SELECT COUNT(*) FROM audit_log WHERE user_id = al.user_id AND action = al.action))
                        as action_breakdown
                    FROM audit_log al
                    WHERE user_id IS NOT NULL
                    AND timestamp BETWEEN COALESCE(%s, timestamp) AND COALESCE(%s, timestamp)
                    GROUP BY user_id
                )
                SELECT 
                    us.*,
                    EXTRACT(EPOCH FROM (last_action - first_action))/3600 as activity_hours
                FROM user_stats us
                ORDER BY total_actions DESC
            """
            results = DatabaseManager.execute_query(query, (start_date, end_date))
            
            if not results:
                return {'user_summaries': [], 'total_users': 0}

            return {
                'user_summaries': results,
                'total_users': len(results),
                'period_start': start_date or min(r['first_action'] for r in results if r['first_action']),
                'period_end': end_date or max(r['last_action'] for r in results if r['last_action'])
            }

        except Exception as e:
            logger.error(f"Error generating user activity summary: {e}", exc_info=True)
            raise DatabaseError(f"Failed to generate user activity summary: {e}")

    @staticmethod
    def generate_security_report(
        days: int = 30,
        suspicious_threshold: int = 100
    ) -> Dict[str, Any]:
        """Generate security-focused audit report"""
        try:
            logger.info(f"Generating security report for the last {days} days.")
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            queries = {
                'high_volume_users': """
                    SELECT user_id, COUNT(*) as action_count, COUNT(DISTINCT client_ip) as ip_count
                    FROM audit_log WHERE timestamp >= %s GROUP BY user_id HAVING COUNT(*) >= %s
                """,
                'failed_operations': """
                    SELECT table_name, action, user_id, client_ip, application_context->'error_message' as error
                    FROM audit_log WHERE action = 'ERROR' AND timestamp >= %s
                """,
                'multiple_ips': """
                    SELECT user_id, array_agg(DISTINCT client_ip) as ips, COUNT(DISTINCT client_ip) as ip_count
                    FROM audit_log WHERE timestamp >= %s GROUP BY user_id HAVING COUNT(DISTINCT client_ip) > 3
                """
            }
            
            report = {}
            for name, query in queries.items():
                params = [start_date]
                if name == 'high_volume_users':
                    params.append(suspicious_threshold)
                report[name] = DatabaseManager.execute_query(query, tuple(params))
            
            return report

        except Exception as e:
            logger.error(f"Error generating security report: {e}", exc_info=True)
            raise DatabaseError(f"Failed to generate security report: {e}")

    # --- Private Helper Methods for Report Generation ---

    @staticmethod
    def _process_activity_data(data: List[Dict]) -> Dict[str, Any]:
        """Process raw activity data for reporting"""
        # This helper function's logic is sound and does not need changes.
        summary = {
            'total_actions': len(data),
            'unique_users': len(set(d['user_id'] for d in data if d['user_id'])),
            'unique_tables': len(set(d['table_name'] for d in data)),
            'action_types': {}, 'table_activity': {}, 'user_activity': {},
            'hourly_distribution': {i: 0 for i in range(24)}, 'details': data
        }
        for record in data:
            action = record['action']
            summary['action_types'][action] = summary['action_types'].get(action, 0) + 1
            table = record['table_name']
            if table not in summary['table_activity']:
                summary['table_activity'][table] = {'total': 0, 'actions': {}}
            summary['table_activity'][table]['total'] += 1
            summary['table_activity'][table]['actions'][action] = summary['table_activity'][table]['actions'].get(action, 0) + 1
            if record['user_id']:
                user = record['user_id']
                if user not in summary['user_activity']:
                    summary['user_activity'][user] = {'total': 0, 'tables': set()}
                summary['user_activity'][user]['total'] += 1
                summary['user_activity'][user]['tables'].add(table)
            hour = record['timestamp'].hour
            summary['hourly_distribution'][hour] += 1
        return summary

    @staticmethod
    def _generate_excel_report(data: Dict[str, Any]) -> bytes:
        """Generate Excel format report"""
        # This helper function's logic is sound and does not need changes.
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            pd.DataFrame({'Metric': ['Total Actions', 'Unique Users', 'Unique Tables'],
                          'Value': [data['total_actions'], data['unique_users'], data['unique_tables']]
                         }).to_excel(writer, sheet_name='Summary', index=False)
            pd.DataFrame([{'Action': k, 'Count': v} for k, v in data['action_types'].items()]
                        ).to_excel(writer, sheet_name='Actions', index=False)
            table_rows = []
            for table, stats in data['table_activity'].items():
                row = {'Table': table, 'Total': stats['total']}
                row.update(stats['actions'])
                table_rows.append(row)
            pd.DataFrame(table_rows).to_excel(writer, sheet_name='Table Activity', index=False)
            user_rows = [{'User': user, 'Total Actions': stats['total'], 'Tables Accessed': len(stats['tables'])}
                         for user, stats in data['user_activity'].items()]
            pd.DataFrame(user_rows).to_excel(writer, sheet_name='User Activity', index=False)
            pd.DataFrame([{'Hour': hour, 'Actions': count} for hour, count in data['hourly_distribution'].items()]
                        ).to_excel(writer, sheet_name='Hourly Activity', index=False)
            pd.DataFrame(data['details']).to_excel(writer, sheet_name='Details', index=False)
        return output.getvalue()

    @staticmethod
    def _generate_csv_report(data: Dict[str, Any]) -> bytes:
        """Generate CSV format report"""
        # This helper function's logic is sound and does not need changes.
        output = BytesIO()
        pd.DataFrame(data['details']).to_csv(output, index=False)
        return output.getvalue()

    @staticmethod
    def _format_field_changes(
        old_data: Optional[Dict], new_data: Optional[Dict], changed_fields: List[str]
    ) -> List[Dict[str, Any]]:
        """Format field changes for display"""
        # This helper function's logic is sound and does not need changes.
        changes = []
        if not changed_fields or not (old_data or new_data):
            return changes
        for field in changed_fields:
            changes.append({
                'field': field,
                'old_value': old_data.get(field) if old_data else None,
                'new_value': new_data.get(field) if new_data else None
            })
        return changes