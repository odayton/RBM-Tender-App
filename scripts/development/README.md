# Migration Tools

This folder contains tools and documentation for managing database migrations in the RBM Tender App.

## Files

### `test_migrations.py`
A comprehensive test script that validates the migration system functionality:
- Checks migration file structure
- Tests all migration commands
- Validates database connectivity
- Tests backup and restore functionality

**Usage:**
```bash
python migration_tools/test_migrations.py
```

### `MIGRATION_GUIDE.md`
Complete documentation for the migration system including:
- Overview of the robust migration system
- CLI commands and usage
- Best practices
- Troubleshooting guide
- Safety features

## Migration System Features

The RBM Tender App now has a robust migration system with:

### Core Commands
- `flask migrate status` - Check migration status
- `flask migrate upgrade` - Run migrations with automatic backup
- `flask migrate rollback` - Rollback migrations safely
- `flask migrate create` - Create new migrations

### Utility Commands
- `flask migrate validate` - Validate migration files
- `flask migrate backup` - Create manual backup
- `flask migrate restore` - Restore from backup
- `flask migrate cleanup` - Clean up old backups
- `flask migrate history` - Show migration history
- `flask migrate info` - Show detailed information

### Safety Features
- Automatic database backups before migrations
- Migration file validation
- Database connection validation
- Rollback safety checks
- Comprehensive error handling

## Migration Files Location

The actual migration files are located in:
- `migrations/versions/` - Migration version files
- `migrations/backups/` - Database backups
- `migrations/env.py` - Alembic environment configuration

## Notes

- The migration system is now production-ready and handles Windows console encoding issues
- All temporary fix scripts have been removed as they are no longer needed
- The system automatically creates backups before running migrations
- Migration validation ensures all files are properly structured 