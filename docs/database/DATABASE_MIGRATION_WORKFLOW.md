# Database Migration Workflow

## Overview
This document defines the standardized workflow for creating, testing, and deploying database migrations to prevent corruption and maintain consistency across environments.

---

## 1. Migration Creation Rules

### 1.1 Naming Conventions
- **Format**: Use descriptive, lowercase names with underscores
- **Examples**:
  - `add_pump_model_fields`
  - `create_customer_history_table`
  - `modify_deal_status_enum`
- **Avoid**: Generic names like `update_tables` or `fix_database`

### 1.2 One Purpose Per Migration
- Each migration should address a single, specific change
- ✅ **Good**: `add_email_verification_to_users`
- ❌ **Bad**: `update_users_and_deals_and_add_products`

### 1.3 Model Import Rules
```python
# ALWAYS import models at the top of your migration file
from app.models import User, Deal, Product

# NEVER use string references for complex operations
# Instead, import the actual model classes
```

### 1.4 Required Components
Every migration file MUST include:
- `revision` identifier
- `down_revision` (parent migration)
- `upgrade()` function
- `downgrade()` function (for rollback capability)

---

## 2. Migration Creation Workflow

### Step 1: Model Changes
```bash
# 1. Make changes to your model files
# 2. Save all changes
# 3. Verify models import without errors
py -c "from app.models import *"
```

### Step 2: Create Migration
```bash
# Using custom command (recommended)
flask migrate create "descriptive_migration_name"

# OR using standard Flask-Migrate
flask db migrate -m "descriptive_migration_name"
```

### Step 3: Review Generated Migration
**Critical Review Checklist**:
- [ ] Review the generated file in `migrations/versions/`
- [ ] Verify all expected changes are present
- [ ] Check for any unexpected changes
- [ ] Ensure `downgrade()` properly reverses `upgrade()`
- [ ] Look for data loss risks (dropping columns/tables)
- [ ] Verify constraint names are unique
- [ ] Check for index naming conflicts

### Step 4: Manual Adjustments
Common adjustments needed:
```python
# Add data migrations if needed
def upgrade():
    # Schema changes first
    op.add_column('users', sa.Column('status', sa.String(20)))
    
    # Then data migrations
    op.execute("UPDATE users SET status = 'active' WHERE is_active = true")

# Always make downgrade mirror upgrade
def downgrade():
    # Reverse in opposite order
    op.drop_column('users', 'status')
```

---

## 3. Testing Workflow

### 3.1 Local Testing (Development Environment)

#### Phase 1: Fresh Database Test
```bash
# 1. Create backup of current database
flask migrate backup -d "before_testing_new_migration"

# 2. Test upgrade
flask migrate upgrade

# 3. Verify database state
flask migrate status
py scripts/development/verify_schema.py  # If available

# 4. Test the application
py app_runner.py
# Manually test affected features
```

#### Phase 2: Rollback Test
```bash
# 1. Test downgrade
flask migrate rollback

# 2. Verify database state
flask migrate status

# 3. Re-apply upgrade
flask migrate upgrade

# 4. Confirm everything works
flask migrate status
```

#### Phase 3: Data Integrity Test
```bash
# 1. Add test data
# 2. Run migration
# 3. Verify test data is preserved
# 4. Check foreign key relationships
# 5. Verify constraints are enforced
```

### 3.2 Pre-Production Testing
Before deploying to production:
```bash
# 1. Create a production-like database dump
flask migrate backup -d "production_clone_test"

# 2. Restore to test environment
flask migrate restore backups/production_clone_test.sql

# 3. Run migrations on production data
flask migrate upgrade

# 4. Verify no errors
# 5. Check data integrity
```

---

## 4. Code Review Checklist

Before committing migrations, verify:

### Schema Changes
- [ ] Column types are appropriate for data
- [ ] Nullable constraints are correct
- [ ] Default values are set where needed
- [ ] Indexes are added for foreign keys
- [ ] Unique constraints are properly defined

### Data Safety
- [ ] No unintended data loss
- [ ] Existing data is preserved or migrated
- [ ] Foreign key relationships maintained
- [ ] Check constraints don't invalidate existing data

### Performance
- [ ] Large table alterations use batch operations
- [ ] Indexes added for commonly queried columns
- [ ] No full table scans for data migrations
- [ ] Consider adding indexes before populating data

