"""
Migration CLI Commands

This module provides Flask CLI commands for robust migration management.
"""

import click
from flask.cli import with_appcontext
from app.utils.db_utils.migration_manager import migration_manager

@click.group()
def migrate():
    """Database migration commands."""
    pass

@migrate.command()
@with_appcontext
def status():
    """Show migration status and information."""
    click.echo("Checking migration status...")
    
    status_info = migration_manager.get_migration_status()
    
    click.echo("\nMigration Status:")
    click.echo(f"  Current Version: {status_info.get('current_version', 'None')}")
    click.echo(f"  Files Valid: {'OK' if status_info.get('files_valid') else 'ERROR'}")
    click.echo(f"  Available Migrations: {len(status_info.get('available_migrations', []))}")
    click.echo(f"  Backup Files: {status_info.get('backups_count', 0)}")
    
    if status_info.get('validation_errors'):
        click.echo("\nValidation Errors:")
        for error in status_info['validation_errors']:
            click.echo(f"  - {error}")
    
    if status_info.get('migration_history'):
        click.echo("\nMigration History:")
        for migration in status_info['migration_history']:
            click.echo(f"  - {migration['version']}")

@migrate.command()
@click.option('--message', '-m', help='Migration message')
@click.option('--backup/--no-backup', default=True, help='Create backup before migration')
@with_appcontext
def upgrade(message="", backup=True):
    """Run database migrations."""
    click.echo("Starting migration upgrade...")
    
    if backup:
        click.echo("Creating backup...")
    
    success = migration_manager.migrate(message=message, create_backup=backup)
    
    if success:
        click.echo("Migration completed successfully!")
    else:
        click.echo("Migration failed!")
        raise click.Abort()

@migrate.command()
@click.option('--revision', '-r', help='Target revision to rollback to')
@with_appcontext
def rollback(revision=None):
    """Rollback database migrations."""
    if revision:
        click.echo(f"Rolling back to revision: {revision}")
    else:
        click.echo("Rolling back one step...")
    
    success = migration_manager.rollback(target_revision=revision)
    
    if success:
        click.echo("Rollback completed successfully!")
    else:
        click.echo("Rollback failed!")
        raise click.Abort()

@migrate.command()
@click.argument('message')
@with_appcontext
def create(message):
    """Create a new migration."""
    click.echo(f"Creating new migration: {message}")
    
    success = migration_manager.create_migration(message)
    
    if success:
        click.echo("Migration created successfully!")
    else:
        click.echo("Failed to create migration!")
        raise click.Abort()

@migrate.command()
@with_appcontext
def validate():
    """Validate migration files."""
    click.echo("Validating migration files...")
    
    is_valid, errors = migration_manager.validate_migration_files()
    
    if is_valid:
        click.echo("All migration files are valid!")
    else:
        click.echo("Migration validation failed:")
        for error in errors:
            click.echo(f"  - {error}")
        raise click.Abort()

@migrate.command()
@click.option('--description', '-d', help='Backup description')
@with_appcontext
def backup(description=""):
    """Create a database backup."""
    click.echo("Creating database backup...")
    
    backup_path = migration_manager.create_backup(description)
    
    if backup_path:
        click.echo(f"Backup created: {backup_path}")
    else:
        click.echo("Failed to create backup!")
        raise click.Abort()

@migrate.command()
@click.argument('backup_path')
@with_appcontext
def restore(backup_path):
    """Restore database from backup."""
    click.echo(f"Restoring database from: {backup_path}")
    
    success = migration_manager.restore_backup(backup_path)
    
    if success:
        click.echo("Database restored successfully!")
    else:
        click.echo("Failed to restore database!")
        raise click.Abort()

@migrate.command()
@click.option('--keep', '-k', default=10, help='Number of backups to keep')
@with_appcontext
def cleanup(keep=10):
    """Clean up old backup files."""
    click.echo(f"Cleaning up old backups (keeping {keep} most recent)...")
    
    removed_count = migration_manager.cleanup_old_backups(keep)
    
    click.echo(f"Cleaned up {removed_count} old backup files!")

@migrate.command()
@with_appcontext
def history():
    """Show detailed migration history."""
    click.echo("Migration History:")
    
    history = migration_manager.get_migration_history()
    current_version = migration_manager.get_current_version()
    
    if not history:
        click.echo("  No migration history found.")
        return
    
    for i, migration in enumerate(history):
        version = migration['version']
        location = migration.get('location', 'Unknown')
        
        # Mark current version
        if version == current_version:
            click.echo(f"  {i+1}. {version} (CURRENT) - {location}")
        else:
            click.echo(f"  {i+1}. {version} - {location}")

@migrate.command()
@with_appcontext
def info():
    """Show detailed migration information."""
    click.echo("Migration Information:")
    
    status_info = migration_manager.get_migration_status()
    
    click.echo(f"\nConfiguration:")
    click.echo(f"  Migrations Directory: {migration_manager.migrations_dir}")
    click.echo(f"  Backups Directory: {migration_manager.backups_dir}")
    
    click.echo(f"\nCurrent State:")
    click.echo(f"  Current Version: {status_info.get('current_version', 'None')}")
    click.echo(f"  Files Valid: {'OK' if status_info.get('files_valid') else 'ERROR'}")
    
    click.echo(f"\nFiles:")
    click.echo(f"  Available Migrations: {len(status_info.get('available_migrations', []))}")
    click.echo(f"  Backup Files: {status_info.get('backups_count', 0)}")
    
    if status_info.get('available_migrations'):
        click.echo(f"\nMigration Files:")
        for migration in status_info['available_migrations']:
            click.echo(f"  - {migration}")
    
    if status_info.get('validation_errors'):
        click.echo(f"\nIssues:")
        for error in status_info['validation_errors']:
            click.echo(f"  - {error}")

def register_migration_commands(app):
    """Register migration commands with the Flask app."""
    app.cli.add_command(migrate) 