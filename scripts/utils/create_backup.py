#!/usr/bin/env python3
"""
Simple Database Backup Script for RBM Tender App
Creates a manual backup of the PostgreSQL database
"""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def load_env_file():
    """Load environment variables from config/.env file"""
    env_file = project_root / 'config' / '.env'
    env_vars = {}
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
                    os.environ[key] = value
    
    return env_vars

def create_backup():
    """Create a manual backup of the PostgreSQL database"""
    
    # Load environment variables
    load_env_file()
    
    # Get database connection details from environment
    database_url = os.environ.get('DATABASE_URL') or os.environ.get('SQLALCHEMY_DATABASE_URI')
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        print("💡 Make sure config/.env file exists and contains DATABASE_URL")
        return False
    
    # Parse connection details
    # Format: postgresql://username:password@localhost:5432/database_name
    try:
        parts = database_url.replace('postgresql://', '').split('@')
        credentials = parts[0].split(':')
        host_port_db = parts[1].split('/')
        
        username = credentials[0]
        password = credentials[1]
        host_port = host_port_db[0].split(':')
        host = host_port[0]
        port = host_port[1] if len(host_port) > 1 else '5432'
        database = host_port_db[1]
        
    except (IndexError, ValueError) as e:
        print(f"❌ Error parsing database URL: {e}")
        print(f"   URL format should be: postgresql://username:password@host:port/database")
        return False
    
    # Create backup directory if it doesn't exist
    backup_dir = project_root / 'backups' / 'database'
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"rbm_postgres_backup_{timestamp}.sql"
    backup_path = backup_dir / backup_filename
    
    # Set environment variable for password
    env = os.environ.copy()
    env['PGPASSWORD'] = password
    
    try:
        print(f"📤 Creating database backup...")
        print(f"   Database: {database}")
        print(f"   Host: {host}:{port}")
        print(f"   User: {username}")
        print(f"   Backup file: {backup_path}")
        
        # Use pg_dump to create the backup
        cmd = [
            'pg_dump',
            '-h', host,
            '-p', port,
            '-U', username,
            '-d', database,
            '--no-password',
            '--verbose',
            '--clean',
            '--if-exists',
            '--create',
            '-f', str(backup_path)
        ]
        
        print("🔄 Running pg_dump...")
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            # Get file size
            file_size = backup_path.stat().st_size
            print(f"✅ Backup created successfully!")
            print(f"📁 File: {backup_path}")
            print(f"📊 Size: {file_size / 1024:.1f} KB")
            print(f"⏰ Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # List recent backups
            list_recent_backups(backup_dir)
            
            return True
        else:
            print(f"❌ Backup failed!")
            print(f"   Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Backup operation timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ Error during backup: {e}")
        return False

def list_recent_backups(backup_dir, count=5):
    """List recent backup files"""
    backup_files = list(backup_dir.glob('rbm_postgres_backup_*.sql'))
    backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    if not backup_files:
        print("📁 No backup files found")
        return
    
    print(f"\n📁 Recent backups (last {min(count, len(backup_files))}):")
    for i, file in enumerate(backup_files[:count], 1):
        size = file.stat().st_size / 1024
        mtime = datetime.fromtimestamp(file.stat().st_mtime)
        print(f"  {i}. {file.name} ({size:.1f} KB) - {mtime.strftime('%Y-%m-%d %H:%M:%S')}")

def restore_backup(backup_filename):
    """Restore database from backup file"""
    
    # Load environment variables
    load_env_file()
    
    # Get database connection details
    database_url = os.environ.get('DATABASE_URL') or os.environ.get('SQLALCHEMY_DATABASE_URI')
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    try:
        parts = database_url.replace('postgresql://', '').split('@')
        credentials = parts[0].split(':')
        host_port_db = parts[1].split('/')
        
        username = credentials[0]
        password = credentials[1]
        host_port = host_port_db[0].split(':')
        host = host_port[0]
        port = host_port[1] if len(host_port) > 1 else '5432'
        database = host_port_db[1]
        
    except (IndexError, ValueError) as e:
        print(f"❌ Error parsing database URL: {e}")
        return False
    
    # Find backup file
    backup_dir = project_root / 'backups' / 'database'
    backup_path = backup_dir / backup_filename
    
    if not backup_path.exists():
        print(f"❌ Backup file not found: {backup_path}")
        return False
    
    # Set environment variable for password
    env = os.environ.copy()
    env['PGPASSWORD'] = password
    
    try:
        print(f"📥 Restoring database from backup...")
        print(f"   Backup file: {backup_path}")
        print(f"   Database: {database}")
        
        # Use psql to restore the database
        cmd = [
            'psql',
            '-h', host,
            '-p', port,
            '-U', username,
            '-d', database,
            '--no-password',
            '-v',
            '-f', str(backup_path)
        ]
        
        print("🔄 Running psql restore...")
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✅ Database restored successfully from: {backup_filename}")
            return True
        else:
            print(f"❌ Restore failed!")
            print(f"   Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Restore operation timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ Error during restore: {e}")
        return False

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple Database Backup Tool for RBM Tender App')
    parser.add_argument('action', choices=['backup', 'restore', 'list'], 
                       help='Action to perform')
    parser.add_argument('--file', help='Backup file to restore (for restore action)')
    
    args = parser.parse_args()
    
    try:
        if args.action == 'backup':
            create_backup()
        
        elif args.action == 'restore':
            if not args.file:
                print("❌ --file argument required for restore action")
                print("💡 Use 'list' action to see available backup files")
                return
            
            restore_backup(args.file)
        
        elif args.action == 'list':
            backup_dir = project_root / 'backups' / 'database'
            backup_dir.mkdir(parents=True, exist_ok=True)
            list_recent_backups(backup_dir, count=10)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()