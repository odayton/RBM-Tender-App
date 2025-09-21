"""
Core Database Safety Module - Schema Validation, Backup Verification, and Safety Protocols
"""

import os
import json
import hashlib
import shutil
import subprocess
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import structlog
from sqlalchemy import text, inspect, MetaData
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

logger = structlog.get_logger(__name__)

class DatabaseSchemaValidator:
    """Validates database schema changes and integrity."""
    
    def __init__(self, db):
        self.db = db
        self.engine = db.engine
        self.metadata = MetaData()
        self.schema_snapshots = {}
        self.validation_rules = self._load_validation_rules()
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load database validation rules."""
        return {
            'required_tables': [
                'users', 'roles', 'user_roles', 'deals', 'companies', 'contacts',
                'quotes', 'quote_options', 'quote_line_items', 'products',
                'quote_recipients', 'quote_snapshots'
            ],
            'critical_columns': {
                'users': ['id', 'email', 'password_hash', 'is_active'],
                'deals': ['id', 'project_name', 'deal_type', 'stage', 'owner_id'],
                'quotes': ['id', 'deal_id', 'recipient_id', 'revision'],
                'products': ['id', 'sku', 'name', 'unit_price']
            },
            'foreign_key_constraints': [
                'deals.owner_id -> users.id',
                'quotes.deal_id -> deals.id',
                'quotes.recipient_id -> quote_recipients.id',
                'quote_line_items.option_id -> quote_options.id',
                'quote_line_items.product_id -> products.id'
            ],
            'index_requirements': [
                'users.email',
                'deals.owner_id',
                'quotes.deal_id',
                'products.sku'
            ]
        }
    
    def validate_schema_integrity(self) -> Dict[str, Any]:
        """Validate current database schema integrity."""
        validation_result = {
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'valid',
            'issues': [],
            'warnings': [],
            'tables_checked': 0,
            'constraints_checked': 0,
            'indexes_checked': 0
        }
        
        try:
            # Check required tables exist
            inspector = inspect(self.engine)
            existing_tables = inspector.get_table_names()
            
            for table in self.validation_rules['required_tables']:
                if table not in existing_tables:
                    validation_result['issues'].append(f"Required table '{table}' is missing")
                    validation_result['status'] = 'invalid'
                else:
                    validation_result['tables_checked'] += 1
            
            # Check critical columns exist
            for table, columns in self.validation_rules['critical_columns'].items():
                if table in existing_tables:
                    existing_columns = [col['name'] for col in inspector.get_columns(table)]
                    for column in columns:
                        if column not in existing_columns:
                            validation_result['issues'].append(
                                f"Critical column '{column}' missing from table '{table}'"
                            )
                            validation_result['status'] = 'invalid'
            
            # Check foreign key constraints
            for constraint in self.validation_rules['foreign_key_constraints']:
                if self._check_foreign_key_constraint(constraint):
                    validation_result['constraints_checked'] += 1
                else:
                    validation_result['warnings'].append(f"Foreign key constraint not found: {constraint}")
            
            # Check required indexes
            for index in self.validation_rules['index_requirements']:
                if self._check_index_exists(index):
                    validation_result['indexes_checked'] += 1
                else:
                    validation_result['warnings'].append(f"Required index not found: {index}")
            
            logger.info("Database schema validation completed",
                       status=validation_result['status'],
                       issues=len(validation_result['issues']),
                       warnings=len(validation_result['warnings']))
            
        except Exception as e:
            validation_result['status'] = 'error'
            validation_result['issues'].append(f"Schema validation failed: {str(e)}")
            logger.error("Database schema validation failed", error=str(e))
        
        return validation_result
    
    def _check_foreign_key_constraint(self, constraint: str) -> bool:
        """Check if a foreign key constraint exists."""
        try:
            # Parse constraint format: "table.column -> referenced_table.referenced_column"
            parts = constraint.split(' -> ')
            if len(parts) != 2:
                return False
            
            table_column = parts[0].split('.')
            ref_table_column = parts[1].split('.')
            
            if len(table_column) != 2 or len(ref_table_column) != 2:
                return False
            
            table, column = table_column
            ref_table, ref_column = ref_table_column
            
            # Query to check foreign key constraint
            query = text("""
                SELECT 1 FROM information_schema.key_column_usage 
                WHERE table_name = :table 
                AND column_name = :column 
                AND referenced_table_name = :ref_table 
                AND referenced_column_name = :ref_column
            """)
            
            result = self.db.session.execute(query, {
                'table': table,
                'column': column,
                'ref_table': ref_table,
                'ref_column': ref_column
            }).fetchone()
            
            return result is not None
            
        except Exception as e:
            logger.warning("Failed to check foreign key constraint", constraint=constraint, error=str(e))
            return False
    
    def _check_index_exists(self, index_spec: str) -> bool:
        """Check if an index exists on a table.column."""
        try:
            table, column = index_spec.split('.')
            
            query = text("""
                SELECT 1 FROM pg_indexes 
                WHERE tablename = :table 
                AND indexdef LIKE :pattern
            """)
            
            result = self.db.session.execute(query, {
                'table': table,
                'pattern': f'%{column}%'
            }).fetchone()
            
            return result is not None
            
        except Exception as e:
            logger.warning("Failed to check index", index_spec=index_spec, error=str(e))
            return False
    
    def create_schema_snapshot(self, name: str) -> bool:
        """Create a snapshot of the current database schema."""
        try:
            inspector = inspect(self.engine)
            snapshot = {
                'timestamp': datetime.utcnow().isoformat(),
                'tables': {},
                'indexes': {},
                'constraints': {}
            }
            
            # Capture table schemas
            for table_name in inspector.get_table_names():
                table_info = {
                    'columns': inspector.get_columns(table_name),
                    'primary_keys': inspector.get_pk_constraint(table_name),
                    'foreign_keys': inspector.get_foreign_keys(table_name),
                    'indexes': inspector.get_indexes(table_name)
                }
                snapshot['tables'][table_name] = table_info
            
            # Store snapshot
            self.schema_snapshots[name] = snapshot
            
            # Save to file
            snapshot_file = Path(current_app.instance_path) / 'database_snapshots' / f'{name}.json'
            snapshot_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(snapshot_file, 'w') as f:
                json.dump(snapshot, f, indent=2, default=str)
            
            logger.info("Schema snapshot created", name=name, file=str(snapshot_file))
            return True
            
        except Exception as e:
            logger.error("Failed to create schema snapshot", name=name, error=str(e))
            return False
    
    def compare_schemas(self, snapshot1: str, snapshot2: str) -> Dict[str, Any]:
        """Compare two schema snapshots."""
        if snapshot1 not in self.schema_snapshots or snapshot2 not in self.schema_snapshots:
            return {'error': 'One or both snapshots not found'}
        
        schema1 = self.schema_snapshots[snapshot1]
        schema2 = self.schema_snapshots[snapshot2]
        
        comparison = {
            'timestamp': datetime.utcnow().isoformat(),
            'snapshot1': snapshot1,
            'snapshot2': snapshot2,
            'differences': {
                'tables_added': [],
                'tables_removed': [],
                'tables_modified': [],
                'columns_added': [],
                'columns_removed': [],
                'columns_modified': []
            }
        }
        
        # Compare tables
        tables1 = set(schema1['tables'].keys())
        tables2 = set(schema2['tables'].keys())
        
        comparison['differences']['tables_added'] = list(tables2 - tables1)
        comparison['differences']['tables_removed'] = list(tables1 - tables2)
        
        # Compare common tables
        common_tables = tables1 & tables2
        for table in common_tables:
            if schema1['tables'][table] != schema2['tables'][table]:
                comparison['differences']['tables_modified'].append(table)
        
        return comparison

class DatabaseBackupManager:
    """Manages database backups with verification and safety protocols."""
    
    def __init__(self, db):
        self.db = db
        self.engine = db.engine
        self.backup_dir = Path(current_app.instance_path) / 'database_backups'
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.retention_days = 30
    
    def create_backup(self, name: Optional[str] = None) -> Dict[str, Any]:
        """Create a database backup with verification."""
        if not name:
            name = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        backup_info = {
            'name': name,
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'in_progress',
            'file_path': None,
            'size_bytes': 0,
            'checksum': None,
            'verification_status': 'pending'
        }
        
        try:
            # Get database connection info
            db_url = str(self.engine.url)
            if not db_url.startswith('postgresql://'):
                raise Exception("Backup only supported for PostgreSQL databases")
            
            # Parse connection details
            import urllib.parse
            parsed = urllib.parse.urlparse(db_url)
            
            backup_file = self.backup_dir / f"{name}.sql"
            
            # Create pg_dump command
            cmd = [
                'pg_dump',
                '-h', parsed.hostname or 'localhost',
                '-p', str(parsed.port or 5432),
                '-U', parsed.username or 'postgres',
                '-d', parsed.path[1:],  # Remove leading slash
                '-f', str(backup_file),
                '--verbose',
                '--no-password'
            ]
            
            # Set password if provided
            env = os.environ.copy()
            if parsed.password:
                env['PGPASSWORD'] = parsed.password
            
            # Execute backup
            logger.info("Starting database backup", name=name, file=str(backup_file))
            result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                raise Exception(f"pg_dump failed: {result.stderr}")
            
            # Verify backup file
            if not backup_file.exists():
                raise Exception("Backup file was not created")
            
            # Calculate file info
            backup_info['file_path'] = str(backup_file)
            backup_info['size_bytes'] = backup_file.stat().st_size
            backup_info['checksum'] = self._calculate_checksum(backup_file)
            
            # Verify backup integrity
            verification_result = self.verify_backup(backup_file)
            backup_info['verification_status'] = verification_result['status']
            
            if verification_result['status'] == 'valid':
                backup_info['status'] = 'completed'
                logger.info("Database backup completed successfully", 
                           name=name, 
                           size=backup_info['size_bytes'],
                           checksum=backup_info['checksum'])
            else:
                backup_info['status'] = 'failed'
                backup_info['error'] = verification_result.get('error', 'Verification failed')
                logger.error("Database backup verification failed", name=name, error=backup_info['error'])
            
            # Save backup metadata
            metadata_file = self.backup_dir / f"{name}.json"
            with open(metadata_file, 'w') as f:
                json.dump(backup_info, f, indent=2)
            
            return backup_info
            
        except Exception as e:
            backup_info['status'] = 'failed'
            backup_info['error'] = str(e)
            logger.error("Database backup failed", name=name, error=str(e))
            return backup_info
    
    def verify_backup(self, backup_file: Path) -> Dict[str, Any]:
        """Verify the integrity of a database backup."""
        verification_result = {
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'valid',
            'checksum': None,
            'file_size': 0,
            'issues': []
        }
        
        try:
            if not backup_file.exists():
                verification_result['status'] = 'invalid'
                verification_result['issues'].append("Backup file does not exist")
                return verification_result
            
            # Check file size
            file_size = backup_file.stat().st_size
            verification_result['file_size'] = file_size
            
            if file_size == 0:
                verification_result['status'] = 'invalid'
                verification_result['issues'].append("Backup file is empty")
                return verification_result
            
            # Calculate checksum
            checksum = self._calculate_checksum(backup_file)
            verification_result['checksum'] = checksum
            
            # Basic SQL syntax check (for PostgreSQL dumps)
            try:
                with open(backup_file, 'r', encoding='utf-8') as f:
                    content = f.read(1024)  # Read first 1KB
                    if 'PostgreSQL database dump' not in content:
                        verification_result['issues'].append("File does not appear to be a PostgreSQL dump")
            except Exception as e:
                verification_result['issues'].append(f"Could not read backup file: {str(e)}")
            
            if verification_result['issues']:
                verification_result['status'] = 'invalid'
            else:
                logger.info("Backup verification successful", file=str(backup_file), checksum=checksum)
            
        except Exception as e:
            verification_result['status'] = 'error'
            verification_result['issues'].append(f"Verification failed: {str(e)}")
            logger.error("Backup verification failed", file=str(backup_file), error=str(e))
        
        return verification_result
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups."""
        backups = []
        
        for backup_file in self.backup_dir.glob("*.json"):
            try:
                with open(backup_file, 'r') as f:
                    backup_info = json.load(f)
                    backups.append(backup_info)
            except Exception as e:
                logger.warning("Failed to load backup metadata", file=str(backup_file), error=str(e))
        
        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return backups
    
    def cleanup_old_backups(self) -> int:
        """Remove backups older than retention period."""
        cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
        removed_count = 0
        
        for backup_file in self.backup_dir.glob("*.json"):
            try:
                with open(backup_file, 'r') as f:
                    backup_info = json.load(f)
                
                backup_time = datetime.fromisoformat(backup_info.get('timestamp', ''))
                if backup_time < cutoff_date:
                    # Remove both JSON and SQL files
                    sql_file = backup_file.with_suffix('.sql')
                    if sql_file.exists():
                        sql_file.unlink()
                    backup_file.unlink()
                    removed_count += 1
                    logger.info("Removed old backup", name=backup_info.get('name'))
            
            except Exception as e:
                logger.warning("Failed to process backup file", file=str(backup_file), error=str(e))
        
        logger.info("Backup cleanup completed", removed_count=removed_count)
        return removed_count

