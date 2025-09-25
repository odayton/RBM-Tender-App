#!/usr/bin/env python3
"""
PostgreSQL Sync Script for Two-Machine Setup
Automates database sync between development machines via OneDrive
"""

import os
import sys
import subprocess
import tempfile
import hashlib
import json
from datetime import datetime
from pathlib import Path
from tqdm import tqdm
import time

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables
load_dotenv('config/.env')

class PostgreSQLSync:
    def __init__(self):
        self.project_root = project_root
        self.sync_dir = self.project_root / 'instance' / 'database_sync'
        self.sync_dir.mkdir(exist_ok=True)
        
        # Get PostgreSQL connection details from environment
        self.postgres_url = os.environ.get('DEV_DATABASE_URL')
        if not self.postgres_url:
            raise ValueError("DEV_DATABASE_URL not found in environment variables")
        
        # Parse connection details
        # Format: postgresql://postgres:password@localhost:5432/rbm_tender_app
        parts = self.postgres_url.replace('postgresql://', '').split('@')
        credentials = parts[0].split(':')
        host_port_db = parts[1].split('/')
        
        self.pg_user = credentials[0]
        self.pg_password = credentials[1]
        self.pg_host = host_port_db[0].split(':')[0]
        self.pg_port = host_port_db[0].split(':')[1] if ':' in host_port_db[0] else '5432'
        self.pg_database = host_port_db[1]
        
        # Metadata file for tracking changes
        self.metadata_file = self.sync_dir / 'sync_metadata.json'
    
    def _find_postgres_bin(self):
        """Find PostgreSQL bin directory"""
        # Common PostgreSQL installation paths on Windows
        possible_paths = [
            Path("C:/Program Files/PostgreSQL/17/bin"),
            Path("C:/Program Files/PostgreSQL/16/bin"),
            Path("C:/Program Files/PostgreSQL/15/bin"),
            Path("C:/Program Files/PostgreSQL/14/bin"),
            Path("C:/Program Files/PostgreSQL/13/bin"),
            Path("C:/Program Files/PostgreSQL/12/bin"),
        ]
        
        for path in possible_paths:
            if path.exists() and (path / 'pg_dump.exe').exists():
                return path
        
        # Check if pg_dump is in PATH
        try:
            result = subprocess.run(['pg_dump', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                return None  # Use PATH version
        except FileNotFoundError:
            pass
        
        return None
    
    def _get_database_checksum(self):
        """Get a checksum of the database to detect changes"""
        try:
            # Get PostgreSQL installation
            pg_bin_path = self._find_postgres_bin()
            if not pg_bin_path:
                return None
            
            # Set environment variable for password
            env = os.environ.copy()
            env['PGPASSWORD'] = self.pg_password
            
            # Get table list and their row counts
            cmd = [
                str(pg_bin_path / 'psql.exe'),
                '-U', self.pg_user,
                '-h', self.pg_host,
                '-p', self.pg_port,
                '-d', self.pg_database,
                '--no-password',
                '-t',  # tuples only
                '-c', """
                SELECT 
                    schemaname || '.' || tablename as table_name,
                    n_tup_ins + n_tup_upd + n_tup_del as total_changes,
                    n_live_tup as live_rows
                FROM pg_stat_user_tables 
                ORDER BY table_name;
                """
            ]
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            if result.returncode == 0:
                # Create a checksum from the table stats
                content = result.stdout.strip()
                return hashlib.md5(content.encode()).hexdigest()
            
        except Exception as e:
            print(f"⚠️  Could not get database checksum: {e}")
        
        return None
    
    def _load_sync_metadata(self):
        """Load sync metadata from file"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Could not load sync metadata: {e}")
        return {}
    
    def _save_sync_metadata(self, metadata):
        """Save sync metadata to file"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            print(f"⚠️  Could not save sync metadata: {e}")
    
    def _has_database_changed(self):
        """Check if database has changed since last sync"""
        current_checksum = self._get_database_checksum()
        if not current_checksum:
            return True  # Assume changed if we can't check
        
        metadata = self._load_sync_metadata()
        last_checksum = metadata.get('last_checksum')
        
        if last_checksum != current_checksum:
            # Update metadata with new checksum
            metadata['last_checksum'] = current_checksum
            metadata['last_check'] = datetime.now().isoformat()
            self._save_sync_metadata(metadata)
            return True
        
        return False
    
    def export_database(self, filename=None):
        """Export PostgreSQL database to SQL file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"rbm_postgres_backup_{timestamp}.sql"
        
        filepath = self.sync_dir / filename
        
        # Set environment variable for password
        env = os.environ.copy()
        env['PGPASSWORD'] = self.pg_password
        
        # Find PostgreSQL installation
        pg_bin_path = self._find_postgres_bin()
        if not pg_bin_path:
            print("❌ PostgreSQL installation not found. Please ensure PostgreSQL is installed.")
            return None
        
        try:
            print(f"📤 Exporting PostgreSQL database to: {filepath}")
            
            # Check if database has changed
            if not self._has_database_changed():
                print("✅ Database unchanged since last sync - no export needed")
                return None
            
            # Use pg_dump to export the database
            cmd = [
                str(pg_bin_path / 'pg_dump.exe'),
                '-U', self.pg_user,
                '-h', self.pg_host,
                '-p', self.pg_port,
                '-d', self.pg_database,
                '--no-password',
                '-v',
                '--clean',
                '--if-exists',
                '--create',
                '-f', str(filepath)
            ]
            
            # Show progress bar for export
            print("🔄 Exporting database...")
            
            # Start the export process
            process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Simple progress tracking for export
            with tqdm(total=100, desc="Export Progress", unit="%", 
                     bar_format='{l_bar}{bar}| {n:.0f}/{total:.0f} [{elapsed}<{remaining}, {rate_fmt}]') as pbar:
                
                # Start with 10% progress
                pbar.n = 10
                pbar.refresh()
                
                # Wait for completion with timeout
                try:
                    stdout, stderr = process.communicate(timeout=300)  # 5 minute timeout
                    result = type('Result', (), {'returncode': process.returncode, 'stdout': stdout, 'stderr': stderr})()
                    
                    # Complete the progress bar
                    pbar.n = 100
                    pbar.refresh()
                    
                except subprocess.TimeoutExpired:
                    process.kill()
                    stdout, stderr = process.communicate()
                    print("⚠️ Export process was terminated due to timeout")
                    result = type('Result', (), {'returncode': -1, 'stdout': stdout, 'stderr': stderr})()
                    pbar.n = 100
                    pbar.refresh()
            
            if result.returncode == 0:
                print(f"✅ Database exported successfully: {filepath}")
                print(f"📁 File size: {filepath.stat().st_size / 1024:.1f} KB")
                return filepath
            else:
                print(f"❌ Export failed: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ Error during export: {e}")
            return None

    def export_database_simple(self):
        """Simple export method without progress tracking (fallback)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.sync_dir / f"rbm_postgres_backup_{timestamp}.sql"
        
        # Set environment variable for password
        env = os.environ.copy()
        env['PGPASSWORD'] = self.pg_password
        
        # Find PostgreSQL installation
        pg_bin_path = self._find_postgres_bin()
        if not pg_bin_path:
            print("❌ PostgreSQL installation not found. Please ensure PostgreSQL is installed.")
            return None
        
        try:
            print(f"📤 Exporting PostgreSQL database to: {filepath}")
            print("🔄 Exporting database (simple mode)...")
            
            # Use pg_dump to export the database
            cmd = [
                str(pg_bin_path / 'pg_dump.exe') if pg_bin_path else 'pg_dump',
                '-U', self.pg_user,
                '-h', self.pg_host,
                '-p', self.pg_port,
                '-d', self.pg_database,
                '--no-password',
                '--verbose',
                '--file', str(filepath)
            ]
            
            # Run the export with timeout
            result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"✅ Database exported successfully: {filepath}")
                print(f"📁 File size: {filepath.stat().st_size / 1024:.1f} KB")
                return filepath
            else:
                print(f"❌ Export failed: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print("❌ Export operation timed out after 5 minutes")
            return None
        except Exception as e:
            print(f"❌ Error during export: {e}")
            return None

    def import_database(self, filepath):
        """Import PostgreSQL database from SQL file with improved progress tracking"""
        if not filepath.exists():
            print(f"❌ Import file not found: {filepath}")
            return False
        
        # Set environment variable for password
        env = os.environ.copy()
        env['PGPASSWORD'] = self.pg_password
        
        # Find PostgreSQL installation
        pg_bin_path = self._find_postgres_bin()
        if not pg_bin_path:
            print("❌ PostgreSQL installation not found. Please ensure PostgreSQL is installed.")
            return False
        
        try:
            print(f"📥 Importing PostgreSQL database from: {filepath}")
            
            # Get file size for progress tracking
            file_size = filepath.stat().st_size
            print(f"📁 File size: {file_size / 1024:.1f} KB")
            
            # Use psql to import the database
            cmd = [
                str(pg_bin_path / 'psql.exe') if pg_bin_path else 'psql',
                '-U', self.pg_user,
                '-h', self.pg_host,
                '-p', self.pg_port,
                '-d', self.pg_database,
                '--no-password',
                '-v',
                '-f', str(filepath)
            ]
            
            print("🔄 Importing database...")
            
            # Start the import process with timeout (Windows-compatible)
            try:
                # Start the import process
                process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                # Simple progress tracking for import
                with tqdm(total=100, desc="Import Progress", unit="%", 
                         bar_format='{l_bar}{bar}| {n:.0f}/{total:.0f} [{elapsed}<{remaining}, {rate_fmt}]') as pbar:
                    
                    # Start with 10% progress
                    pbar.n = 10
                    pbar.refresh()
                    
                    # Wait for completion with timeout
                    try:
                        stdout, stderr = process.communicate(timeout=30)  # 30 second timeout for faster fallback
                        result = type('Result', (), {'returncode': process.returncode, 'stdout': stdout, 'stderr': stderr})()
                        
                        # Complete the progress bar
                        pbar.n = 100
                        pbar.refresh()
                        
                    except subprocess.TimeoutExpired:
                        process.kill()
                        stdout, stderr = process.communicate()
                        print("⚠️ Import process was terminated due to timeout")
                        result = type('Result', (), {'returncode': -1, 'stdout': stdout, 'stderr': stderr})()
                        pbar.n = 100
                        pbar.refresh()
                
                if result.returncode == 0:
                    print(f"✅ Database imported successfully from: {filepath}")
                    return True
                else:
                    print(f"❌ Import failed: {result.stderr}")
                    # Show first few lines of stdout for debugging
                    if result.stdout:
                        lines = result.stdout.split('\n')[:5]
                        print("📋 Output preview:")
                        for line in lines:
                            if line.strip():
                                print(f"   {line}")
                    return False
                    
            except Exception as e:
                print(f"❌ Error during import: {e}")
                if 'process' in locals():
                    process.kill()
                return False
                
        except Exception as e:
            print(f"❌ Error during import setup: {e}")
            return False

    def import_database_simple(self, filepath):
        """Simple import method without progress tracking (fallback)"""
        if not filepath.exists():
            print(f"❌ Import file not found: {filepath}")
            return False
        
        # Set environment variable for password
        env = os.environ.copy()
        env['PGPASSWORD'] = self.pg_password
        
        # Find PostgreSQL installation
        pg_bin_path = self._find_postgres_bin()
        if not pg_bin_path:
            print("❌ PostgreSQL installation not found. Please ensure PostgreSQL is installed.")
            return False
        
        try:
            print(f"📥 Importing PostgreSQL database from: {filepath}")
            print(f"📁 File size: {filepath.stat().st_size / 1024:.1f} KB")
            print("🔄 Importing database (simple mode)...")
            
            # Use psql to import the database
            cmd = [
                str(pg_bin_path / 'psql.exe') if pg_bin_path else 'psql',
                '-U', self.pg_user,
                '-h', self.pg_host,
                '-p', self.pg_port,
                '-d', self.pg_database,
                '--no-password',
                '-f', str(filepath)
            ]
            
            # Run the import with timeout
            result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"✅ Database imported successfully from: {filepath}")
                return True
            else:
                print(f"❌ Import failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Import operation timed out after 5 minutes")
            return False
        except Exception as e:
            print(f"❌ Error during import: {e}")
            return False
    
    def list_available_backups(self):
        """List available backup files"""
        backup_files = list(self.sync_dir.glob('rbm_postgres_backup_*.sql'))
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        if not backup_files:
            print("📁 No backup files found")
            return []
        
        print(f"📁 Found {len(backup_files)} backup files:")
        for i, file in enumerate(backup_files, 1):
            size = file.stat().st_size / 1024
            mtime = datetime.fromtimestamp(file.stat().st_mtime)
            print(f"  {i}. {file.name} ({size:.1f} KB) - {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return backup_files
    
    def cleanup_old_backups(self, keep_count=5):
        """Clean up old backup files, keeping the most recent ones"""
        backup_files = list(self.sync_dir.glob('rbm_postgres_backup_*.sql'))
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        if len(backup_files) <= keep_count:
            print(f"📁 No cleanup needed - only {len(backup_files)} backup files")
            return
        
        files_to_delete = backup_files[keep_count:]
        for file in files_to_delete:
            try:
                file.unlink()
                print(f"🗑️  Deleted old backup: {file.name}")
            except Exception as e:
                print(f"⚠️  Could not delete {file.name}: {e}")
    
    def sync_to_onedrive(self):
        """Export database and sync to OneDrive"""
        print("🔄 Starting PostgreSQL to OneDrive sync...")
        
        # Check if database has changed
        if not self._has_database_changed():
            print("✅ Database unchanged since last sync - no sync needed")
            return True
        
        # Export database with fallback
        print("🔄 Attempting export with progress tracking...")
        backup_file = self.export_database()
        
        if not backup_file:
            print("⚠️ Progress tracking export failed, trying simple export...")
            backup_file = self.export_database_simple()
        
        if not backup_file:
            print("❌ All export methods failed. Please check the error messages above.")
            return False
        
        # Clean up old backups
        self.cleanup_old_backups()
        
        print("✅ Sync to OneDrive completed!")
        print(f"📁 Backup file: {backup_file}")
        print("💡 The file will automatically sync to your other machine via OneDrive")
        
        return True
    
    def sync_from_onedrive(self, backup_file=None):
        """Import database from OneDrive backup"""
        print("🔄 Starting OneDrive to PostgreSQL sync...")
        
        if backup_file:
            filepath = self.sync_dir / backup_file
        else:
            # Use the most recent backup
            backup_files = list(self.sync_dir.glob('rbm_postgres_backup_*.sql'))
            if not backup_files:
                print("❌ No backup files found in sync directory")
                return False
            
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            filepath = backup_files[0]
        
        # Import database with fallback
        print("🔄 Attempting import with progress tracking...")
        success = self.import_database(filepath)
        
        if not success:
            print("⚠️ Progress tracking import failed, trying simple import...")
            success = self.import_database_simple(filepath)
        
        if success:
            print("✅ Sync from OneDrive completed!")
            print(f"📁 Restored from: {filepath}")
        else:
            print("❌ All import methods failed. Please check the error messages above.")
        
        return success

def show_menu():
    """Display interactive menu"""
    print("\n" + "="*60)
    print("🔄 PostgreSQL Database Sync Tool")
    print("="*60)
    print("Choose an action:")
    print("1. 📤 Export database (create backup)")
    print("2. 📥 Import database (restore from backup)")
    print("3. 📋 List available backups")
    print("4. 🔄 Sync OUT - Export & prepare for OneDrive")
    print("5. 🔄 Sync IN - Import from OneDrive backup")
    print("6. 🔍 Check sync status (incremental)")
    print("7. 🗑️  Clean up old backups")
    print("8. ❌ Exit")
    print("="*60)

def get_user_choice():
    """Get user choice from menu"""
    while True:
        try:
            choice = input("\nEnter your choice (1-8): ").strip()
            if choice in ['1', '2', '3', '4', '5', '6', '7', '8']:
                return choice
            else:
                print("❌ Invalid choice. Please enter a number between 1-8.")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            sys.exit(0)

def interactive_mode():
    """Run in interactive mode"""
    try:
        sync = PostgreSQLSync()
        
        while True:
            show_menu()
            choice = get_user_choice()
            
            if choice == '1':
                print("\n📤 Exporting database...")
                sync.export_database()
                
            elif choice == '2':
                print("\n📥 Importing database...")
                # Check if specific file requested
                backup_files = list(sync.sync_dir.glob('rbm_postgres_backup_*.sql'))
                if backup_files:
                    backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                    print("\nAvailable backups:")
                    for i, file in enumerate(backup_files[:5], 1):  # Show last 5
                        size = file.stat().st_size / 1024
                        mtime = datetime.fromtimestamp(file.stat().st_mtime)
                        print(f"  {i}. {file.name} ({size:.1f} KB) - {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    use_latest = input("\nUse latest backup? (y/n): ").strip().lower()
                    if use_latest == 'y':
                        sync.sync_from_onedrive()
                    else:
                        print("💡 Use command line with --file option for specific backup")
                else:
                    print("❌ No backup files found")
                    
            elif choice == '3':
                print("\n📋 Available backups:")
                sync.list_available_backups()
                
            elif choice == '4':
                print("\n🔄 Syncing OUT to OneDrive...")
                sync.sync_to_onedrive()
                
            elif choice == '5':
                print("\n🔄 Syncing IN from OneDrive...")
                sync.sync_from_onedrive()
                
            elif choice == '6':
                print("\n🔍 Checking sync status...")
                if sync._has_database_changed():
                    print("🔄 Database has changed since last sync")
                    print("💡 Use 'Sync OUT' to export changes")
                else:
                    print("✅ Database unchanged since last sync")
                    print("💡 No sync needed")
                    
            elif choice == '7':
                print("\n🗑️  Cleaning up old backups...")
                keep_count = input("How many backups to keep? (default: 5): ").strip()
                try:
                    keep_count = int(keep_count) if keep_count else 5
                    sync.cleanup_old_backups(keep_count)
                except ValueError:
                    print("❌ Invalid number. Using default of 5.")
                    sync.cleanup_old_backups(5)
                    
            elif choice == '8':
                print("\n👋 Goodbye!")
                break
            
            # Ask if user wants to continue
            if choice != '8':
                continue_choice = input("\nPress Enter to continue or 'q' to quit: ").strip().lower()
                if continue_choice == 'q':
                    print("\n👋 Goodbye!")
                    break
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        input("\nPress Enter to exit...")
        sys.exit(1)

def main():
    """Main function"""
    import argparse
    
    # Check if any arguments were provided
    if len(sys.argv) == 1:
        # No arguments - run interactive mode
        interactive_mode()
        return
    
    # Arguments provided - run command line mode
    parser = argparse.ArgumentParser(description='PostgreSQL Sync for Two-Machine Setup')
    parser.add_argument('action', choices=['export', 'import', 'list', 'sync-out', 'sync-in'], 
                       help='Action to perform')
    parser.add_argument('--file', help='Specific backup file to import')
    parser.add_argument('--keep', type=int, default=5, help='Number of backups to keep')
    
    args = parser.parse_args()
    
    try:
        sync = PostgreSQLSync()
        
        if args.action == 'export':
            sync.export_database()
        
        elif args.action == 'import':
            if args.file:
                sync.import_database(sync.sync_dir / args.file)
            else:
                sync.sync_from_onedrive()
        
        elif args.action == 'list':
            sync.list_available_backups()
        
        elif args.action == 'sync-out':
            sync.sync_to_onedrive()
        
        elif args.action == 'sync-in':
            sync.sync_from_onedrive(args.file)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
