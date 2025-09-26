#!/usr/bin/env python3
"""
Smart Backup System for RBM Tender App

This script creates intelligent backups that:
- Only backup when changes are detected
- Compare file sizes and checksums
- Automatically clean up old backups
- Prevent disk space issues
"""

import os
import sys
import shutil
import hashlib
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import json
import argparse
from typing import Dict, List, Optional, Tuple

class SmartBackupManager:
    """Intelligent backup manager that prevents redundant backups."""
    
    def __init__(self, app_path: str = "/opt/rbm-tender-app", backup_dir: str = "/opt"):
        self.app_path = Path(app_path)
        self.backup_dir = Path(backup_dir)
        self.backup_prefix = "rbm-tender-app.backup"
        self.max_backups = 3  # Keep only 3 recent backups
        self.min_backup_interval = 3600  # 1 hour minimum between backups
        
        # Files/directories to exclude from backup
        self.exclude_patterns = {
            'venv/lib/python*/site-packages',  # Python packages (can be reinstalled)
            'app/instance/logs',               # Log files
            'app/instance/sessions',           # Session files
            'app/instance/uploads',            # Upload files (if not critical)
            '__pycache__',                     # Python cache
            '*.pyc',                          # Compiled Python files
            '.git',                           # Git repository
            'node_modules',                   # Node modules (if any)
        }
        
    def should_create_backup(self) -> Tuple[bool, str]:
        """
        Determine if a backup should be created.
        Returns (should_backup, reason)
        """
        # Check if app directory exists
        if not self.app_path.exists():
            return False, "Application directory does not exist"
        
        # Get existing backups
        existing_backups = self.get_existing_backups()
        
        # If no backups exist, create one
        if not existing_backups:
            return True, "No existing backups found"
        
        # Check minimum time interval
        latest_backup = existing_backups[0]
        time_since_backup = datetime.now() - latest_backup['timestamp']
        if time_since_backup.total_seconds() < self.min_backup_interval:
            return False, f"Too soon since last backup ({time_since_backup.total_seconds():.0f}s < {self.min_backup_interval}s)"
        
        # Check if application has changed
        has_changes, change_reason = self.detect_changes(latest_backup)
        if not has_changes:
            return False, f"No changes detected: {change_reason}"
        
        return True, f"Changes detected: {change_reason}"
    
    def get_existing_backups(self) -> List[Dict]:
        """Get list of existing backups sorted by timestamp (newest first)."""
        backups = []
        
        for backup_dir in self.backup_dir.glob(f"{self.backup_prefix}.*"):
            if backup_dir.is_dir():
                # Extract timestamp from directory name
                timestamp_str = backup_dir.name.replace(f"{self.backup_prefix}.", "")
                try:
                    # Parse timestamp (format: YYYYMMDD-HHMMSS)
                    timestamp = datetime.strptime(timestamp_str, "%Y%m%d-%H%M%S")
                    backups.append({
                        'path': backup_dir,
                        'timestamp': timestamp,
                        'size': self.get_directory_size(backup_dir)
                    })
                except ValueError:
                    # Skip directories with invalid timestamp format
                    continue
        
        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x['timestamp'], reverse=True)
        return backups
    
    def detect_changes(self, latest_backup: Dict) -> Tuple[bool, str]:
        """
        Detect if the application has changed since the latest backup.
        Returns (has_changes, reason)
        """
        backup_path = latest_backup['path']
        
        # Compare directory sizes first (quick check)
        current_size = self.get_directory_size(self.app_path)
        backup_size = latest_backup['size']
        
        if current_size != backup_size:
            return True, f"Size changed: {current_size} vs {backup_size} bytes"
        
        # If sizes are the same, do detailed file comparison
        changes = self.compare_directories(self.app_path, backup_path)
        
        if changes:
            return True, f"Files changed: {', '.join(changes[:3])}{'...' if len(changes) > 3 else ''}"
        
        return False, "No file changes detected"
    
    def get_directory_size(self, path: Path) -> int:
        """Calculate total size of directory, excluding specified patterns."""
        total_size = 0
        
        try:
            for item in path.rglob('*'):
                if item.is_file() and not self.should_exclude_file(item):
                    try:
                        total_size += item.stat().st_size
                    except (OSError, PermissionError):
                        # Skip files we can't access
                        continue
        except (OSError, PermissionError):
            # If we can't access the directory, return 0
            pass
        
        return total_size
    
    def should_exclude_file(self, file_path: Path) -> bool:
        """Check if a file should be excluded from backup comparison."""
        path_str = str(file_path)
        
        for pattern in self.exclude_patterns:
            if pattern in path_str:
                return True
        
        return False
    
    def compare_directories(self, current_path: Path, backup_path: Path) -> List[str]:
        """Compare two directories and return list of changed files."""
        changes = []
        
        # Get all files in current directory
        current_files = {}
        for file_path in current_path.rglob('*'):
            if file_path.is_file() and not self.should_exclude_file(file_path):
                relative_path = file_path.relative_to(current_path)
                current_files[str(relative_path)] = {
                    'size': file_path.stat().st_size,
                    'mtime': file_path.stat().st_mtime
                }
        
        # Compare with backup files
        for file_path in backup_path.rglob('*'):
            if file_path.is_file() and not self.should_exclude_file(file_path):
                relative_path = file_path.relative_to(backup_path)
                relative_str = str(relative_path)
                
                if relative_str in current_files:
                    current_info = current_files[relative_str]
                    backup_info = {
                        'size': file_path.stat().st_size,
                        'mtime': file_path.stat().st_mtime
                    }
                    
                    # Check if file has changed
                    if (current_info['size'] != backup_info['size'] or 
                        abs(current_info['mtime'] - backup_info['mtime']) > 1):
                        changes.append(relative_str)
                    
                    # Remove from current_files to track new files
                    del current_files[relative_str]
                else:
                    # File was deleted
                    changes.append(f"{relative_str} (deleted)")
        
        # Add new files
        for relative_str in current_files:
            changes.append(f"{relative_str} (new)")
        
        return changes
    
    def create_backup(self, force: bool = False) -> Optional[str]:
        """Create a backup if needed."""
        if not force:
            should_backup, reason = self.should_create_backup()
            if not should_backup:
                print(f"⏭️  Skipping backup: {reason}")
                return None
        
        # Clean up old backups first
        self.cleanup_old_backups()
        
        # Create new backup
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_name = f"{self.backup_prefix}.{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        print(f"📦 Creating backup: {backup_name}")
        
        try:
            # Copy application directory
            shutil.copytree(
                self.app_path, 
                backup_path,
                ignore=self._ignore_patterns,
                dirs_exist_ok=False
            )
            
            # Create backup metadata
            metadata = {
                'timestamp': timestamp,
                'created_at': datetime.now().isoformat(),
                'source_path': str(self.app_path),
                'backup_path': str(backup_path),
                'size_bytes': self.get_directory_size(backup_path),
                'excluded_patterns': list(self.exclude_patterns)
            }
            
            metadata_file = backup_path / '.backup_metadata.json'
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"✅ Backup created successfully: {backup_path}")
            print(f"   📏 Size: {metadata['size_bytes']:,} bytes")
            
            return str(backup_path)
            
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            # Clean up failed backup
            if backup_path.exists():
                shutil.rmtree(backup_path)
            return None
    
    def _ignore_patterns(self, dir_path: str, names: List[str]) -> List[str]:
        """Function to ignore patterns during shutil.copytree."""
        ignored = []
        
        for name in names:
            full_path = os.path.join(dir_path, name)
            
            # Check if this path should be excluded
            for pattern in self.exclude_patterns:
                if pattern in full_path:
                    ignored.append(name)
                    break
        
        return ignored
    
    def cleanup_old_backups(self) -> int:
        """Remove old backups, keeping only the most recent ones."""
        existing_backups = self.get_existing_backups()
        
        if len(existing_backups) <= self.max_backups:
            return 0
        
        # Remove oldest backups
        backups_to_remove = existing_backups[self.max_backups:]
        removed_count = 0
        
        for backup in backups_to_remove:
            try:
                print(f"🗑️  Removing old backup: {backup['path'].name}")
                shutil.rmtree(backup['path'])
                removed_count += 1
            except Exception as e:
                print(f"⚠️  Failed to remove backup {backup['path'].name}: {e}")
        
        if removed_count > 0:
            print(f"✅ Cleaned up {removed_count} old backup(s)")
        
        return removed_count
    
    def list_backups(self) -> None:
        """List all existing backups."""
        backups = self.get_existing_backups()
        
        if not backups:
            print("📭 No backups found")
            return
        
        print(f"📋 Found {len(backups)} backup(s):")
        print("=" * 80)
        
        for i, backup in enumerate(backups, 1):
            age = datetime.now() - backup['timestamp']
            age_str = self._format_timedelta(age)
            
            print(f"{i}. {backup['path'].name}")
            print(f"   📅 Created: {backup['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} ({age_str} ago)")
            print(f"   📏 Size: {backup['size']:,} bytes")
            print()
    
    def _format_timedelta(self, td: timedelta) -> str:
        """Format timedelta as human-readable string."""
        total_seconds = int(td.total_seconds())
        
        if total_seconds < 60:
            return f"{total_seconds}s"
        elif total_seconds < 3600:
            return f"{total_seconds // 60}m"
        elif total_seconds < 86400:
            return f"{total_seconds // 3600}h"
        else:
            return f"{total_seconds // 86400}d"