### Rollback Safety
- [ ] `downgrade()` truly reverses `upgrade()`
- [ ] Data can be recovered after rollback
- [ ] No destructive operations without backup

---

## 5. Deployment Process

### 5.1 Pre-Deployment Checklist
- [ ] All tests pass locally
- [ ] Migration reviewed by at least one other person
- [ ] Backup strategy confirmed
- [ ] Rollback plan documented
- [ ] Estimated downtime calculated (if any)
- [ ] Communication plan for users (if needed)

### 5.2 Production Deployment Steps

#### Step 1: Create Production Backup
```bash
# On production server
flask migrate backup -d "before_migration_$(date +%Y%m%d_%H%M%S)"

# Verify backup was created
ls -lh migrations/backups/
```

#### Step 2: Validate Current State
```bash
# Check current migration version
flask migrate status

# Validate migration files
flask migrate validate
```

#### Step 3: Apply Migration
```bash
# Run with backup (recommended)
flask migrate upgrade --backup

# Monitor output for errors
# Check application logs
```

#### Step 4: Verify Deployment
```bash
# Check new version
flask migrate status

# Verify application starts
sudo systemctl status rbm-tender-app  # Adjust service name

# Test critical functionality
# Check application logs for errors
```

### 5.3 Rollback Procedure (If Needed)
```bash
# Option 1: Rollback via migration
flask migrate rollback

# Option 2: Restore from backup (if migration rollback fails)
flask migrate restore migrations/backups/backup_YYYYMMDD_HHMMSS.sql

# Restart application
sudo systemctl restart rbm-tender-app
```

---

## 6. Common Patterns & Solutions

### 6.1 Adding a Column with Default Value
```python
def upgrade():
    # Add column as nullable first
    op.add_column('table_name', 
        sa.Column('new_column', sa.String(50), nullable=True))
    
    # Set default values for existing rows
    op.execute("UPDATE table_name SET new_column = 'default_value' WHERE new_column IS NULL")
    
    # Make column non-nullable if needed
    op.alter_column('table_name', 'new_column', nullable=False)

def downgrade():
    op.drop_column('table_name', 'new_column')
```

### 6.2 Renaming a Column
```python
def upgrade():
    # SQLite doesn't support RENAME COLUMN directly
    # Use batch mode for SQLite compatibility
    with op.batch_alter_table('table_name') as batch_op:
        batch_op.alter_column('old_name', new_column_name='new_name')

def downgrade():
    with op.batch_alter_table('table_name') as batch_op:
        batch_op.alter_column('new_name', new_column_name='old_name')
```

### 6.3 Creating Enum Types (PostgreSQL)
```python
def upgrade():
    # Create enum type
    deal_status = sa.Enum('draft', 'pending', 'approved', 'rejected', 
                          name='deal_status_enum')
    deal_status.create(op.get_bind(), checkfirst=True)
    
    # Add column using enum
    op.add_column('deals', 
        sa.Column('status', deal_status, nullable=False))

def downgrade():
    op.drop_column('deals', 'status')
    
    # Drop enum type
    sa.Enum(name='deal_status_enum').drop(op.get_bind(), checkfirst=True)
```

### 6.4 Large Table Migrations
```python
def upgrade():
    # For large tables, add index BEFORE populating data
    op.create_index('idx_deals_customer_id', 'deals', ['customer_id'])
    
    # Use batch updates for large data migrations
    connection = op.get_bind()
    
    # Process in chunks
    batch_size = 1000
    offset = 0
    
    while True:
        result = connection.execute(f"""
            UPDATE deals 
            SET processed = true 
            WHERE id IN (
                SELECT id FROM deals 
                WHERE processed = false 
                LIMIT {batch_size} OFFSET {offset}
            )
        """)
        
        if result.rowcount == 0:
            break
        offset += batch_size
```

---

## 7. Environment-Specific Considerations

### 7.1 Development
- Rapid iteration allowed
- Can reset database if needed
- Test rollbacks frequently

### 7.2 Production (AWS EC2 PostgreSQL)
- **ALWAYS** create backup before migration
- Test on production clone first
- Plan for potential downtime
- Have rollback plan ready
- Monitor application after deployment

### 7.3 Migration Conflicts
If multiple developers create migrations:
```bash
# 1. Update from main branch
git pull origin main

# 2. Check for migration conflicts
ls migrations/versions/

# 3. If parallel migrations exist, merge them
flask db merge -m "merge_parallel_migrations"

# 4. Review and test merged migration
```

---

