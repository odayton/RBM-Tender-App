# Database Schema Repair Guide

## Quick Start

If you're getting a 500 error with "column does not exist" or migration errors with "column already exists", run:

```bash
py manage.py fix-schema
```

This command will automatically detect and fix schema mismatches between your database and model definitions.

---

## When to Use Schema Repair

Use the `fix-schema` command when you encounter:

### 1. Application Errors
- **500 Internal Server Error** when accessing pages
- Error: `sqlalchemy.exc.ProgrammingError: column X.Y does not exist`
- Missing columns referenced in models

### 2. Migration Errors
- Error: `psycopg2.errors.DuplicateColumn: column "X" already exists`
- Alembic migration history out of sync with database
- Trying to apply migrations that partially succeeded

### 3. Development Issues
- Pulled code with model changes but database not updated
- Database restored from backup with different schema
- Manual database changes made outside migrations

---

## Command Options

### Basic Usage
```bash
# Check and fix all schema issues
py manage.py fix-schema
```

This will:
1. Check your database schema against model definitions
2. Add any missing columns
3. Update migration history to "head"

### Check Only (No Changes)
```bash
# See what's wrong without fixing
py manage.py fix-schema --check-only
```

Use this to:
- Diagnose schema issues
- See what would be changed
- Verify schema state before making changes

### Fix Without Stamping
```bash
# Fix schema but don't update migration history
py manage.py fix-schema --no-stamp
```

Use this when:
- You want to manually control migration versioning
- Testing schema changes
- You'll stamp manually later

---

## What the Command Does

### Step 1: Inspection
The command inspects your database and compares it with expected schema defined in `manage.py`:

```python
expected_schema = {
    'quote_line_items': [
        ('assembly_metadata', 'TEXT', True),
        ('list_price', 'NUMERIC(10, 2)', True),
    ],
}
```

### Step 2: Detection
It identifies missing columns, reporting:
- ✓ Columns that exist
- ✗ Columns that are missing

### Step 3: Repair
For each missing column, it:
- Generates appropriate ALTER TABLE statement
- Executes the SQL
- Commits the change
- Reports success/failure

### Step 4: Synchronization
Updates Alembic's migration history to mark database as current.

---

## Adding Tables to Schema Verification

To check additional tables, edit `manage.py` and add to the `expected_schema` dictionary:

```python
expected_schema = {
    'quote_line_items': [
        ('assembly_metadata', 'TEXT', True),
        ('list_price', 'NUMERIC(10, 2)', True),
        ('custom_sku', 'VARCHAR(80)', True),
        ('custom_name', 'VARCHAR(200)', True),
        ('custom_description', 'TEXT', True),
    ],
    'users': [
        ('email_verified', 'BOOLEAN', False),
        ('verification_token', 'VARCHAR(255)', True),
        ('verified_at', 'TIMESTAMP', True),
    ],
    'deals': [
        ('archived', 'BOOLEAN', False),
        ('archived_at', 'TIMESTAMP', True),
    ],
}
```

**Format**: `(column_name, SQL_type, is_nullable)`

### Column Type Examples
- Text: `'TEXT'`, `'VARCHAR(100)'`, `'CHAR(10)'`
- Numbers: `'INTEGER'`, `'NUMERIC(10, 2)'`, `'BIGINT'`
- Dates: `'TIMESTAMP'`, `'DATE'`, `'TIME'`
- Boolean: `'BOOLEAN'`
- JSON: `'JSON'`, `'JSONB'` (PostgreSQL)

### Nullable Rules
- `True` = Column allows NULL values
- `False` = Column requires a value (NOT NULL)

---

## Common Scenarios

### Scenario 1: After Pulling Code
**Situation**: You pulled code with model changes, but your database isn't updated.

```bash
git pull origin main
py manage.py fix-schema
py wsgi.py  # Test the application
```

### Scenario 2: Migration Failed Halfway
**Situation**: Migration started but failed, leaving partial changes.