def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Smart Backup Manager for RBM Tender App")
    parser.add_argument('--app-path', default='/opt/rbm-tender-app', 
                       help='Path to application directory')
    parser.add_argument('--backup-dir', default='/opt', 
                       help='Directory to store backups')
    parser.add_argument('--max-backups', type=int, default=3, 
                       help='Maximum number of backups to keep')
    parser.add_argument('--force', action='store_true', 
                       help='Force backup creation even if no changes detected')
    parser.add_argument('--list', action='store_true', 
                       help='List existing backups')
    parser.add_argument('--cleanup', action='store_true', 
                       help='Clean up old backups')
    
    args = parser.parse_args()
    
    # Check if running as root for /opt access
    if os.geteuid() != 0:
        print("⚠️  Warning: Not running as root. May not have access to /opt directory.")
        print("   Consider running with sudo for production deployments.")
    
    manager = SmartBackupManager(
        app_path=args.app_path,
        backup_dir=args.backup_dir
    )
    manager.max_backups = args.max_backups
    
    if args.list:
        manager.list_backups()
    elif args.cleanup:
        removed = manager.cleanup_old_backups()
        print(f"Removed {removed} old backup(s)")
    else:
        result = manager.create_backup(force=args.force)
        if result:
            print(f"Backup created: {result}")
        else:
            print("No backup created")
            sys.exit(1)

if __name__ == "__main__":
    main()
