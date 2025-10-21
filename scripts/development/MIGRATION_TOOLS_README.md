# Migration Development Tools

This directory contains tools to help with database migration development and validation.

---

## Available Tools

### 1. Migration Pre-Check Script

**File**: `check_migration.py`

**Purpose**: Validates migration files before committing or deploying to catch common issues.

**Usage**:
```bash
py scripts/development/check_migration.py
```

**What it checks**:
- ✅ Required components (revision, upgrade, downgrade)
- ✅ Empty downgrade functions
- ✅ Dangerous operations (DROP, DELETE, TRUNCATE)
- ✅ Hardcoded sensitive values
- ✅ TODO/FIXME comments
- ✅ Transaction safety

**When to use**:
- Before committing migration files
- Before deploying to production
- As part of code review process
- When in doubt about a migration

**Example output**:
```
============================================================
Migration Pre-Check
============================================================

Found 2 migration file(s)

Checking: 20251013_1430_abc123_add_email_verification.py
  ✓ Checked 20251013_1430_abc123_add_email_verification.py

============================================================
Results
============================================================

✅ No errors found

⚠️  WARNINGS (1):
  • 20251013_1430_abc123_add_email_verification.py: Uses op.drop_column - Drops column - ensure data is not needed

============================================================
⚠️  PASSED with warnings - Review warnings before deploying
============================================================
```

---

### 2. Git Pre-Commit Hook

**File**: `pre-commit-hook-template.sh`

**Purpose**: Automatically validates migrations when you commit them to Git.

**Installation**:
```bash
# Copy to Git hooks directory
cp scripts/development/pre-commit-hook-template.sh .git/hooks/pre-commit

# Make it executable (Linux/Mac)
chmod +x .git/hooks/pre-commit

# On Windows, the hook should work as-is if Git Bash is installed
```

**What it does**:
1. Detects if migration files are being committed
2. Runs `check_migration.py` automatically
3. Checks if models are importable
4. Prevents commit if issues are found

**Bypassing the hook** (when necessary):
```bash
git commit --no-verify -m "Your commit message"
```

**When to bypass**:
- Only when you know what you're doing
- During emergencies
- When committing intentionally incomplete work (use with caution)

---

## Workflow Integration

### Recommended Daily Workflow

1. **Make model changes**
   ```bash
   # Edit your model files
   # Save changes
   ```

2. **Create migration**
   ```bash
   flask migrate create "descriptive_name"
   ```

3. **Check migration automatically** (if pre-commit hook installed)
   ```bash
   git add migrations/versions/your_migration.py
   git commit -m "feat: Add your feature"
   # Hook runs automatically
   ```

4. **Or check manually**
   ```bash
   py scripts/development/check_migration.py
   git add migrations/versions/your_migration.py
   git commit -m "feat: Add your feature"
   ```

5. **Test locally**
   ```bash
   flask migrate upgrade
   # Test your application
   flask migrate rollback
   flask migrate upgrade
   ```

---

## Common Scenarios

### Scenario 1: Simple Column Addition
```bash
# 1. Edit model, add column
# 2. Create migration
flask migrate create "add_status_to_users"

# 3. Review generated file
# 4. Check for issues
py scripts/development/check_migration.py

# 5. Test locally
flask migrate backup -d "test_run"
flask migrate upgrade
# Test application
flask migrate rollback
flask migrate upgrade

# 6. Commit
git add .
git commit -m "feat: Add status field to users"
```

### Scenario 2: Complex Data Migration
```bash
# 1. Edit model
# 2. Create migration
flask migrate create "migrate_user_data"

# 3. Manually edit migration file to add data migration logic
# 4. Add transaction handling if needed
# 5. Check migration
py scripts/development/check_migration.py

# 6. Test extensively
flask migrate backup -d "before_data_migration"
flask migrate upgrade
# Verify data integrity
flask migrate rollback
# Verify rollback worked
flask migrate upgrade
# Final verification

# 7. Commit
git add .
git commit -m "feat: Migrate user data to new structure"
```

### Scenario 3: Migration Has Issues
```bash
# 1. Check migration
py scripts/development/check_migration.py

# Output shows errors:
# ❌ ERRORS (1):
#   • Missing downgrade() function

# 2. Fix the migration file
# 3. Re-check
py scripts/development/check_migration.py

# 4. Once clean, proceed with testing
flask migrate upgrade
```

---

## Configuration

### Customizing Checks

To customize what the migration checker looks for, edit `check_migration.py`:

```python
# Add custom checks in the MigrationChecker class

def check_custom_rule(self, filename, content):
    """Add your custom check."""
    if 'your_pattern' in content:
        self.warnings.append(f"{filename}: Your custom warning")
```

### Disabling Specific Checks

If you need to temporarily disable a check:

```python
# In check_migration.py, comment out the check:

def check_all(self):
    # ...
    # self.check_dangerous_operations(...)  # Disabled
```

---

## Troubleshooting

### Pre-Commit Hook Not Running

**Problem**: Hook doesn't execute on commit

**Solutions**:
1. Check hook is executable:
   ```bash
   ls -la .git/hooks/pre-commit
   ```

2. Ensure it has execute permissions (Linux/Mac):
   ```bash
   chmod +x .git/hooks/pre-commit
   ```

3. Verify path is correct:
   ```bash
   cat .git/hooks/pre-commit | head -1
   # Should show #!/bin/sh
   ```

### Check Script Errors

**Problem**: `check_migration.py` fails to run

**Solutions**:
1. Verify you're in project root
2. Check Python is available: `py --version`
3. Ensure migration files exist: `ls migrations/versions/`

### False Positives

**Problem**: Checker flags legitimate code

**Solutions**:
1. Review the warning - is it actually a concern?
2. If false positive, you can:
   - Add a comment in the migration explaining why it's safe
   - Proceed with commit using `--no-verify` (document why)
   - Customize the checker to ignore specific patterns

---

## Best Practices

### DO:
✅ Run checker before every commit
✅ Review all warnings, even if tests pass
✅ Install pre-commit hook for automatic checking
✅ Keep migration files clean and documented
✅ Test migrations locally before pushing

### DON'T:
❌ Skip checks because you're in a hurry
❌ Use `--no-verify` without good reason
❌ Ignore warnings without reviewing them
❌ Commit migrations that fail checks
❌ Deploy without testing locally first

---

## Related Documentation

- **[Database Migration Workflow](../../docs/database/DATABASE_MIGRATION_WORKFLOW.md)** - Complete workflow guide
- **[Migration Checklist](../../docs/database/MIGRATION_CHECKLIST.md)** - Quick reference checklist
- **[Migration Workflow Diagram](../../docs/database/MIGRATION_WORKFLOW_DIAGRAM.md)** - Visual flowcharts
- **[Main Documentation](../../docs/RBM_TENDER_APP_DOCUMENTATION.md)** - Full app documentation

---

## Support

If you encounter issues or have questions about these tools:

1. Check the main migration documentation
2. Review error messages carefully
3. Ask the development team
4. Check Git history for similar migrations

---

**Last Updated**: October 2025
**Maintained By**: Development Team

