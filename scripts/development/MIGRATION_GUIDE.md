# RBM Tender App - Migration Guide

This guide provides comprehensive information about the robust migration system implemented for the RBM Tender App.

## Table of Contents

1. [Overview](#overview)
2. [Migration System Features](#migration-system-features)
3. [Getting Started](#getting-started)
4. [CLI Commands](#cli-commands)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)
7. [Safety Features](#safety-features)
8. [Backup and Recovery](#backup-and-recovery)
9. [Advanced Usage](#advanced-usage)

## Overview

The RBM Tender App uses a robust migration system built on Flask-Migrate and Alembic with enhanced safety features, automatic backups, and comprehensive validation.

### Key Features

- ✅ **Automatic Backups**: Creates database backups before migrations
- ✅ **Safety Validation**: Checks for dangerous operations and data loss risks
- ✅ **Comprehensive Logging**: Detailed logging for debugging and monitoring
- ✅ **Rollback Capabilities**: Easy rollback to previous versions
- ✅ **CLI Commands**: User-friendly command-line interface
- ✅ **Error Recovery**: Robust error handling and recovery mechanisms

## Migration System Features

### 1. Enhanced Environment (`migrations/env.py`)

The migration environment has been completely rewritten with:

- **Comprehensive Error Handling**: Better error messages and debugging information
- **Database Connection Validation**: Verifies database connectivity before migrations
- **Model Import Validation**: Ensures all models are properly imported
- **Automatic Backups**: Creates timestamped backups before migrations
- **Enhanced Logging**: Detailed logging with emojis for better readability

### 2. Migration Manager (`app/utils/db_utils/migration_manager.py`)

A comprehensive migration management utility providing:

- **Migration Validation**: Checks migration files for common issues
- **Status Monitoring**: Detailed migration status and history
- **Backup Management**: Automatic backup creation and restoration
- **Rollback Support**: Safe rollback to previous versions
- **Cleanup Utilities**: Automatic cleanup of old backup files

### 3. Safety Checker (`app/utils/db_utils/migration_safety.py`)

Advanced safety validation including:

- **Dangerous Operation Detection**: Identifies potentially harmful operations
- **Data Loss Risk Assessment**: Warns about operations that might cause data loss
- **Constraint Validation**: Checks for constraint-related issues
- **Foreign Key Validation**: Validates foreign key relationships
- **Dependency Checking**: Ensures migration dependencies are satisfied

## Getting Started

### Prerequisites

1. Ensure you have the latest version of the application
2. Activate your virtual environment
3. Make sure your database is accessible

### Basic Migration Workflow

```bash
# 1. Check migration status
flask migrate status

# 2. Create a new migration (if needed)
flask migrate create "Add new feature"

# 3. Validate the migration
flask migrate validate

# 4. Run migrations
flask migrate upgrade

# 5. Verify the migration
flask migrate status
```

## CLI Commands

### Core Commands

#### `flask migrate status`
Shows current migration status and information.

```bash
flask migrate status
```

**Output:**
```
🔍 Checking migration status...

📊 Migration Status:
  Current Version: 1e645907263d
  Files Valid: ✅
  Available Migrations: 3
  Backup Files: 2
```

#### `flask migrate upgrade`
Runs database migrations with automatic backup.

```bash
# Basic upgrade
flask migrate upgrade

# Upgrade with custom message
flask migrate upgrade --message "Production deployment"

# Upgrade without backup (not recommended)
flask migrate upgrade --no-backup
```

#### `flask migrate rollback`
Rolls back migrations.

```bash
# Rollback one step
flask migrate rollback

# Rollback to specific revision
flask migrate rollback --revision 1e645907263d
```

#### `flask migrate create`
Creates a new migration.

```bash
flask migrate create "Add user preferences table"
```

### Utility Commands

#### `flask migrate validate`
Validates migration files for issues.

```bash
flask migrate validate
```

#### `flask migrate backup`
Creates a manual database backup.

```bash
# Basic backup
flask migrate backup

# Backup with description
flask migrate backup --description "Before major update"
```

#### `flask migrate restore`
Restores database from backup.

```bash
flask migrate restore migrations/backups/backup_20241201_143022_rbm_tender_app.db
```

#### `flask migrate cleanup`
Cleans up old backup files.

```bash
# Keep 10 most recent backups (default)
flask migrate cleanup

# Keep only 5 most recent backups
flask migrate cleanup --keep 5
```

#### `flask migrate history`
Shows detailed migration history.

```bash
flask migrate history
```

#### `flask migrate info`
Shows comprehensive migration information.

```bash
flask migrate info
```

## Best Practices

### 1. Always Create Backups

```bash
# Automatic backup (recommended)
flask migrate upgrade

# Manual backup before major changes
flask migrate backup --description "Before schema changes"
```

### 2. Validate Before Applying

```bash
# Check migration safety
flask migrate validate

# Review warnings and recommendations
flask migrate info
```

### 3. Test Migrations in Development

```bash
# Use testing mode for development
python app_runner.py
# Select option 3: Testing Mode
```

### 4. Use Descriptive Migration Messages

```bash
# Good
flask migrate create "Add user preferences and settings tables"

# Bad
flask migrate create "fix"
```

### 5. Review Migration Files

Always review generated migration files before applying:

```python
# Check for dangerous operations
op.drop_table('users')  # ⚠️ Dangerous!

# Check for data loss risks
op.alter_column('users', 'email', type_=sa.String(50))  # ⚠️ May truncate data
```

### 6. Monitor Migration Logs

Watch for warnings and errors in the migration output:

```
⚠️  Adding NOT NULL constraint to existing column may fail if data exists
⚠️  Creating indexes on large tables may take significant time
```

## Troubleshooting

### Common Issues

#### 1. Migration Validation Fails

**Problem:** `flask migrate validate` reports errors

**Solution:**

```bash
# Check migration files
flask migrate info

# Review specific errors
flask migrate status

# Fix issues in migration files
# Re-run validation
flask migrate validate
```

#### 2. Migration Fails During Upgrade

**Problem:** Migration fails with database errors

**Solution:**

```bash
# Check current status
flask migrate status

# Review error logs
# Restore from backup if needed
flask migrate restore <backup_file>

# Fix the issue and retry
flask migrate upgrade
```

#### 3. Model Import Errors

**Problem:** "Model not found" errors during migration

**Solution:**

```bash
# Check model imports in migrations/env.py
# Ensure all models are properly imported
# Verify model file paths
```

#### 4. Database Connection Issues

**Problem:** Cannot connect to database during migration

**Solution:**

```bash
# Check database configuration
# Verify database file exists
# Check file permissions
# Ensure no other processes are using the database
```

#### 5. Migration File Encoding Issues

**Problem:** `'charmap' codec can't decode byte` errors when reading migration files

**Solution:**

```bash
# Run the encoding fix script
python fix_migration_encoding.py

# Or manually fix the file encoding
# Open the migration file in a text editor and save as UTF-8
```

### Error Recovery

#### Automatic Recovery

The migration system includes automatic recovery features:

1. **Automatic Backups**: Created before each migration
2. **Transaction Rollback**: Failed migrations are automatically rolled back
3. **Error Logging**: Detailed error information for debugging

#### Manual Recovery

```bash
# 1. Check available backups
ls migrations/backups/

# 2. Restore from backup
flask migrate restore migrations/backups/backup_20241201_143022_rbm_tender_app.db

# 3. Verify restoration
flask migrate status

# 4. Fix the issue and retry migration
flask migrate upgrade
```

## Safety Features

### 1. Dangerous Operation Detection

The system automatically detects and warns about:

- Table drops (`op.drop_table()`)
- Column drops (`op.drop_column()`)
- Index drops (`op.drop_index()`)
- Constraint drops (`op.drop_constraint()`)
- Direct SQL operations (`op.execute()`)

### 2. Data Loss Risk Assessment

Warns about operations that might cause data loss:

- VARCHAR length reductions
- Type conversions that might truncate data
- NOT NULL constraint additions to existing columns
- Unique constraint additions to existing data

### 3. Constraint Validation

Checks for constraint-related issues:

- Foreign key additions to missing tables
- Constraint drops affecting data integrity
- Index operations on large tables

### 4. Dependency Checking

Validates migration dependencies:

- Ensures down_revision files exist
- Checks migration chain integrity
- Validates revision relationships

## Backup and Recovery

### Automatic Backups

Backups are automatically created:

- Before each migration upgrade
- With timestamped filenames
- Stored in `migrations/backups/` directory

### Backup Naming Convention

```
backup_YYYYMMDD_HHMMSS_description_database.db
```

Example:
```
backup_20241201_143022_before_user_update_rbm_tender_app.db
```

### Manual Backup Management

```bash
# Create manual backup
flask migrate backup --description "Before major changes"

# List available backups
ls migrations/backups/

# Restore from backup
flask migrate restore migrations/backups/backup_20241201_143022_rbm_tender_app.db

# Clean up old backups
flask migrate cleanup --keep 5
```

### Backup Best Practices

1. **Keep Multiple Backups**: Don't rely on a single backup
2. **Test Restorations**: Periodically test backup restoration
3. **Offsite Storage**: Consider storing backups in a different location
4. **Regular Cleanup**: Clean up old backups to save space

## Advanced Usage

### Custom Migration Scripts

You can create custom migration scripts for complex operations:

```python
# migrations/versions/custom_migration.py
def upgrade():
    # Custom upgrade logic
    op.execute("UPDATE users SET status = 'active' WHERE status IS NULL")
    
def downgrade():
    # Custom downgrade logic
    op.execute("UPDATE users SET status = NULL WHERE status = 'active'")
```

### Migration Testing

Test migrations in a safe environment:

```bash
# Use testing mode
python app_runner.py
# Select option 3: Testing Mode

# Run migrations
flask migrate upgrade

# Verify results
flask migrate status

# Test rollback
flask migrate rollback
```

### Production Deployment

For production deployments:

1. **Create Backup**: `flask migrate backup --description "Before production deployment"`
2. **Validate**: `flask migrate validate`
3. **Test**: Run migrations in staging environment
4. **Deploy**: Run migrations in production
5. **Verify**: `flask migrate status`

### Monitoring and Logging

Monitor migration operations:

```bash
# Check migration logs
tail -f logs/app.log | grep -i migration

# Monitor backup creation
ls -la migrations/backups/

# Check database size
du -h app/instance/rbm_tender_app.db
```

## Configuration

### Environment Variables

```bash
# Database URL
DATABASE_URL=sqlite:///app/instance/rbm_tender_app.db

# Migration settings
FLASK_CONFIG=development
```

### Migration Configuration

The migration system uses the following configuration files:

- `migrations/alembic.ini`: Alembic configuration
- `migrations/env.py`: Migration environment
- `app/utils/db_utils/migration_manager.py`: Migration manager
- `app/utils/db_utils/migration_safety.py`: Safety checker

## Support

If you encounter issues with migrations:

1. Check this guide for common solutions
2. Review the migration logs for detailed error information
3. Use the validation commands to identify issues
4. Restore from backup if needed
5. Contact the development team for complex issues

## Migration Checklist

Before running migrations in production:

- [ ] Test migrations in development environment
- [ ] Create manual backup
- [ ] Validate migration files
- [ ] Review migration warnings
- [ ] Ensure database connectivity
- [ ] Check available disk space
- [ ] Notify team members
- [ ] Have rollback plan ready

After running migrations:

- [ ] Verify migration success
- [ ] Check application functionality
- [ ] Monitor for errors
- [ ] Update documentation
- [ ] Clean up old backups (if needed) 