```bash
# Check what's missing
py manage.py fix-schema --check-only

# Fix issues and sync
py manage.py fix-schema

# Verify
flask db current
```

### Scenario 3: Manual Database Changes
**Situation**: You made emergency changes directly in the database.

```bash
# First, document what you changed
# Then sync migration history
py manage.py fix-schema

# Or if schema is correct, just update history
py manage.py db-stamp head
```

### Scenario 4: Development Environment Sync
**Situation**: Multiple developers have different database states.

```bash
# Everyone should run:
git pull origin main
py manage.py fix-schema
py manage.py db-upgrade
```

---

## Example Output

### Successful Repair
```
============================================================
Database Schema Verification and Repair
============================================================
Checking database schema against model definitions...

✓ Column exists: quote_line_items.list_price
✗ Missing column: quote_line_items.assembly_metadata (TEXT)
  Executing: ALTER TABLE quote_line_items ADD COLUMN assembly_metadata TEXT
  ✓ Added column: quote_line_items.assembly_metadata

============================================================
✓ Applied 1 schema fix(es)

Updating migration history...
✓ Database stamped with latest migration
============================================================

✓ Schema repair completed successfully!
You can now run the application without schema errors.
```

### Check Only Output
```
============================================================
Database Schema Verification and Repair
============================================================
Checking database schema against model definitions...

✓ Column exists: quote_line_items.list_price
✗ Missing column: quote_line_items.assembly_metadata (TEXT)

============================================================
Found schema mismatches. Run without --check-only to fix.
============================================================
```

---

## Related Commands

### Check Migration Status
```bash
flask db current                # Current revision
flask migrate status            # Detailed status
```

### Manual Stamping
```bash
py manage.py db-stamp head      # Mark as latest version
py manage.py db-stamp <rev_id>  # Mark as specific version
```

### Apply Migrations
```bash
py manage.py db-upgrade         # Apply pending migrations
```

### Create Migrations
```bash
py manage.py db-migrate "message"  # Create new migration
```

---

## Troubleshooting

### Problem: "Table does not exist"
If the command reports tables don't exist, your database is missing entire tables.

**Solution**: Run migrations first, then schema repair:
```bash
py manage.py db-upgrade
py manage.py fix-schema
```

### Problem: "Failed to add column"
If adding a column fails, check:
- Database connection
- User permissions
- Column type compatibility
- Existing data constraints

**Solution**: Check error details and fix underlying issue:
```bash
py manage.py fix-schema  # Will show specific error
```

### Problem: Schema looks correct but app still fails
The issue might not be schema-related.

**Solution**: Check application logs:
```bash
# Look at recent errors
Get-Content app/instance/logs/errors.log -Tail 50

# Check specific error patterns
Select-String "ERROR" app/instance/logs/app.log
```

---

## Best Practices

### DO:
✅ Run `fix-schema` after pulling code with model changes  
✅ Use `--check-only` first to see what will change  
✅ Review the output to understand what was fixed  
✅ Test the application after running schema repair  
✅ Add commonly problematic tables to `expected_schema`  

### DON'T:
❌ Run in production without testing in development first  
❌ Skip reviewing what columns are being added  
❌ Ignore the command output  
❌ Use as a replacement for proper migrations  
❌ Run without understanding why schema is out of sync  

---

## Prevention

To avoid schema mismatches in the future:

1. **Always use migrations** for schema changes
2. **Test migrations locally** before deploying
3. **Run schema repair** after pulling code
4. **Document manual changes** if absolutely necessary
5. **Keep migration history clean** and linear

---

## Additional Resources

- [Database Migration Workflow](./DATABASE_MIGRATION_WORKFLOW.md)
- [Migration Checklist](./MIGRATION_CHECKLIST.md)
- [Troubleshooting Guide](../troubleshooting/)

---

**Last Updated**: 2025-10-16  
**Maintainer**: Development Team