class DatabaseSafetyManager:
    """Main database safety manager coordinating all safety features."""
    
    def __init__(self, db):
        self.db = db
        self.schema_validator = DatabaseSchemaValidator(db)
        self.backup_manager = DatabaseBackupManager(db)
        self.safety_protocols = self._load_safety_protocols()
    
    def _load_safety_protocols(self) -> Dict[str, Any]:
        """Load database safety protocols."""
        return {
            'backup_before_migration': True,
            'validate_schema_after_migration': True,
            'require_manual_confirmation': True,
            'max_backup_age_hours': 24,
            'min_free_space_gb': 5,
            'critical_tables': ['users', 'deals', 'quotes'],
            'backup_retention_days': 30
        }
    
    def pre_migration_safety_check(self) -> Dict[str, Any]:
        """Perform safety checks before running migrations."""
        safety_check = {
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'safe',
            'checks': {},
            'warnings': [],
            'blockers': []
        }
        
        try:
            # Check 1: Verify schema integrity
            schema_validation = self.schema_validator.validate_schema_integrity()
            safety_check['checks']['schema_validation'] = schema_validation
            
            if schema_validation['status'] == 'invalid':
                safety_check['blockers'].append("Schema validation failed")
                safety_check['status'] = 'unsafe'
            
            # Check 2: Ensure recent backup exists
            recent_backup = self._check_recent_backup()
            safety_check['checks']['recent_backup'] = recent_backup
            
            if not recent_backup['exists']:
                safety_check['warnings'].append("No recent backup found")
                if self.safety_protocols['backup_before_migration']:
                    safety_check['blockers'].append("Recent backup required before migration")
                    safety_check['status'] = 'unsafe'
            
            # Check 3: Verify disk space
            disk_space = self._check_disk_space()
            safety_check['checks']['disk_space'] = disk_space
            
            if disk_space['free_gb'] < self.safety_protocols['min_free_space_gb']:
                safety_check['blockers'].append("Insufficient disk space")
                safety_check['status'] = 'unsafe'
            
            # Check 4: Database connectivity
            connectivity = self._check_database_connectivity()
            safety_check['checks']['connectivity'] = connectivity
            
            if not connectivity['connected']:
                safety_check['blockers'].append("Database connectivity issues")
                safety_check['status'] = 'unsafe'
            
            logger.info("Pre-migration safety check completed",
                       status=safety_check['status'],
                       blockers=len(safety_check['blockers']),
                       warnings=len(safety_check['warnings']))
            
        except Exception as e:
            safety_check['status'] = 'error'
            safety_check['blockers'].append(f"Safety check failed: {str(e)}")
            logger.error("Pre-migration safety check failed", error=str(e))
        
        return safety_check
    
    def _check_recent_backup(self) -> Dict[str, Any]:
        """Check if a recent backup exists."""
        backups = self.backup_manager.list_backups()
        recent_cutoff = datetime.utcnow() - timedelta(hours=self.safety_protocols['max_backup_age_hours'])
        
        recent_backups = [
            backup for backup in backups
            if datetime.fromisoformat(backup.get('timestamp', '')) > recent_cutoff
            and backup.get('status') == 'completed'
        ]
        
        return {
            'exists': len(recent_backups) > 0,
            'count': len(recent_backups),
            'latest': recent_backups[0] if recent_backups else None
        }
    
    def _check_disk_space(self) -> Dict[str, Any]:
        """Check available disk space."""
        try:
            import shutil
            total, used, free = shutil.disk_usage(self.backup_manager.backup_dir)
            free_gb = free / (1024**3)
            
            return {
                'free_gb': round(free_gb, 2),
                'total_gb': round(total / (1024**3), 2),
                'used_gb': round(used / (1024**3), 2),
                'sufficient': free_gb >= self.safety_protocols['min_free_space_gb']
            }
        except Exception as e:
            return {
                'error': str(e),
                'sufficient': False
            }
    
    def _check_database_connectivity(self) -> Dict[str, Any]:
        """Check database connectivity and basic health."""
        try:
            # Test basic connection
            with self.db.engine.connect() as conn:
                result = conn.execute(text("SELECT 1")).fetchone()
                if result[0] != 1:
                    return {'connected': False, 'error': 'Unexpected query result'}
            
            return {'connected': True, 'status': 'healthy'}
            
        except Exception as e:
            return {'connected': False, 'error': str(e)}
    
    def create_safety_backup(self) -> Dict[str, Any]:
        """Create a safety backup before critical operations."""
        backup_name = f"safety_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        return self.backup_manager.create_backup(backup_name)
    
    def get_safety_status(self) -> Dict[str, Any]:
        """Get overall database safety status."""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'schema_validation': self.schema_validator.validate_schema_integrity(),
            'recent_backups': self._check_recent_backup(),
            'disk_space': self._check_disk_space(),
            'connectivity': self._check_database_connectivity(),
            'safety_protocols': self.safety_protocols
        }

# Global database safety manager
db_safety_manager = None

def init_database_safety(db):
    """Initialize database safety manager."""
    global db_safety_manager
    db_safety_manager = DatabaseSafetyManager(db)
    logger.info("Database safety manager initialized")
    return db_safety_manager

def get_database_safety_manager():
    """Get the global database safety manager."""
    return db_safety_manager


