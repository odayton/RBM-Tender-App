#!/usr/bin/env python3
"""
Database Backup Manager

This script provides comprehensive backup and redundancy features to prevent data loss.
"""

import os
import shutil
import sqlite3
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
import json
import hashlib
import subprocess
import psycopg2
from urllib.parse import urlparse

class BackupManager:
    """Comprehensive backup management system."""
    
    def __init__(self, db_path=None):
        self.db_path = db_path or Path("app/instance/rbm_tender_app.db")
        self.backup_dir = Path("app/instance/backups")
        self.backup_dir.mkdir(exist_ok=True)
        
        # Detect database type from environment
        self.db_type = self._detect_database_type()
        self.db_url = os.environ.get('DATABASE_URL')
    
    def _detect_database_type(self):
        """Detect the database type from environment variables."""
        db_url = os.environ.get('DATABASE_URL')
        
        if db_url:
            if db_url.startswith('postgresql://') or db_url.startswith('postgres://'):
                return 'postgresql'
            elif db_url.startswith('sqlite://'):
                return 'sqlite'
        
        # Fallback: check if SQLite file exists
        if self.db_path.exists():
            return 'sqlite'
        
        return 'unknown'
        
    def create_backup(self, description="", include_metadata=True):
        """Create a comprehensive backup of the database."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Determine backup file extension based on database type
        if self.db_type == 'postgresql':
            backup_name = f"backup_{timestamp}_{description.replace(' ', '_')}.sql"
        else:
            backup_name = f"backup_{timestamp}_{description.replace(' ', '_')}.db"
            
        backup_path = self.backup_dir / backup_name
        
        try:
            # Create backup based on database type
            if self.db_type == 'postgresql':
                self._create_postgresql_backup(backup_path)
            elif self.db_type == 'sqlite':
                shutil.copy2(self.db_path, backup_path)
            else:
                print(f"❌ Unknown database type: {self.db_type}")
                return None
            
            # Create metadata file
            if include_metadata:
                metadata = self._create_backup_metadata(backup_path)
                metadata_path = backup_path.with_suffix('.json')
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2, default=str)
            
            print(f"✅ Backup created: {backup_name}")
            print(f"   📁 Location: {backup_path}")
            print(f"   📏 Size: {backup_path.stat().st_size} bytes")
            print(f"   🗄️  Database: {self.db_type}")
            
            # Clean up old backups
            self._cleanup_old_backups()
            
            return str(backup_path)
            
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return None
    
    def _create_postgresql_backup(self, backup_path):
        """Create a PostgreSQL backup using pg_dump."""
        try:
            # Parse database URL
            parsed_url = urlparse(self.db_url)
            
            # Build pg_dump command
            cmd = [
                'pg_dump',
                '-h', parsed_url.hostname or 'localhost',
                '-p', str(parsed_url.port or 5432),
                '-U', parsed_url.username or 'postgres',
                '-d', parsed_url.path.lstrip('/') or 'rbm_tender_app',
                '-f', str(backup_path),
                '--no-password',  # Use environment variables for password
                '--verbose'
            ]
            
            # Set environment variables for password
            env = os.environ.copy()
            if parsed_url.password:
                env['PGPASSWORD'] = parsed_url.password
            
            # Execute pg_dump
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"pg_dump failed: {result.stderr}")
                
            print(f"📦 PostgreSQL backup created successfully")
            
        except Exception as e:
            raise Exception(f"PostgreSQL backup failed: {e}")
    
    def _create_backup_metadata(self, backup_path):
        """Create metadata for the backup."""
        try:
            # Calculate file hash
            with open(backup_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            
            metadata = {
                "backup_timestamp": datetime.now().isoformat(),
                "backup_file": str(backup_path),
                "file_size": backup_path.stat().st_size,
                "file_hash": file_hash,
                "database_type": self.db_type,
                "description": "Auto-generated backup"
            }
            
            # Add database-specific metadata
            if self.db_type == 'sqlite':
                metadata["original_file"] = str(self.db_path)
                try:
                    conn = sqlite3.connect(backup_path)
                    cursor = conn.cursor()
                    
                    # Get table information
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = [row[0] for row in cursor.fetchall()]
                    
                    # Get row counts for each table
                    table_counts = {}
                    for table in tables:
                        try:
                            cursor.execute(f"SELECT COUNT(*) FROM {table}")
                            count = cursor.fetchone()[0]
                            table_counts[table] = count
                        except:
                            table_counts[table] = 0
                    
                    conn.close()
                    
                    metadata["tables"] = tables
                    metadata["table_counts"] = table_counts
                    
                except Exception as e:
                    metadata["error"] = f"Failed to get SQLite metadata: {e}"
                    
            elif self.db_type == 'postgresql':
                metadata["database_url"] = self._mask_password(self.db_url)
                try:
                    # Get basic info from the SQL dump file
                    with open(backup_path, 'r') as f:
                        content = f.read()
                        metadata["backup_type"] = "SQL dump"
                        metadata["contains_data"] = "-- Data for" in content or "INSERT INTO" in content
                        
                except Exception as e:
                    metadata["error"] = f"Failed to analyze PostgreSQL backup: {e}"
            
            return metadata
            
        except Exception as e:
            return {"error": str(e)}
    
    def _mask_password(self, db_url):
        """Mask password in database URL for security."""
        if not db_url:
            return None
        parsed = urlparse(db_url)
        if parsed.password:
            return db_url.replace(parsed.password, "***")
        return db_url
    
    def restore_backup(self, backup_path):
        """Restore database from backup."""
        backup_path = Path(backup_path)
        
        if not backup_path.exists():
            print(f"❌ Backup file not found: {backup_path}")
            return False
        
        try:
            # Create a backup of current database before restore
            current_backup = self.create_backup("before_restore")
            
            # Restore the backup
            shutil.copy2(backup_path, self.db_path)
            
            print(f"✅ Database restored from: {backup_path}")
            print(f"   📁 Current backup saved as: {current_backup}")
            
            return True
            
        except Exception as e:
            print(f"❌ Restore failed: {e}")
            return False
    
    def list_backups(self):
        """List all available backups."""
        backups = []
        
        # Look for both .db and .sql backup files
        for pattern in ["backup_*.db", "backup_*.sql"]:
            for file in self.backup_dir.glob(pattern):
                try:
                    metadata_file = file.with_suffix('.json')
                    metadata = {}
                    
                    if metadata_file.exists():
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                    
                    backup_info = {
                        "file": file.name,
                        "path": str(file),
                        "size": file.stat().st_size,
                        "created": datetime.fromtimestamp(file.stat().st_mtime),
                        "metadata": metadata
                    }
                    backups.append(backup_info)
                    
                except Exception as e:
                    print(f"⚠️  Error reading backup {file}: {e}")
        
        return sorted(backups, key=lambda x: x["created"], reverse=True)
    
    def _cleanup_old_backups(self, keep_count=10):
        """Clean up old backups, keeping only the most recent ones."""
        backups = self.list_backups()
        
        if len(backups) > keep_count:
            backups_to_delete = backups[keep_count:]
            
            for backup in backups_to_delete:
                try:
                    # Delete backup file
                    Path(backup["path"]).unlink()
                    
                    # Delete metadata file
                    metadata_file = Path(backup["path"]).with_suffix('.json')
                    if metadata_file.exists():
                        metadata_file.unlink()
                    
                    print(f"🗑️  Deleted old backup: {backup['file']}")
                    
                except Exception as e:
                    print(f"⚠️  Error deleting backup {backup['file']}: {e}")
    
    def verify_backup(self, backup_path):
        """Verify that a backup is valid and complete."""
        backup_path = Path(backup_path)
        
        if not backup_path.exists():
            print(f"❌ Backup file not found: {backup_path}")
            return False
        
        try:
            # Test database connection
            conn = sqlite3.connect(backup_path)
            cursor = conn.cursor()
            
            # Check if it's a valid SQLite database
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            conn.close()
            
            print(f"✅ Backup verification successful: {backup_path}")
            print(f"   📋 Tables found: {len(tables)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Backup verification failed: {e}")
            return False
    
    def auto_backup(self):
        """Create an automatic backup if needed."""
        # Skip auto-backup in development mode to prevent loops
        import os
        if os.environ.get('FLASK_ENV') == 'development':
            return None
        
        # Skip backup if database type is unknown or PostgreSQL tools not available
        if self.db_type == 'unknown':
            print("⚠️  Skipping backup: Unknown database type")
            return None
            
        if self.db_type == 'postgresql' and not self._check_postgresql_tools():
            print("⚠️  Skipping backup: PostgreSQL tools (pg_dump) not available")
            return None
            
        # Check if we need to create a backup
        if not self._should_create_backup():
            return None
        
        # Add a small delay to prevent rapid-fire backups
        import time
        time.sleep(1)
        
        return self.create_backup("auto_backup")
    
    def _check_postgresql_tools(self):
        """Check if PostgreSQL tools are available."""
        try:
            result = subprocess.run(['pg_dump', '--version'], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def _should_create_backup(self):
        """Determine if we should create an automatic backup."""
        backups = self.list_backups()
        
        if not backups:
            return True
        
        # Check if last backup is older than 24 hours
        last_backup = backups[0]["created"]
        hours_since_backup = (datetime.now() - last_backup).total_seconds() / 3600
        
        return hours_since_backup > 24

def main():
    """Main function for backup management."""
    manager = BackupManager()
    
    print("🔧 Database Backup Manager")
    print("=" * 50)
    
    # Create initial backup
    print("\n📦 Creating initial backup...")
    backup_path = manager.create_backup("initial_setup")
    
    if backup_path:
        print(f"✅ Initial backup created: {backup_path}")
        
        # List all backups
        print("\n📋 Available backups:")
        backups = manager.list_backups()
        for i, backup in enumerate(backups[:5], 1):
            print(f"  {i}. {backup['file']} ({backup['size']} bytes)")
            print(f"     Created: {backup['created']}")
        
        # Verify the backup
        print(f"\n🔍 Verifying backup...")
        manager.verify_backup(backup_path)
    
    print("\n🎉 Backup system initialized successfully!")

if __name__ == "__main__":
    main() 