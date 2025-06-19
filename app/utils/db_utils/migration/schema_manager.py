# app/utils/db_utils/migration/schema_manager.py

from typing import Dict, List, Any, Optional, Union
import logging
from datetime import datetime
from app.core.core_database import DatabaseManager, DatabaseError

logger = logging.getLogger(__name__)

class SchemaManager:
    """Manages database schema versions and migrations"""

    SCHEMA_VERSION_TABLE = "schema_versions"

    @classmethod
    def initialize_schema_management(cls) -> None:
        """Initialize schema version tracking"""
        try:
            # Create schema versions table if it doesn't exist
            query = """
                CREATE TABLE IF NOT EXISTS schema_versions (
                    id SERIAL PRIMARY KEY,
                    version VARCHAR(50) NOT NULL,
                    description TEXT,
                    applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    applied_by VARCHAR(100),
                    script_name VARCHAR(255),
                    checksum VARCHAR(64),
                    status VARCHAR(20) DEFAULT 'success',
                    execution_time INTEGER,
                    error_message TEXT,
                    CONSTRAINT unique_version UNIQUE (version)
                );
                
                CREATE INDEX IF NOT EXISTS idx_schema_versions_version 
                ON schema_versions(version);
            """
            DatabaseManager.execute_query(query)
            logger.info("Schema version tracking initialized")

        except Exception as e:
            logger.error(f"Error initializing schema management: {str(e)}")
            raise DatabaseError(f"Failed to initialize schema management: {str(e)}")

    @classmethod
    def get_current_version(cls) -> str:
        """Get the current schema version"""
        try:
            query = """
                SELECT version 
                FROM schema_versions 
                WHERE status = 'success'
                ORDER BY applied_at DESC 
                LIMIT 1
            """
            result = DatabaseManager.execute_query(query)
            return result[0]['version'] if result else '0.0.0'

        except Exception as e:
            logger.error(f"Error getting current schema version: {str(e)}")
            raise DatabaseError(f"Failed to get schema version: {str(e)}")

    @classmethod
    def record_migration(
        cls,
        version: str,
        description: str,
        script_name: str,
        checksum: str,
        execution_time: int,
        applied_by: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> None:
        """Record a migration attempt"""
        try:
            query = """
                INSERT INTO schema_versions 
                (version, description, script_name, checksum, execution_time, 
                 applied_by, status, error_message)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                version,
                description,
                script_name,
                checksum,
                execution_time,
                applied_by,
                'failed' if error_message else 'success',
                error_message
            )
            DatabaseManager.execute_query(query, params)
            logger.info(f"Migration to version {version} recorded")

        except Exception as e:
            logger.error(f"Error recording migration: {str(e)}")
            raise DatabaseError(f"Failed to record migration: {str(e)}")

    @classmethod
    def verify_schema_integrity(cls) -> List[Dict[str, Any]]:
        """Verify the integrity of all schema objects"""
        try:
            issues = []
            
            # Check table existence and structure
            table_checks = [
                # Pump-related tables
                ('general_pump_details', ['sku', 'name', 'poles', 'kw']),
                ('historic_pump_data', ['sku', 'flow', 'head']),
                # Deal-related tables
                ('deals', ['id', 'name', 'stage', 'amount']),
                ('revisions', ['id', 'deal_id', 'version']),
                ('line_items', ['id', 'deal_id', 'entity_type']),
                # Organization-related tables
                ('contacts', ['id', 'representative_name', 'representative_email']),
                ('companies', ['id', 'company_name']),
                # Other core tables
                ('bom', ['id', 'pump_sku']),
                ('schema_versions', ['id', 'version'])
            ]
            
            for table_name, required_columns in table_checks:
                issues.extend(cls._check_table_structure(table_name, required_columns))
            
            # Check foreign key constraints
            fk_checks = [
                ('bom', 'pump_sku', 'general_pump_details', 'sku'),
                ('line_items', 'deal_id', 'deals', 'id'),
                ('revisions', 'deal_id', 'deals', 'id'),
                ('contacts', 'company_id', 'companies', 'id')
            ]
            
            for table, column, ref_table, ref_column in fk_checks:
                issues.extend(cls._check_foreign_keys(table, column, ref_table, ref_column))
            
            return issues

        except Exception as e:
            logger.error(f"Error verifying schema integrity: {str(e)}")
            raise DatabaseError(f"Failed to verify schema integrity: {str(e)}")

    @classmethod
    def _check_table_structure(
        cls,
        table_name: str,
        required_columns: List[str]
    ) -> List[Dict[str, Any]]:
        """Check table existence and required columns"""
        issues = []
        
        try:
            # Check if table exists
            query = """
                SELECT EXISTS (
                    SELECT 1 
                    FROM information_schema.tables 
                    WHERE table_name = %s
                );
            """
            table_exists = DatabaseManager.execute_query(query, (table_name,))[0]['exists']
            
            if not table_exists:
                issues.append({
                    'type': 'missing_table',
                    'object': table_name,
                    'description': f"Table {table_name} does not exist"
                })
                return issues

            # Check columns
            query = """
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = %s;
            """
            columns = DatabaseManager.execute_query(query, (table_name,))
            existing_columns = {col['column_name'] for col in columns}
            
            for required_col in required_columns:
                if required_col not in existing_columns:
                    issues.append({
                        'type': 'missing_column',
                        'object': f"{table_name}.{required_col}",
                        'description': f"Required column {required_col} missing in {table_name}"
                    })
            
            return issues

        except Exception as e:
            logger.error(f"Error checking table structure: {str(e)}")
            raise DatabaseError(f"Failed to check table structure: {str(e)}")

    @classmethod
    def _check_foreign_keys(
        cls,
        table: str,
        column: str,
        ref_table: str,
        ref_column: str
    ) -> List[Dict[str, Any]]:
        """Check foreign key constraints and data integrity"""
        issues = []
        
        try:
            # Check for orphaned records
            query = f"""
                SELECT t1.{column} 
                FROM {table} t1
                LEFT JOIN {ref_table} t2 ON t1.{column} = t2.{ref_column}
                WHERE t1.{column} IS NOT NULL
                AND t2.{ref_column} IS NULL;
            """
            orphaned = DatabaseManager.execute_query(query)
            
            if orphaned:
                issues.append({
                    'type': 'orphaned_records',
                    'object': f"{table}.{column}",
                    'description': f"Found {len(orphaned)} orphaned records referencing {ref_table}.{ref_column}",
                    'details': orphaned
                })
            
            return issues

        except Exception as e:
            logger.error(f"Error checking foreign keys: {str(e)}")
            raise DatabaseError(f"Failed to check foreign keys: {str(e)}")

    @classmethod
    def create_schema_backup(cls) -> str:
        """Create a backup of the current schema"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"schema_backup_{timestamp}.sql"
            
            # Get schema definition
            query = """
                SELECT 
                    table_name,
                    column_name,
                    data_type,
                    column_default,
                    is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public'
                ORDER BY table_name, ordinal_position;
            """
            
            schema = DatabaseManager.execute_query(query)
            
            # Generate CREATE TABLE statements
            current_table = None
            create_statements = []
            columns = []
            
            for col in schema:
                if col['table_name'] != current_table:
                    if columns:
                        create_statements.append(
                            f"CREATE TABLE {current_table} (\n"
                            f"    {',\n    '.join(columns)}\n"
                            ");"
                        )
                    current_table = col['table_name']
                    columns = []
                
                nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                default = f"DEFAULT {col['column_default']}" if col['column_default'] else ""
                
                columns.append(
                    f"{col['column_name']} {col['data_type']} {nullable} {default}".strip()
                )
            
            # Add last table
            if columns:
                create_statements.append(
                    f"CREATE TABLE {current_table} (\n"
                    f"    {',\n    '.join(columns)}\n"
                    ");"
                )
            
            # Write backup file
            with open(backup_name, 'w') as f:
                f.write("\n\n".join(create_statements))
            
            logger.info(f"Schema backup created: {backup_name}")
            return backup_name

        except Exception as e:
            logger.error(f"Error creating schema backup: {str(e)}")
            raise DatabaseError(f"Failed to create schema backup: {str(e)}")