## 8. Troubleshooting

### Problem: Migration fails mid-execution
```bash
# Check current state
flask migrate status

# Check database for partial changes
# Manually verify tables/columns

# Option 1: Complete manually, then stamp version
flask db stamp head

# Option 2: Restore from backup
flask migrate restore backups/backup_file.sql
```

### Problem: Alembic version table is out of sync
```bash
# Check current database state
flask db current

# Option 1: Use fix-schema to sync everything (recommended)
py manage.py fix-schema

# Option 2: Manually stamp correct version
py manage.py db-stamp <revision_id>

# Verify
flask migrate status
```

### Problem: Column already exists error during migration
**Error**: `psycopg2.errors.DuplicateColumn: column "X" of relation "Y" already exists`

This means your database has the column but Alembic thinks it doesn't.

```bash
# Solution 1: Check what's out of sync and fix
py manage.py fix-schema --check-only
py manage.py fix-schema

# Solution 2: If schema is correct, just update migration history
py manage.py db-stamp head
```

### Problem: Column does not exist (500 error in application)
**Error**: `sqlalchemy.exc.ProgrammingError: column X.Y does not exist`

Your model references a column that isn't in the database.

```bash
# Solution: Add missing columns and sync
py manage.py fix-schema

# Then verify application works
py wsgi.py  # or your app runner
```

### Problem: Migration creates duplicate indexes/constraints
```python
# Use checkfirst parameter
op.create_index('idx_name', 'table', ['column'], unique=False, 
                if_not_exists=True)  # PostgreSQL 9.5+

# Or check before creating
from sqlalchemy import inspect

def upgrade():
    conn = op.get_bind()
    inspector = inspect(conn)
    
    existing_indexes = [idx['name'] for idx in inspector.get_indexes('table_name')]
    
    if 'idx_name' not in existing_indexes:
        op.create_index('idx_name', 'table_name', ['column'])
```

---

## 9. Schema Synchronization and Repair

### 9.1 When to Use Schema Repair

Use the `fix-schema` command when:
- Migration history is out of sync with actual database schema
- Columns exist in models but not in database (causing 500 errors)
- Manual database changes were made outside of migrations
- Migrating from an older version without complete migration history
- Database was restored from backup with different migration state

### 9.2 Schema Repair Command

The `fix-schema` command automatically detects and fixes schema mismatches:

```bash
# Check and fix all schema issues (recommended)
py manage.py fix-schema

# Only check for issues without applying fixes
py manage.py fix-schema --check-only

# Fix issues but don't update migration history
py manage.py fix-schema --no-stamp
```

### 9.3 How Schema Repair Works

The command performs the following steps:

1. **Inspection**: Compares database schema with expected schema defined in models
2. **Detection**: Identifies missing columns, tables, or other schema elements
3. **Reporting**: Lists all found issues with details
4. **Fixing**: Adds missing columns/elements (if not in check-only mode)
5. **Stamping**: Updates migration history to 'head' (if not using --no-stamp)

### 9.4 Adding Tables to Schema Verification

To add more tables for verification, edit `manage.py` and update the `expected_schema` dictionary:

```python
expected_schema = {
    'quote_line_items': [
        ('assembly_metadata', 'TEXT', True),
        ('list_price', 'NUMERIC(10, 2)', True),
    ],
    'your_table_name': [
        ('column_name', 'COLUMN_TYPE', is_nullable),
        ('email', 'VARCHAR(120)', False),
        ('status', 'VARCHAR(20)', True),
    ],
}
```

Format: `(column_name, SQL_type, nullable_boolean)`

### 9.5 Common Schema Mismatch Scenarios

#### Scenario 1: Migration Failed Partially
**Symptom**: 500 errors, column does not exist
```bash
# Solution
py manage.py fix-schema
```

#### Scenario 2: Manual Database Changes
**Symptom**: Alembic thinks migration is needed but column exists
```bash
# Check what's different
py manage.py fix-schema --check-only

# If schema is actually correct, just update history
py manage.py db-stamp head
```

#### Scenario 3: Development Environment Out of Sync
**Symptom**: Different developers have different database states
```bash
# Pull latest code
git pull origin main

# Fix schema to match models
py manage.py fix-schema

# Verify everything is in sync
py manage.py db-upgrade
```

### 9.6 Prevention Best Practices

To avoid schema mismatches:

