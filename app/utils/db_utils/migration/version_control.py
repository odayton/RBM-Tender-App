# app/utils/db_utils/migration/version_control.py

from typing import Dict, List, Any, Optional, Tuple
import logging
import hashlib
from pathlib import Path
from datetime import datetime
import re
from app.core.core_database import DatabaseManager, DatabaseError

logger = logging.getLogger(__name__)

class VersionControl:
    """Manages database version control and migration scripts"""

    MIGRATION_PATH = Path(__file__).parent.parent / 'migrations'
    VERSION_PATTERN = re.compile(r'V(\d+)__(.+)\.sql')

    @classmethod
    def initialize(cls) -> None:
        """Initialize version control system"""
        try:
            # Ensure migrations directory exists
            cls.MIGRATION_PATH.mkdir(parents=True, exist_ok=True)
            
            # Create migrations table if it doesn't exist
            query = """
                CREATE TABLE IF NOT EXISTS migrations (
                    version INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    script_path TEXT NOT NULL,
                    checksum TEXT NOT NULL,
                    applied_at TIMESTAMP,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pending',
                    error_message TEXT
                );
            """
            DatabaseManager.execute_query(query)
            logger.info("Version control system initialized")

        except Exception as e:
            logger.error(f"Error initializing version control: {str(e)}")
            raise DatabaseError(f"Failed to initialize version control: {str(e)}")

    @classmethod
    def create_migration(cls, name: str, description: Optional[str] = None) -> Path:
        """Create a new migration script"""
        try:
            # Get next version number
            current_version = cls.get_latest_version()
            next_version = current_version + 1
            
            # Create migration file name
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            script_name = f"V{next_version}__{name}.sql"
            script_path = cls.MIGRATION_PATH / script_name
            
            # Create migration file with template
            template = f"""-- Migration: {name}
-- Version: {next_version}
-- Created: {timestamp}
-- Description: {description or 'No description provided'}

-- Write your migration SQL here
BEGIN;

-- Your SQL statements here

COMMIT;

-- Rollback SQL here (if needed)
--ROLLBACK;
"""
            
            script_path.write_text(template)
            
            # Record migration
            checksum = cls._calculate_checksum(script_path)
            query = """
                INSERT INTO migrations 
                (version, name, description, script_path, checksum)
                VALUES (%s, %s, %s, %s, %s)
            """
            params = (next_version, name, description, str(script_path), checksum)
            DatabaseManager.execute_query(query, params)
            
            logger.info(f"Created migration script: {script_path}")
            return script_path

        except Exception as e:
            logger.error(f"Error creating migration: {str(e)}")
            raise DatabaseError(f"Failed to create migration: {str(e)}")

    @classmethod
    def get_latest_version(cls) -> int:
        """Get the latest migration version"""
        try:
            query = """
                SELECT COALESCE(MAX(version), 0) as version 
                FROM migrations
                WHERE status = 'success'
            """
            result = DatabaseManager.execute_query(query)
            return result[0]['version']

        except Exception as e:
            logger.error(f"Error getting latest version: {str(e)}")
            raise DatabaseError(f"Failed to get latest version: {str(e)}")

    @classmethod
    def get_pending_migrations(cls) -> List[Dict[str, Any]]:
        """Get list of pending migrations"""
        try:
            query = """
                SELECT * 
                FROM migrations 
                WHERE status = 'pending'
                ORDER BY version ASC
            """
            return DatabaseManager.execute_query(query)

        except Exception as e:
            logger.error(f"Error getting pending migrations: {str(e)}")
            raise DatabaseError(f"Failed to get pending migrations: {str(e)}")

    @classmethod
    def verify_migrations(cls) -> List[Dict[str, str]]:
        """
        Verify integrity of migration scripts.
        Checks for:
        - Missing scripts
        - Checksum mismatches
        - Script content validity
        - Version sequence integrity
        - Naming convention compliance
        - SQL syntax validation
        """
        try:
            issues = []
            
            # Get all recorded migrations
            query = """
                SELECT 
                    version,
                    name,
                    description,
                    script_path,
                    checksum,
                    status,
                    applied_at
                FROM migrations
                ORDER BY version ASC
            """
            migrations = DatabaseManager.execute_query(query)

            # Get list of files in migrations directory
            migration_files = list(cls.MIGRATION_PATH.glob('V*__.sql'))
            recorded_paths = {Path(m['script_path']) for m in migrations}
            existing_files = set(migration_files)

            # Check for unrecorded migration files
            unrecorded_files = existing_files - recorded_paths
            for file in unrecorded_files:
                issues.append({
                    'version': 'unknown',
                    'type': 'unrecorded_script',
                    'description': f"Migration script exists but is not recorded: {file}"
                })

            # Verify each recorded migration
            last_version = 0
            for migration in migrations:
                script_path = Path(migration['script_path'])
                version = migration['version']

                # Check file existence
                if not script_path.exists():
                    issues.append({
                        'version': version,
                        'type': 'missing_script',
                        'description': f"Migration script not found: {script_path}"
                    })
                    continue

                # Check version sequence
                if version != last_version + 1:
                    issues.append({
                        'version': version,
                        'type': 'version_gap',
                        'description': f"Version sequence gap: Expected {last_version + 1}, found {version}"
                    })
                last_version = version

                # Verify file naming convention
                if not cls.VERSION_PATTERN.match(script_path.name):
                    issues.append({
                        'version': version,
                        'type': 'invalid_naming',
                        'description': f"Invalid migration file name format: {script_path.name}"
                    })

                # Check checksum
                current_checksum = cls._calculate_checksum(script_path)
                if current_checksum != migration['checksum']:
                    issues.append({
                        'version': version,
                        'type': 'checksum_mismatch',
                        'description': f"Checksum mismatch for {script_path}"
                    })

                # Validate SQL syntax and structure
                try:
                    sql_content = script_path.read_text()
                    
                    # Check for transaction blocks
                    if 'BEGIN' not in sql_content.upper() or 'COMMIT' not in sql_content.upper():
                        issues.append({
                            'version': version,
                            'type': 'missing_transaction',
                            'description': f"Missing transaction blocks in {script_path.name}"
                        })

                    # Check for dangerous operations
                    dangerous_operations = ['DROP DATABASE', 'TRUNCATE', 'DELETE FROM', 'DROP TABLE']
                    for operation in dangerous_operations:
                        if operation.upper() in sql_content.upper():
                            issues.append({
                                'version': version,
                                'type': 'dangerous_operation',
                                'description': f"Potentially dangerous operation '{operation}' found in {script_path.name}"
                            })

                    # Validate basic SQL syntax
                    try:
                        DatabaseManager.execute_query(
                            f"EXPLAIN {sql_content}",
                            dry_run=True
                        )
                    except Exception as e:
                        issues.append({
                            'version': version,
                            'type': 'invalid_sql',
                            'description': f"SQL syntax error in {script_path.name}: {str(e)}"
                        })

                except Exception as e:
                    issues.append({
                        'version': version,
                        'type': 'read_error',
                        'description': f"Error reading or parsing {script_path.name}: {str(e)}"
                    })

                # Check applied migrations order
                if migration['status'] == 'success' and migration['applied_at']:
                    query = """
                        SELECT version, applied_at
                        FROM migrations
                        WHERE version < %s
                            AND status = 'success'
                            AND applied_at > %s
                    """
                    out_of_order = DatabaseManager.execute_query(
                        query,
                        (version, migration['applied_at'])
                    )
                    
                    if out_of_order:
                        issues.append({
                            'version': version,
                            'type': 'invalid_order',
                            'description': f"Migration {version} was applied after some lower versions"
                        })

            # Check for duplicate versions
            version_counts = {}
            for migration in migrations:
                version = migration['version']
                version_counts[version] = version_counts.get(version, 0) + 1
                
            for version, count in version_counts.items():
                if count > 1:
                    issues.append({
                        'version': version,
                        'type': 'duplicate_version',
                        'description': f"Multiple migrations found for version {version}"
                    })

            return issues

        except Exception as e:
            logger.error(f"Error verifying migrations: {str(e)}")
            raise DatabaseError(f"Failed to verify migrations: {str(e)}")
        
    @classmethod
    def record_migration_result(
        cls,
        version: int,
        status: str,
        error_message: Optional[str] = None
    ) -> None:
        """Record the result of a migration attempt"""
        try:
            query = """
                UPDATE migrations 
                SET status = %s,
                    applied_at = CASE WHEN %s = 'success' THEN CURRENT_TIMESTAMP ELSE NULL END,
                    error_message = %s
                WHERE version = %s
            """
            params = (status, status, error_message, version)
            DatabaseManager.execute_query(query, params)
            
            logger.info(f"Recorded migration result for version {version}: {status}")

        except Exception as e:
            logger.error(f"Error recording migration result: {str(e)}")
            raise DatabaseError(f"Failed to record migration result: {str(e)}")

    @classmethod
    def get_migration_history(cls) -> List[Dict[str, Any]]:
        """Get complete migration history"""
        try:
            query = """
                SELECT *
                FROM migrations
                ORDER BY version DESC
            """
            return DatabaseManager.execute_query(query)

        except Exception as e:
            logger.error(f"Error getting migration history: {str(e)}")
            raise DatabaseError(f"Failed to get migration history: {str(e)}")

    @classmethod
    def _calculate_checksum(cls, file_path: Path) -> str:
        """Calculate SHA-256 checksum of a file"""
        sha256_hash = hashlib.sha256()
        content = file_path.read_bytes()
        sha256_hash.update(content)
        return sha256_hash.hexdigest()

    @classmethod
    def create_rollback_script(cls, version: int) -> Path:
        """Create a rollback script for a specific version"""
        try:
            query = "SELECT * FROM migrations WHERE version = %s"
            migration = DatabaseManager.execute_query(query, (version,))
            
            if not migration:
                raise ValueError(f"Migration version {version} not found")
                
            migration = migration[0]
            rollback_name = f"R{version}__{migration['name']}_rollback.sql"
            rollback_path = cls.MIGRATION_PATH / rollback_name
            
            template = f"""-- Rollback for Migration: {migration['name']}
-- Version: {version}
-- Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- Description: Rollback script for {migration['description']}

BEGIN;

-- Write your rollback SQL here

COMMIT;
"""
            
            rollback_path.write_text(template)
            logger.info(f"Created rollback script: {rollback_path}")
            return rollback_path

        except Exception as e:
            logger.error(f"Error creating rollback script: {str(e)}")
            raise DatabaseError(f"Failed to create rollback script: {str(e)}")

    @classmethod
    def validate_migration_order(cls) -> List[Dict[str, str]]:
        """Validate the order and sequence of migrations"""
        try:
            issues = []
            migrations = cls.get_migration_history()
            
            # Check for version gaps
            versions = [m['version'] for m in migrations]
            expected_versions = set(range(1, max(versions) + 1))
            missing_versions = expected_versions - set(versions)
            
            if missing_versions:
                issues.append({
                    'type': 'missing_versions',
                    'description': f"Missing migration versions: {sorted(missing_versions)}"
                })
            
            # Check for duplicate versions
            version_counts = {}
            for m in migrations:
                version_counts[m['version']] = version_counts.get(m['version'], 0) + 1
                
            duplicates = {v: c for v, c in version_counts.items() if c > 1}
            if duplicates:
                issues.append({
                    'type': 'duplicate_versions',
                    'description': f"Duplicate migration versions found: {duplicates}"
                })
            
            # Check application order
            successful_migrations = [
                m for m in migrations 
                if m['status'] == 'success' and m['applied_at'] is not None
            ]
            
            for i in range(len(successful_migrations) - 1):
                current = successful_migrations[i]
                next_migration = successful_migrations[i + 1]
                
                if current['applied_at'] < next_migration['applied_at'] and \
                   current['version'] > next_migration['version']:
                    issues.append({
                        'type': 'invalid_order',
                        'description': f"Migration {current['version']} was applied before {next_migration['version']}"
                    })
            
            return issues

        except Exception as e:
            logger.error(f"Error validating migration order: {str(e)}")
            raise DatabaseError(f"Failed to validate migration order: {str(e)}")