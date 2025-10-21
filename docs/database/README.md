# Database Documentation

This directory contains comprehensive documentation for database operations, migrations, and maintenance.

## Quick Links

### Core Documentation
- **[Migration Workflow](./DATABASE_MIGRATION_WORKFLOW.md)** - Complete guide to creating and deploying migrations
- **[Schema Repair Guide](./SCHEMA_REPAIR_GUIDE.md)** - ⭐ NEW: Fix schema mismatches and sync issues
- **[Migration Checklist](./MIGRATION_CHECKLIST.md)** - Step-by-step checklist for safe migrations
- **[Migration Setup Summary](./MIGRATION_SETUP_SUMMARY.md)** - Overview of migration system setup

## Quick Fixes

### Getting "column does not exist" errors?
```bash
py manage.py fix-schema
```
See [Schema Repair Guide](./SCHEMA_REPAIR_GUIDE.md) for details.

### Migration says "column already exists"?
```bash
py manage.py fix-schema --check-only  # Check what's wrong
py manage.py db-stamp head             # Sync migration history
```

### Database won't start or migrate?
1. Check the logs: `Get-Content app/instance/logs/errors.log -Tail 50`
2. Verify connection: `py manage.py info`
3. Check migration status: `flask db current`

## Common Commands

```bash
# Schema Repair
py manage.py fix-schema                 # Check and fix schema issues
py manage.py fix-schema --check-only    # Check only

# Migrations
py manage.py db-upgrade                 # Apply pending migrations
py manage.py db-migrate "message"       # Create new migration
py manage.py db-stamp head              # Mark as current

# Information
flask db current                        # Current migration version
flask migrate status                    # Detailed status
py manage.py info                       # App configuration
```

## Document Overview

### [DATABASE_MIGRATION_WORKFLOW.md](./DATABASE_MIGRATION_WORKFLOW.md)
Complete workflow documentation covering:
- Migration creation rules and best practices
- Testing workflows for local and pre-production
- Deployment process with safety checks
- Troubleshooting common issues
- **NEW: Schema synchronization and repair**
- Quick reference commands

### [SCHEMA_REPAIR_GUIDE.md](./SCHEMA_REPAIR_GUIDE.md) ⭐ NEW
Dedicated guide for fixing schema mismatches:
- When to use schema repair
- Command options and usage
- Adding tables to verification
- Common scenarios with solutions
- Example output
- Best practices

### [MIGRATION_CHECKLIST.md](./MIGRATION_CHECKLIST.md)
Step-by-step checklist for safe database migrations with verification points at each stage.

### [MIGRATION_SETUP_SUMMARY.md](./MIGRATION_SETUP_SUMMARY.md)
Overview of the migration system setup and configuration.

### [MIGRATION_WORKFLOW_DIAGRAM.md](./MIGRATION_WORKFLOW_DIAGRAM.md)
Visual representation of the migration workflow process.

## Getting Help

If you encounter issues not covered in these documents:

1. Check application logs: `app/instance/logs/`
2. Review recent migrations: `migrations/versions/`
3. Verify database connection: `py manage.py info`
4. Check migration history: `flask db current`

For emergency database issues, see the [Operational Runbooks](../runbooks/OPERATIONAL_RUNBOOKS.md).

