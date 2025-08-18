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
        raise click.Abort()
    
    success = manager.verify_backup(str(backup_path))
    
    if success:
        click.echo("✅ Backup verification successful!")
    else:
        click.echo("❌ Backup verification failed!")
        raise click.Abort()

@backup.command()
@click.option('--keep', default=10, help='Number of backups to keep')
@with_appcontext
def cleanup(keep):
    """Clean up old backups, keeping only the most recent ones."""
    manager = BackupManager()
    
    backups = manager.list_backups()
    
    if len(backups) <= keep:
        click.echo(f"📭 No cleanup needed. You have {len(backups)} backups (keeping {keep}).")
        return
    
    to_delete = len(backups) - keep
    click.echo(f"🗑️  Will delete {to_delete} old backup(s), keeping {keep} most recent.")
    
    if click.confirm("Proceed with cleanup?"):
        manager._cleanup_old_backups(keep)
        click.echo("✅ Cleanup completed!")
    else:
        click.echo("Cleanup cancelled.")

def register_backup_commands(app):
    """Register backup commands with the Flask app."""
    app.cli.add_command(backup) 