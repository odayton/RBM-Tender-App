"""
Migration Management Utility

This module provides robust migration management capabilities including:
- Migration validation and safety checks
- Automatic backups before migrations
- Rollback capabilities
- Migration status monitoring
- Error recovery
"""

import os
import sys
import logging
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

class MigrationManager:
    """Comprehensive migration management utility."""
    
    def __init__(self, app=None, db=None):
        self.app = app
        self.db = db
        
        # Get the project root directory (where migrations folder is located)
        if app:
            # If we have an app, use its root path
            project_root = Path(app.root_path).parent
        else:
            # Try to find the project root by looking for migrations directory
            current_dir = Path.cwd()
            project_root = None
            
            # Walk up the directory tree to find the migrations folder
            for parent in [current_dir] + list(current_dir.parents):
                if (parent / "migrations").exists():
                    project_root = parent
                    break
            
            if not project_root:
                # Fallback: assume we're in the project root
                project_root = current_dir
        
        self.migrations_dir = project_root / "migrations"
        self.backups_dir = self.migrations_dir / "backups"
        
        # Ensure the backups directory exists
        try:
            self.backups_dir.mkdir(exist_ok=True)
        except FileNotFoundError:
            # If the parent directory doesn't exist, create the full path
            self.backups_dir.mkdir(parents=True, exist_ok=True)
        
    def init_app(self, app, db):
        """Initialize the migration manager with Flask app and database."""
        self.app = app
        self.db = db
        
    def get_current_version(self) -> Optional[str]:
        """Get the current migration version from the database."""
        try:
            with self.db.engine.connect() as conn:
                result = conn.execute(text("SELECT version_num FROM alembic_version"))
                row = result.fetchone()
                return row[0] if row else None
        except SQLAlchemyError as e:
            logger.error(f"Failed to get current version: {e}")
            return None
            
    def get_migration_history(self) -> List[Dict]:
        """Get the migration history from the database."""
        try:
            with self.db.engine.connect() as conn:
                # Check if version_locations column exists
                inspector = inspect(self.db.engine)
                columns = [col['name'] for col in inspector.get_columns('alembic_version')]
                
                if 'version_locations' in columns:
                    result = conn.execute(text("""
                        SELECT version_num, version_locations 
                        FROM alembic_version 
                        ORDER BY version_num
                    """))
                    return [{"version": row[0], "location": row[1]} for row in result.fetchall()]
                else:
                    # Fallback for older schema
                    result = conn.execute(text("""
                        SELECT version_num 
                        FROM alembic_version 
                        ORDER BY version_num
                    """))
                    return [{"version": row[0], "location": "Unknown"} for row in result.fetchall()]
        except SQLAlchemyError as e:
            logger.error(f"Failed to get migration history: {e}")
            return []
            
    def validate_migration_files(self) -> Tuple[bool, List[str]]:
        """Validate that all migration files are present and valid."""
        errors = []
        
        try:
            # Get all migration files
            versions_dir = self.migrations_dir / "versions"
            if not versions_dir.exists():
                errors.append("Migrations versions directory not found")
                return False, errors
                
            migration_files = list(versions_dir.glob("*.py"))
            if not migration_files:
                errors.append("No migration files found")
                return False, errors
                
            # Check each migration file
            for migration_file in sorted(migration_files):
                try:
                    # Try different encodings to handle encoding issues
                    content = None
                    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
                    
                    for encoding in encodings:
                        try:
                            with open(migration_file, 'r', encoding=encoding) as f:
                                content = f.read()
                            break
                        except UnicodeDecodeError:
                            continue
                    
                    if content is None:
                        errors.append(f"Could not read migration file {migration_file.name} with any encoding")
                        continue
                        
                    # Basic validation
                    if 'revision =' not in content:
                        errors.append(f"Invalid migration file: {migration_file.name}")
                    if 'def upgrade()' not in content:
                        errors.append(f"Missing upgrade function in: {migration_file.name}")
                    if 'def downgrade()' not in content:
                        errors.append(f"Missing downgrade function in: {migration_file.name}")
                        
                except Exception as e:
                    errors.append(f"Error reading migration file {migration_file.name}: {e}")
                    
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Error validating migration files: {e}")
            return False, errors
            
    def create_backup(self, description: str = "") -> Optional[str]:
        """Create a backup of the database."""
        try:
            # Get database file path
            db_url = str(self.db.engine.url)
            
            # For PostgreSQL, we'll use pg_dump for backups
            if 'postgresql' in db_url:
                # Create backup filename with timestamp and description
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                desc_suffix = f"_{description.replace(' ', '_')}" if description else ""
                backup_name = f"backup_{timestamp}{desc_suffix}_postgres.sql"
                backup_path = self.backups_dir / backup_name
                
                # Use pg_dump to create backup
                import subprocess
                import os
                
                # Parse connection details from URL
                # Format: postgresql://user:password@host:port/database
                url_parts = db_url.replace('postgresql://', '').split('@')
                if len(url_parts) == 2:
                    credentials = url_parts[0].split(':')
                    host_port_db = url_parts[1].split('/')
                    
                    user = credentials[0]
                    password = credentials[1]
                    host_port = host_port_db[0].split(':')
                    host = host_port[0]
                    port = host_port[1] if len(host_port) > 1 else '5432'
                    database = host_port_db[1]
                    
                    # Set environment variable for password
                    env = os.environ.copy()
                    env['PGPASSWORD'] = password
                    
                    # Run pg_dump
                    cmd = ['pg_dump', '-U', user, '-h', host, '-p', port, '-d', database, '-f', str(backup_path)]
                    result = subprocess.run(cmd, env=env, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        logger.info(f"PostgreSQL backup created: {backup_path}")
                        return str(backup_path)
                    else:
                        logger.error(f"pg_dump failed: {result.stderr}")
                        
            logger.info("Database backup skipped (PostgreSQL backup failed or unsupported database)")
            return None
            
        except Exception as e:
            logger.error(f"Failed to create database backup: {e}")
            return None
            
    def restore_backup(self, backup_path: str) -> bool:
        """Restore database from a backup."""
        try:
            if not os.path.exists(backup_path):
                logger.error(f"Backup file not found: {backup_path}")
                return False
                
            # Get current database URL
            db_url = str(self.db.engine.url)
            if 'postgresql' in db_url:
                # Parse connection details from URL
                url_parts = db_url.replace('postgresql://', '').split('@')
                if len(url_parts) == 2:
                    credentials = url_parts[0].split(':')
                    host_port_db = url_parts[1].split('/')
                    
                    user = credentials[0]
                    password = credentials[1]
                    host_port = host_port_db[0].split(':')
                    host = host_port[0]
                    port = host_port[1] if len(host_port) > 1 else '5432'
                    database = host_port_db[1]
                    
                    # Set environment variable for password
                    env = os.environ.copy()
                    env['PGPASSWORD'] = password
                    
                    # Run psql to restore backup
                    cmd = ['psql', '-U', user, '-h', host, '-p', port, '-d', database, '-f', backup_path]
                    result = subprocess.run(cmd, env=env, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        logger.info(f"PostgreSQL database restored from backup: {backup_path}")
                        return True
                    else:
                        logger.error(f"psql restore failed: {result.stderr}")
                        
            logger.error("Restore only supported for PostgreSQL databases")
            return False
            
        except Exception as e:
            logger.error(f"Failed to restore database: {e}")
            return False
            
    def run_migration_command(self, command: str, args: List[str] = None) -> Tuple[bool, str]:
        """Run a migration command using Flask-Migrate."""
        try:
            cmd = ["flask", "db", command]
            if args:
                cmd.extend(args)
                
            logger.info(f"Running command: {' '.join(cmd)}")
            
            # Run the command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
                env=os.environ.copy()
            )
            
            if result.returncode == 0:
                logger.info(f"Command '{command}' completed successfully")
                return True, result.stdout
            else:
                logger.error(f"Command '{command}' failed: {result.stderr}")
                return False, result.stderr
                
        except Exception as e:
            logger.error(f"Error running migration command: {e}")
            return False, str(e)
            
    def migrate(self, message: str = "", create_backup: bool = True) -> bool:
        """Run database migrations with safety checks."""
        try:
            logger.info("Starting migration process...")
            
            # Validate migration files
            is_valid, errors = self.validate_migration_files()
            if not is_valid:
                logger.error("Migration validation failed:")
                for error in errors:
                    logger.error(f"  - {error}")
                return False
                
            # Create backup if requested
            backup_path = None
            if create_backup:
                backup_path = self.create_backup(f"before_migration_{message}")
                
            # Check current status
            current_version = self.get_current_version()
            logger.info(f"Current migration version: {current_version}")
            
            # Run migration
            success, output = self.run_migration_command("upgrade")
            if not success:
                logger.error("Migration failed")
                if backup_path and os.path.exists(backup_path):
                    logger.info("Backup available for manual restore if needed")
                return False
                
            # Verify migration
            new_version = self.get_current_version()
            logger.info(f"New migration version: {new_version}")
            
            if new_version != current_version:
                logger.info("Migration completed successfully")
                return True
            else:
                logger.info("No new migrations to apply")
                return True
                
        except Exception as e:
            logger.error(f"Migration process failed: {e}")
            return False
            
    def rollback(self, target_revision: str = None, backup_path: str = None) -> bool:
        """Rollback to a specific migration version."""
        try:
            logger.info("Starting rollback process...")
            
            current_version = self.get_current_version()
            logger.info(f"Current version: {current_version}")
            
            if target_revision:
                logger.info(f"Target version: {target_revision}")
                success, output = self.run_migration_command("downgrade", [target_revision])
            else:
                # Rollback one step
                # Get the previous revision
                history = self.get_migration_history()
                if len(history) > 1:
                    previous_revision = history[-2]['version']  # Get the second-to-last revision
                    success, output = self.run_migration_command("downgrade", [previous_revision])
                else:
                    logger.error("No previous revision to rollback to")
                    return False
                
            if not success:
                logger.error("Rollback failed")
                return False
                
            new_version = self.get_current_version()
            logger.info(f"New version after rollback: {new_version}")
            
            logger.info("Rollback completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Rollback process failed: {e}")
            return False
            
    def create_migration(self, message: str) -> bool:
        """Create a new migration."""
        try:
            logger.info(f"Creating new migration: {message}")
            
            success, output = self.run_migration_command("revision", ["--autogenerate", "-m", message])
            if not success:
                logger.error("Failed to create migration")
                return False
                
            logger.info("Migration created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating migration: {e}")
            return False
            
    def get_migration_status(self) -> Dict:
        """Get comprehensive migration status."""
        try:
            current_version = self.get_current_version()
            history = self.get_migration_history()
            is_valid, errors = self.validate_migration_files()
            
            # Get available migrations
            versions_dir = self.migrations_dir / "versions"
            available_migrations = []
            if versions_dir.exists():
                for migration_file in sorted(versions_dir.glob("*.py")):
                    available_migrations.append(migration_file.stem)
                    
            return {
                "current_version": current_version,
                "migration_history": history,
                "files_valid": is_valid,
                "validation_errors": errors,
                "available_migrations": available_migrations,
                "backups_count": len(list(self.backups_dir.glob("*.db"))) if self.backups_dir.exists() else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting migration status: {e}")
            return {
                "error": str(e),
                "current_version": None,
                "migration_history": [],
                "files_valid": False,
                "validation_errors": [str(e)],
                "available_migrations": [],
                "backups_count": 0
            }
            
    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """Clean up old backup files, keeping the most recent ones."""
        try:
            if not self.backups_dir.exists():
                return 0
                
            # Get all backup files sorted by modification time
            backup_files = []
            for backup_file in self.backups_dir.glob("*.db"):
                backup_files.append((backup_file, backup_file.stat().st_mtime))
                
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # Remove old backups
            removed_count = 0
            for backup_file, _ in backup_files[keep_count:]:
                backup_file.unlink()
                removed_count += 1
                logger.info(f"Removed old backup: {backup_file.name}")
                
            if removed_count > 0:
                logger.info(f"Cleaned up {removed_count} old backup files")
                
            return removed_count
            
        except Exception as e:
            logger.error(f"Error cleaning up backups: {e}")
            return 0

# Global migration manager instance
migration_manager = MigrationManager() 