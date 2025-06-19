# app/utils/db_utils/migration/migration_runner.py

from typing import Dict, List, Any, Optional, Union
import logging
from datetime import datetime
from pathlib import Path
from app.core.core_database import DatabaseManager, DatabaseError
from .schema_manager import SchemaManager
from .version_control import VersionControl

logger = logging.getLogger(__name__)

class MigrationRunner:
    """Executes database migrations and manages the migration process"""

    def __init__(self):
        self.schema_manager = SchemaManager()
        self.version_control = VersionControl()

    def run_pending_migrations(self, dry_run: bool = False) -> List[Dict[str, Any]]:
        """Run all pending migrations"""
        try:
            # Initialize version control if needed
            self.version_control.initialize()
            
            # Get pending migrations
            pending = self.version_control.get_pending_migrations()
            if not pending:
                logger.info("No pending migrations found")
                return []

            results = []
            for migration in pending:
                try:
                    if dry_run:
                        logger.info(f"[DRY RUN] Would apply migration: {migration['version']}")
                        continue

                    # Create schema backup before migration
                    backup_path = self.schema_manager.create_schema_backup()
                    logger.info(f"Created schema backup: {backup_path}")

                    # Apply migration
                    self._apply_migration(migration)
                    results.append({
                        'version': migration['version'],
                        'status': 'success',
                        'backup': backup_path
                    })

                except Exception as e:
                    error_msg = f"Migration {migration['version']} failed: {str(e)}"
                    logger.error(error_msg)
                    results.append({
                        'version': migration['version'],
                        'status': 'failed',
                        'error': error_msg
                    })
                    break

            return results

        except Exception as e:
            logger.error(f"Error running migrations: {str(e)}")
            raise DatabaseError(f"Failed to run migrations: {str(e)}")

    def rollback_migration(self, version: int) -> Dict[str, Any]:
        """Rollback a specific migration"""
        try:
            # Verify migration exists and was applied
            query = """
                SELECT * FROM migrations 
                WHERE version = %s AND status = 'success'
            """
            migration = DatabaseManager.execute_query(query, (version,))
            
            if not migration:
                raise ValueError(f"Migration version {version} not found or not applied")
            
            migration = migration[0]
            
            # Create backup before rollback
            backup_path = self.schema_manager.create_schema_backup()
            logger.info(f"Created schema backup before rollback: {backup_path}")
            
            # Find rollback script
            rollback_path = Path(migration['script_path']).parent / f"R{version}_rollback.sql"
            if not rollback_path.exists():
                raise FileNotFoundError(f"Rollback script not found: {rollback_path}")
            
            # Execute rollback
            with DatabaseManager.transaction() as conn:
                with rollback_path.open() as f:
                    rollback_sql = f.read()
                    DatabaseManager.execute_query(rollback_sql)
                
                # Update migration status
                self.version_control.record_migration_result(
                    version,
                    'rolled_back',
                    None
                )
            
            return {
                'version': version,
                'status': 'rolled_back',
                'backup': backup_path
            }

        except Exception as e:
            error_msg = f"Rollback failed: {str(e)}"
            logger.error(error_msg)
            return {
                'version': version,
                'status': 'rollback_failed',
                'error': error_msg
            }

    def _apply_migration(self, migration: Dict[str, Any]) -> None:
        """Apply a single migration"""
        try:
            script_path = Path(migration['script_path'])
            if not script_path.exists():
                raise FileNotFoundError(f"Migration script not found: {script_path}")
            
            # Verify script hasn't been modified
            current_checksum = self.version_control._calculate_checksum(script_path)
            if current_checksum != migration['checksum']:
                raise ValueError(f"Migration script checksum mismatch: {script_path}")
            
            # Execute migration
            with DatabaseManager.transaction() as conn:
                with script_path.open() as f:
                    migration_sql = f.read()
                    DatabaseManager.execute_query(migration_sql)
                
                # Record successful migration
                self.version_control.record_migration_result(
                    migration['version'],
                    'success',
                    None
                )
            
            logger.info(f"Successfully applied migration {migration['version']}")

        except Exception as e:
            logger.error(f"Error applying migration: {str(e)}")
            self.version_control.record_migration_result(
                migration['version'],
                'failed',
                str(e)
            )
            raise

    def get_migration_status(self) -> Dict[str, Any]:
        """Get current migration status"""
        try:
            pending = self.version_control.get_pending_migrations()
            history = self.version_control.get_migration_history()
            current_version = self.version_control.get_latest_version()
            
            return {
                'current_version': current_version,
                'pending_count': len(pending),
                'total_migrations': len(history),
                'failed_migrations': len([m for m in history if m['status'] == 'failed']),
                'last_migration': next(
                    (m for m in history if m['status'] == 'success'),
                    None
                ),
                'pending_migrations': pending
            }

        except Exception as e:
            logger.error(f"Error getting migration status: {str(e)}")
            raise DatabaseError(f"Failed to get migration status: {str(e)}")

    def verify_database_state(self) -> List[Dict[str, str]]:
        """Verify overall database state"""
        try:
            issues = []
            
            # Check schema integrity
            schema_issues = self.schema_manager.verify_schema_integrity()
            if schema_issues:
                issues.extend(schema_issues)
            
            # Verify migration scripts
            migration_issues = self.version_control.verify_migrations()
            if migration_issues:
                issues.extend(migration_issues)
            
            # Check migration order
            order_issues = self.version_control.validate_migration_order()
            if order_issues:
                issues.extend(order_issues)
            
            return issues

        except Exception as e:
            logger.error(f"Error verifying database state: {str(e)}")
            raise DatabaseError(f"Failed to verify database state: {str(e)}")

    def generate_migration_report(self) -> Dict[str, Any]:
        """Generate comprehensive migration report"""
        try:
            status = self.get_migration_status()
            issues = self.verify_database_state()
            history = self.version_control.get_migration_history()
            
            return {
                'status': status,
                'issues': issues,
                'history': history,
                'generated_at': datetime.now().isoformat(),
                'database_schema_version': self.schema_manager.get_current_version()
            }

        except Exception as e:
            logger.error(f"Error generating migration report: {str(e)}")
            raise DatabaseError(f"Failed to generate migration report: {str(e)}")