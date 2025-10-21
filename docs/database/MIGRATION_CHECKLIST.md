# Migration Checklist

Quick reference guide for database migrations. Print this or keep it handy!

---

## Pre-Migration Checklist

### Model Changes
- [ ] All model changes are saved
- [ ] Models import successfully: `py -c "from app.models import *"`
- [ ] Changes follow project conventions
- [ ] Foreign keys and relationships are correct

### Create Migration
- [ ] Run: `flask migrate create "descriptive_name"`
- [ ] Migration file created in `migrations/versions/`
- [ ] File name is descriptive and clear

---

## Migration Review Checklist

### File Structure
- [ ] Has `revision` identifier
- [ ] Has `down_revision` (parent migration)
- [ ] Has `upgrade()` function with changes
- [ ] Has `downgrade()` function with reversals
- [ ] Imports are at the top

### Schema Changes
- [ ] All expected changes are present
- [ ] No unexpected changes
- [ ] Column types are appropriate
- [ ] Nullable constraints are correct
- [ ] Default values set where needed
- [ ] Indexes added for foreign keys
- [ ] Unique constraints properly defined
- [ ] Check constraints don't break existing data

### Data Safety
- [ ] No unintended data loss
- [ ] Existing data preserved or migrated
- [ ] Foreign key relationships maintained
- [ ] Enum values are valid

### Performance
- [ ] Indexes added before data population
- [ ] Large tables use batch operations
- [ ] No unnecessary full table scans

### Rollback
- [ ] `downgrade()` truly reverses `upgrade()`
- [ ] Not just `pass` in downgrade
- [ ] Tested rollback locally

---

## Local Testing Checklist

### Phase 1: Backup & Upgrade
- [ ] Create backup: `flask migrate backup -d "test_run"`
- [ ] Check status: `flask migrate status`
- [ ] Run upgrade: `flask migrate upgrade`
- [ ] Verify success (no errors in output)
- [ ] Check new status: `flask migrate status`

### Phase 2: Application Testing
- [ ] Start application: `py app_runner.py`
- [ ] Test affected features manually
- [ ] Check for errors in logs
- [ ] Verify database queries work
- [ ] Test create/read/update/delete operations

### Phase 3: Rollback Testing
- [ ] Run rollback: `flask migrate rollback`
- [ ] Verify success (no errors)
- [ ] Check status: `flask migrate status`
- [ ] Test application still works
- [ ] Re-apply: `flask migrate upgrade`
- [ ] Verify it works again

### Phase 4: Data Integrity
- [ ] Add test data
- [ ] Run migration
- [ ] Verify test data preserved
- [ ] Check relationships intact
- [ ] Verify constraints enforced

---

## Git Workflow Checklist

### Before Committing
- [ ] All local tests passed
- [ ] Migration validated: `flask migrate validate`
- [ ] No sensitive data in migration
- [ ] Reviewed changes with `git diff`

### Committing
- [ ] Stage migration: `git add migrations/versions/<file>.py`
- [ ] Stage model changes: `git add app/models/`
- [ ] Write descriptive commit message
- [ ] Include migration ID in commit message

### After Committing
- [ ] Push to branch: `git push origin <branch>`
- [ ] Create pull request
- [ ] Request code review
- [ ] Link to related issues/tickets

---

## Production Deployment Checklist

### Pre-Deployment
- [ ] All tests pass
- [ ] Code reviewed and approved
- [ ] Merged to main branch
- [ ] Rollback plan documented
- [ ] Backup strategy confirmed
- [ ] Communication sent (if needed)
- [ ] Know when to deploy (low traffic time)

### On Production Server

#### Step 1: Preparation
- [ ] SSH into production server
- [ ] Navigate to app directory
- [ ] Activate virtual environment (if applicable)
- [ ] Pull latest code: `git pull origin main`

#### Step 2: Backup
- [ ] Create backup: `flask migrate backup -d "prod_$(date +%Y%m%d_%H%M%S)"`
- [ ] Verify backup created: `ls -lh migrations/backups/`
- [ ] Note backup filename for rollback