1. **Always Use Migrations**: Never manually alter production database schema
2. **Test Migrations Locally**: Run `py manage.py db-upgrade` after pulling code
3. **Check Status Regularly**: Run `flask migrate status` to verify state
4. **Use Version Control**: Commit migration files with model changes
5. **Document Manual Changes**: If emergency manual changes are needed, document them immediately and create corresponding migration

### 9.7 Manual Stamping

If you need to manually set the migration version without running migrations:

```bash
# Stamp to latest version
py manage.py db-stamp head

# Stamp to specific version
py manage.py db-stamp <revision_id>

# Check current version
flask db current
```

**Use Cases for Manual Stamping**:
- Database schema is correct but migration history is wrong
- Restoring from backup with different migration state
- After manual schema fixes
- Initializing migration tracking on existing database

---

## 10. Best Practices Summary

### DO:
✅ Create descriptive migration names
✅ Test migrations locally before deploying
✅ Always create backups before production migrations
✅ Write reversible migrations (proper downgrade functions)
✅ Review generated migrations before committing
✅ Test rollback procedures
✅ Document complex migrations
✅ Use batch operations for large tables
✅ Add indexes for foreign keys

### DON'T:
❌ Skip testing migrations
❌ Deploy to production without backup
❌ Create empty downgrade() functions
❌ Ignore migration validation errors
❌ Make multiple unrelated changes in one migration
❌ Assume autogenerated migrations are perfect
❌ Drop columns without verifying they're unused
❌ Rush production deployments

---

## 11. Quick Reference Commands

```bash
# Status and Information
flask migrate status                    # Current migration state
flask migrate history                   # Migration history
flask migrate info                      # Detailed information
flask migrate validate                  # Validate migration files

# Creating Migrations
py manage.py db-migrate "message"       # Create new migration (custom command)
flask db migrate -m "message"           # Alternative (Flask-Migrate)

# Applying Migrations
py manage.py db-upgrade                 # Apply all pending migrations (custom command)
flask db upgrade                        # Alternative (Flask-Migrate)
flask migrate upgrade --backup          # Apply with automatic backup

# Rollback
flask migrate rollback                  # Rollback one migration
flask migrate rollback -r <revision>    # Rollback to specific revision
flask db downgrade                      # Alternative (Flask-Migrate)

# Schema Repair and Synchronization (NEW)
py manage.py fix-schema                 # Check and fix schema mismatches
py manage.py fix-schema --check-only    # Check only, don't apply fixes
py manage.py fix-schema --no-stamp      # Fix without updating migration history
py manage.py db-stamp head              # Manually stamp as current
py manage.py db-stamp <revision>        # Manually stamp to specific revision

# Backup and Restore
flask migrate backup -d "description"   # Create backup
flask migrate restore <path>            # Restore from backup
flask migrate cleanup -k 10             # Keep 10 most recent backups

# Development
flask db current                        # Show current revision
flask db stamp <revision>               # Manually set migration version
flask db merge                          # Merge parallel migrations
```

---

## 12. Integration with Git Workflow

### Before Committing
```bash
# 1. Ensure migration is tested
flask migrate validate

# 2. Stage migration files
git add migrations/versions/<new_migration>.py

# 3. Commit with descriptive message
git commit -m "feat: Add email verification fields to users

- Added email_verified boolean column
- Added verification_token column
- Added verified_at timestamp
- Updated user model

Migration: abc123_add_email_verification_to_users"

# 4. Push to repository
git push origin your-branch
```

### After Merging to Main
```bash
# On production server
git pull origin main
flask migrate status
flask migrate upgrade --backup
sudo systemctl restart rbm-tender-app
```

---

## 13. Additional Resources

- **Flask-Migrate Documentation**: https://flask-migrate.readthedocs.io/
- **Alembic Documentation**: https://alembic.sqlalchemy.org/
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/

---

## Appendix: Migration File Template

```python
"""Add description of changes

Revision ID: <auto-generated>
Revises: <parent-revision>
Create Date: <timestamp>

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '<auto-generated>'
down_revision = '<parent-revision>'
branch_labels = None
depends_on = None


def upgrade():
    """
    Apply the database schema changes.
    
    Changes:
    - List each change clearly
    - Explain any data migrations
    - Note any potential issues
    """
    # Schema changes
    pass
    

def downgrade():
    """
    Reverse the database schema changes.
    
    Reverses:
    - List what gets reversed
    - Explain any data restoration
    - Note any caveats
    """
    # Reverse schema changes in opposite order
    pass
```

