# PostgreSQL Safety Protocols
**Date**: 2025-01-15  
**Status**: Active  
**Tags**: #postgresql #safety #database #schema

## 🎯 **Overview**

This document outlines the updated safety protocols for PostgreSQL database management in the RBM Tender App. These protocols replace the previous SQLite migration-based safety measures.

## 🛡️ **Core Safety Principles**

### **1. Always Backup Before Changes**
- **Command**: `py scripts/development/postgres_sync.py sync-out`
- **Purpose**: Creates a complete database backup before any schema modifications
- **Frequency**: Before every schema change, no exceptions

### **2. Use Transactions for All Changes**
- **Principle**: Wrap all schema changes in `BEGIN`/`COMMIT` blocks
- **Benefit**: Automatic rollback if any command fails
- **Example**:
  ```sql
  BEGIN;
  ALTER TABLE users ADD COLUMN two_factor_enabled BOOLEAN DEFAULT FALSE;
  ALTER TABLE users ADD COLUMN two_factor_secret VARCHAR(32);
  ALTER TABLE users ADD COLUMN backup_codes TEXT;
  COMMIT;
  ```

### **3. Validate Before and After**
- **Before**: Check current table structure
- **After**: Verify changes applied correctly
- **Command**: `& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -d rbm_tender_app -c "\d table_name"`

## 📋 **Standard Operating Procedures**

### **Pre-Change Checklist**
1. ✅ **Create Backup**: `py scripts/development/postgres_sync.py sync-out`
2. ✅ **Verify Connection**: Test PostgreSQL connection
3. ✅ **Check Current Schema**: Review existing table structure
4. ✅ **Plan Changes**: Document all SQL commands
5. ✅ **Test Environment**: Verify in safe environment first

### **During Changes**
1. ✅ **Use Transactions**: Wrap all changes in BEGIN/COMMIT
2. ✅ **Monitor Logs**: Watch for errors or warnings
3. ✅ **Validate Each Step**: Check structure after each change
4. ✅ **Document Progress**: Keep detailed records

### **Post-Change Checklist**
1. ✅ **Verify Structure**: Confirm all changes applied correctly
2. ✅ **Test Application**: Ensure app works with new schema
3. ✅ **Update Sync**: Run `sync-out` to backup new schema
4. ✅ **Document Changes**: Update documentation
5. ✅ **Sync Other Machines**: Use two-machine sync system

## 🔧 **Common Operations**

### **Adding New Columns**
```sql
-- Safe column addition
BEGIN;
ALTER TABLE users ADD COLUMN new_field VARCHAR(100) DEFAULT NULL;
COMMIT;

-- Verify the change
\d users
```

### **Modifying Existing Columns**
```sql
-- Safe column modification
BEGIN;
ALTER TABLE users ALTER COLUMN existing_field TYPE VARCHAR(200);
COMMIT;

-- Verify the change
\d users
```

### **Adding Indexes**
```sql
-- Safe index creation
BEGIN;
CREATE INDEX idx_users_email ON users(email);
COMMIT;

-- Verify the index
\di idx_users_email
```

## 🚨 **Emergency Procedures**

### **If Schema Change Fails**
1. **Check Transaction Status**: Look for incomplete transactions
2. **Rollback if Needed**: Use `ROLLBACK;` command
3. **Restore from Backup**: `py scripts/development/postgres_sync.py sync-in`
4. **Investigate Issue**: Review error logs and fix the problem
5. **Retry with Fix**: Apply corrected changes

### **If Database Becomes Unresponsive**
1. **Check PostgreSQL Service**: `Get-Service postgresql*`
2. **Restart Service**: `Restart-Service postgresql-x64-17`
3. **Verify Connection**: Test basic connectivity
4. **Restore if Corrupted**: Use backup restoration

### **If Sync Fails**
1. **Check Sync Status**: `py scripts/development/postgres_sync.py status`
2. **Force Sync-Out**: `py scripts/development/postgres_sync.py sync-out`
3. **Check for Conflicts**: Review sync logs
4. **Manual Resolution**: Resolve conflicts manually if needed

## 📊 **Monitoring and Validation**

### **Health Checks**

```bash
# Check PostgreSQL service status
Get-Service postgresql*

# Test database connection
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -c "\l"

# Check table structure
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -d rbm_tender_app -c "\dt"

# Verify specific table
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -d rbm_tender_app -c "\d users"
```

### **Performance Monitoring**
- Monitor query performance after schema changes
- Check for any new indexes needed
- Verify application response times
- Watch for any new errors in logs

## 🔗 **Related Documentation**

- [PostgreSQL Sync System](postgres-sync-improvements.md)
- [Database Configuration](../RBM_TENDER_APP_DOCUMENTATION.md#database-migrations)
- [Emergency Procedures](runbooks/emergency-website-down.md)

## 📝 **Change Log**

- **2025-01-15**: Initial PostgreSQL safety protocols created
- **2025-01-15**: Updated from SQLite migration-based protocols
- **2025-01-15**: Added transaction safety and validation procedures