#### Step 3: Validation
- [ ] Check current status: `flask migrate status`
- [ ] Validate migrations: `flask migrate validate`
- [ ] Review pending migrations
- [ ] Confirm correct migration will run

#### Step 4: Apply Migration
- [ ] Run migration: `flask migrate upgrade`
- [ ] Watch output for errors
- [ ] DO NOT interrupt if in progress
- [ ] Verify success message

#### Step 5: Restart Application
- [ ] Restart service: `sudo systemctl restart rbm-tender-app`
- [ ] Check service status: `sudo systemctl status rbm-tender-app`
- [ ] Check for errors: `sudo journalctl -u rbm-tender-app -n 50`

#### Step 6: Verification
- [ ] Check migration status: `flask migrate status`
- [ ] Access application URL
- [ ] Test critical functionality
- [ ] Check application logs
- [ ] Monitor for 15-30 minutes

### If Problems Occur
- [ ] Stop the application
- [ ] Restore backup: `flask migrate restore <backup_file>`
- [ ] OR rollback: `flask migrate rollback`
- [ ] Restart application
- [ ] Verify application works
- [ ] Notify team
- [ ] Document issue
- [ ] Fix locally and retest

---

## Post-Deployment Checklist

### Immediate (Within 1 Hour)
- [ ] Application accessible
- [ ] No errors in logs
- [ ] Critical features working
- [ ] Database responding normally
- [ ] No performance issues

### Short Term (Within 24 Hours)
- [ ] Monitor error logs
- [ ] Check database size/performance
- [ ] Verify all features still work
- [ ] Collect user feedback
- [ ] Document any issues

### Documentation
- [ ] Update deployment log
- [ ] Document any manual steps taken
- [ ] Note any issues encountered
- [ ] Update runbooks if needed

---

## Emergency Rollback Checklist

### If Migration Fails
- [ ] **DON'T PANIC**
- [ ] Document the error
- [ ] Check migration status
- [ ] Attempt rollback: `flask migrate rollback`

### If Rollback Fails
- [ ] Stop the application immediately
- [ ] Find latest backup file
- [ ] Restore: `flask migrate restore <backup_file>`
- [ ] Restart application
- [ ] Verify application works
- [ ] Notify team immediately

### After Emergency Rollback
- [ ] Document what happened
- [ ] Save error logs
- [ ] Test fix locally before redeploying
- [ ] Review what went wrong
- [ ] Update processes to prevent recurrence

---

## Common Issues Quick Reference

| Issue | Quick Fix |
|-------|-----------|
| "No changes detected" | Verify models imported in `app/models/__init__.py` |
| "Multiple heads detected" | Run `flask db merge` |
| "Can't locate revision" | Check `alembic_version` table |
| Migration half-completed | Check state, restore backup, or stamp version |
| Import errors | Verify all dependencies installed |
| Permission denied | Check database user permissions |

---

## Daily Development Rules

### Before Starting Work
1. Pull latest code
2. Check migration status
3. Ensure database is current

### Before Creating Migration
1. Test model changes
2. Verify imports work
3. Use descriptive names

### Before Committing
1. Test upgrade
2. Test rollback
3. Test upgrade again
4. Validate migration file

### Before Deploying
1. All tests pass
2. Code reviewed
3. Backup plan ready
4. Rollback plan ready

---

## Quick Commands Reference

```bash
# Status
flask migrate status

# Create
flask migrate create "message"

# Test locally
flask migrate upgrade
flask migrate rollback
flask migrate upgrade

# Production
flask migrate backup -d "prod_backup"
flask migrate validate
flask migrate upgrade

# Emergency
flask migrate rollback
flask migrate restore <backup_file>
```

---

## Remember

- ✅ **ALWAYS** backup before production migrations
- ✅ **ALWAYS** test rollback locally
- ✅ **ALWAYS** review generated migrations
- ✅ **NEVER** skip testing
- ✅ **NEVER** deploy without backup
- ✅ **NEVER** rush production deployments

---

**Last Updated**: October 2025
**Maintained By**: Development Team

