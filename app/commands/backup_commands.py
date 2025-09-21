"""
Backup CLI Commands

This module provides Flask CLI commands for backup management.
"""

import click
from flask.cli import with_appcontext
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backup_manager import BackupManager

@click.group()
def backup():
    """Database backup commands."""
    pass

@backup.command()
@click.option('--description', '-d', help='Backup description')
@with_appcontext
def create(description=""):
    """Create a manual backup."""
    manager = BackupManager()
    backup_path = manager.create_backup(description or "manual_backup")
    
    if backup_path:
        click.echo(f"✅ Backup created successfully: {backup_path}")
    else:
        click.echo("❌ Backup creation failed!")
        raise click.Abort()

@backup.command()
@with_appcontext
def list():
    """List all available backups."""
    manager = BackupManager()
    backups = manager.list_backups()
    
    if not backups:
        click.echo("📭 No backups found.")
        return
    
    click.echo(f"📋 Found {len(backups)} backup(s):")
    click.echo("=" * 60)
    
    for i, backup in enumerate(backups, 1):
        click.echo(f"{i}. {backup['file']}")
        click.echo(f"   📏 Size: {backup['size']} bytes")
        click.echo(f"   📅 Created: {backup['created']}")
        
        if backup['metadata'] and 'table_counts' in backup['metadata']:
            total_records = sum(backup['metadata']['table_counts'].values())
            click.echo(f"   📊 Records: {total_records}")
        
        click.echo()

@backup.command()
@click.argument('backup_file')
@with_appcontext
def restore(backup_file):
    """Restore database from backup."""
    manager = BackupManager()
    
    # Find the backup file
    backup_path = Path("app/instance/backups") / backup_file
    
    if not backup_path.exists():
        click.echo(f"❌ Backup file not found: {backup_file}")
        click.echo("Use 'flask backup list' to see available backups.")
        raise click.Abort()
    
    # Confirm the restore
    if not click.confirm(f"Are you sure you want to restore from {backup_file}? This will overwrite the current database."):
        click.echo("Restore cancelled.")
        return
    
    success = manager.restore_backup(str(backup_path))
    
    if success:
        click.echo("✅ Database restored successfully!")
    else:
        click.echo("❌ Restore failed!")
        raise click.Abort()

@backup.command()
@click.argument('backup_file')
@with_appcontext
def verify(backup_file):
    """Verify a backup file."""
    manager = BackupManager()
    
    # Find the backup file
    backup_path = Path("app/instance/backups") / backup_file
    
    if not backup_path.exists():
        click.echo(f"❌ Backup file not found: {backup_file}")
        click.echo("Use 'flask backup list' to see available backups.")
        raise click.Abort()
    
    success = manager.verify_backup(str(backup_path))
    
    if success:
        click.echo("✅ Backup verification successful!")
    else:
        click.echo("❌ Backup verification failed!")
        raise click.Abort()

@backup.command()
@click.option('--keep', '-k', default=5, help='Number of backups to keep')
@with_appcontext
def cleanup(keep):
    """Clean up old backups, keeping only the specified number."""
    manager = BackupManager()
    
    if not click.confirm(f"Are you sure you want to clean up old backups, keeping only {keep}?"):
        click.echo("Cleanup cancelled.")
        return
    
    removed_count = manager.cleanup_old_backups(keep)
    click.echo(f"✅ Cleanup completed. Removed {removed_count} old backup(s).")

# Database Sync Commands
@click.group()
def sync():
    """Database synchronization commands."""
    pass

@sync.command()
@click.option('--env-file', '-e', default='.env.production', help='Environment file to use')
@with_appcontext
def database(env_file):
    """Sync PostgreSQL database for deployment."""
    click.echo("🔄 PostgreSQL database sync is now handled by the postgres_sync.py script")
    click.echo("💡 Use: py scripts/development/postgres_sync.py for database synchronization")
    click.echo("📋 Available commands:")
    click.echo("  - Export database: py scripts/development/postgres_sync.py export")
    click.echo("  - Import database: py scripts/development/postgres_sync.py import")
    click.echo("  - Sync to OneDrive: py scripts/development/postgres_sync.py sync-out")
    click.echo("  - Sync from OneDrive: py scripts/development/postgres_sync.py sync-in")

@sync.command()
@with_appcontext
def status():
    """Check the PostgreSQL database status."""
    click.echo("🔍 PostgreSQL database status check")
    click.echo("💡 Use the postgres_sync.py script for detailed database status:")
    click.echo("  py scripts/development/postgres_sync.py")
    click.echo("📋 Or check database directly:")
    click.echo("  py -c \"import psycopg2; conn = psycopg2.connect('postgresql://postgres:YOUR_PASSWORD@localhost:5432/rbm_tender_app'); cur = conn.cursor(); cur.execute('SELECT version()'); print('PostgreSQL:', cur.fetchone()[0]); conn.close()\"")

def register_backup_commands(app):
    """Register backup commands with the Flask app."""
    app.cli.add_command(backup)
    app.cli.add_command(sync) 