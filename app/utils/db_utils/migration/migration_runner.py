from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
from app.core.core_database import DatabaseManager, DatabaseError
from .schema_manager import SchemaManager
from .version_control import VersionControl
from app.core.core_logging import logger # Use central app logger

class MigrationRunner:
    """Executes database migrations and manages the migration process."""

    def __init__(self):
        self.schema_manager = SchemaManager()
        self.version_control = VersionControl()

    def run_pending_migrations(self, dry_run: bool = False) -> List[Dict[str, Any]]:
        """Run all pending migrations."""
        logger.info(f"Checking for pending migrations... (Dry Run: {dry_run})")
        try:
            self.version_control.initialize()
            
            pending = self.version_control.get_pending_migrations()
            if not pending:
                logger.info("No pending migrations found.")
                return []

            logger.info(f"Found {len(pending)} pending migrations.")
            results = []
            for migration in pending:
                version = migration['version']
                try:
                    if dry_run:
                        logger.info(f"[DRY RUN] Would apply migration: {version}")
                        results.append({'version': version, 'status': 'dry_run_skipped'})
                        continue

                    backup_path = self.schema_manager.create_schema_backup()
                    logger.info(f"Created schema backup before applying migration {version}: {backup_path}")

                    self._apply_migration(migration)
                    results.append({'version': version, 'status': 'success', 'backup': backup_path})

                except Exception as e:
                    error_msg = f"Migration {version} failed: {e}"
                    logger.error(error_msg, exc_info=True)
                    results.append({'version': version, 'status': 'failed', 'error': error_msg})
                    # Stop processing further migrations on failure
                    break
            
            return results

        except Exception as e:
            logger.error(f"Error running migrations: {e}", exc_info=True)
            raise DatabaseError(f"Failed to run migrations: {e}")

    def rollback_migration(self, version: int) -> Dict[str, Any]:
        """Rollback a specific migration."""
        logger.info(f"Attempting to roll back migration version: {version}")
        try:
            query = "SELECT * FROM migrations WHERE version = %s AND status = 'success'"
            migration = DatabaseManager.execute_query(query, (version,))
            
            if not migration:
                raise ValueError(f"Migration version {version} not found or was not applied successfully.")
            
            migration = migration[0]
            
            backup_path = self.schema_manager.create_schema_backup()
            logger.info(f"Created schema backup before rollback: {backup_path}")
            
            rollback_path = Path(migration['script_path']).parent / f"R{version}_rollback.sql"
            if not rollback_path.exists():
                raise FileNotFoundError(f"Rollback script not found: {rollback_path}")
            
            with DatabaseManager.transaction():
                with rollback_path.open() as f:
                    rollback_sql = f.read()
                    DatabaseManager.execute_query(rollback_sql)
                
                self.version_control.record_migration_result(version, 'rolled_back', None)
            
            logger.info(f"Successfully rolled back migration version {version}.")
            return {'version': version, 'status': 'rolled_back', 'backup': backup_path}

        except Exception as e:
            error_msg = f"Rollback for version {version} failed: {e}"
            logger.error(error_msg, exc_info=True)
            return {'version': version, 'status': 'rollback_failed', 'error': error_msg}

    def _apply_migration(self, migration: Dict[str, Any]) -> None:
        """Apply a single migration within a transaction."""
        version = migration['version']
        script_path = Path(migration['script_path'])
        
        logger.info(f"Applying migration {version} from script: {script_path}")
        try:
            if not script_path.exists():
                raise FileNotFoundError(f"Migration script not found: {script_path}")
            
            current_checksum = self.version_control._calculate_checksum(script_path)
            if current_checksum != migration['checksum']:
                raise ValueError(f"Checksum mismatch for migration script: {script_path}. File may have been altered.")
            
            with DatabaseManager.transaction():
                with script_path.open() as f:
                    migration_sql = f.read()
                    DatabaseManager.execute_query(migration_sql)
                
                self.version_control.record_migration_result(version, 'success', None)
            
            logger.info(f"Successfully applied migration {version}")

        except Exception as e:
            logger.error(f"Error applying migration {version}: {e}", exc_info=True)
            self.version_control.record_migration_result(version, 'failed', str(e))
            raise # Re-raise to be caught by the main loop

    def get_migration_status(self) -> Dict[str, Any]:
        """Get current migration status."""
        try:
            pending = self.version_control.get_pending_migrations()
            history = self.version_control.get_migration_history()
            current_version = self.version_control.get_latest_version()
            
            return {
                'current_version': current_version,
                'pending_count': len(pending),
                'total_migrations': len(history),
                'failed_migrations': len([m for m in history if m['status'] == 'failed']),
                'last_migration': next((m for m in history if m['status'] == 'success'), None),
                'pending_migrations': pending
            }
        except Exception as e:
            logger.error(f"Error getting migration status: {e}", exc_info=True)
            raise DatabaseError(f"Failed to get migration status: {e}")

    # Other methods like verify_database_state and generate_migration_report are unchanged
    # as they already delegate logic and their logging will be handled by the callee.