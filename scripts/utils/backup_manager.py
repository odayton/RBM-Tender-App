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

class BackupManager:
    """Comprehensive backup management system."""
    
    def __init__(self, db_path=None):
        self.db_path = db_path or Path("app/instance/rbm_tender_app.db")
        self.backup_dir = Path("app/instance/backups")
        self.backup_dir.mkdir(exist_ok=True)
        
    def create_backup(self, description="", include_metadata=True):
        """Create a comprehensive backup of the database."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}_{description.replace(' ', '_')}.db"
        backup_path = self.backup_dir / backup_name
        
        try:
            # Create backup
            shutil.copy2(self.db_path, backup_path)
            
            # Create metadata file
            if include_metadata:
                metadata = self._create_backup_metadata(backup_path)
                metadata_path = backup_path.with_suffix('.json')
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2, default=str)
            
            print(f"✅ Backup created: {backup_name}")
            print(f"   📁 Location: {backup_path}")
            print(f"   📏 Size: {backup_path.stat().st_size} bytes")
            
            # Clean up old backups
            self._cleanup_old_backups()
            
            return str(backup_path)
            
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return None
    
    def _create_backup_metadata(self, backup_path):
        """Create metadata for the backup."""
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
            
            # Calculate file hash
            with open(backup_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            
            return {
                "backup_timestamp": datetime.now().isoformat(),
                "original_file": str(self.db_path),
                "backup_file": str(backup_path),
                "file_size": backup_path.stat().st_size,
                "file_hash": file_hash,
                "tables": tables,
                "table_counts": table_counts,
                "description": "Auto-generated backup"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
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
        
        for file in self.backup_dir.glob("backup_*.db"):
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
        # Check if we need to create a backup
        if not self._should_create_backup():
            return None
        
        return self.create_backup("auto_backup")
    
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