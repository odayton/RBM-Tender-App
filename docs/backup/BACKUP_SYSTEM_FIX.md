# Backup System Fix for Production PostgreSQL

**Date**: 2025-01-15  
**Issue**: Backup system trying to backup non-existent SQLite file in PostgreSQL production environment  
**Status**: Fixed

## 🎯 **Problem Summary**

Your production logs showed repeated backup failures:
```
❌ Backup failed: [Errno 2] No such file or directory: 'app/instance/rbm_tender_app.db'
```

**Root Cause**: The backup system was hardcoded to use SQLite (`rbm_tender_app.db`) but your production environment uses PostgreSQL [[memory:7074475]].

## 🔧 **Solution Implemented**

### 1. **Updated Backup Manager** (`app/utils/backup_manager.py`)

**New Features**:
- **Database Type Detection**: Automatically detects SQLite vs PostgreSQL from `DATABASE_URL` environment variable
- **PostgreSQL Backup Support**: Uses `pg_dump` to create SQL backups
- **Smart Fallback**: Skips backup gracefully if PostgreSQL tools aren't available
- **Enhanced Metadata**: Includes database type and backup format information

**Key Changes**:
```python
# Detects database type automatically
def _detect_database_type(self):
    db_url = os.environ.get('DATABASE_URL')
    if db_url and ('postgresql://' in db_url or 'postgres://' in db_url):
        return 'postgresql'
    elif self.db_path.exists():
        return 'sqlite'
    return 'unknown'

# Creates appropriate backup format
if self.db_type == 'postgresql':
    backup_name = f"backup_{timestamp}_{description}.sql"  # SQL dump
    self._create_postgresql_backup(backup_path)
elif self.db_type == 'sqlite':
    backup_name = f"backup_{timestamp}_{description}.db"   # SQLite file
    shutil.copy2(self.db_path, backup_path)
```

### 2. **PostgreSQL Backup Implementation**

**Features**:
- Uses `pg_dump` for reliable PostgreSQL backups
- Parses `DATABASE_URL` for connection parameters
- Creates SQL dump files (`.sql`) instead of binary files
- Includes comprehensive metadata

**Backup Process**:
```bash
pg_dump -h hostname -p 5432 -U username -d database -f backup.sql
```

### 3. **PostgreSQL Client Installation Script** (`scripts/deployment/install-postgresql-client.sh`)

**Purpose**: Installs PostgreSQL client tools on your server for backup functionality.

**Supports**:
- Amazon Linux 2 / CentOS / RHEL
- Ubuntu / Debian
- Installs `postgresql15` client package

## 🚀 **Deployment Steps**

### Step 1: Install PostgreSQL Client Tools

SSH into your production server and run:

```bash
# Make script executable
chmod +x install-postgresql-client.sh

# Install PostgreSQL client tools
sudo ./install-postgresql-client.sh
```

This installs:
- `pg_dump` - for creating backups
- `pg_restore` - for restoring backups  
- `psql` - PostgreSQL command line client

### Step 2: Deploy Updated Backup System

```bash
# Upload the updated backup manager
scp -i your-key.pem app/utils/backup_manager.py ec2-user@your-server-ip:/home/ec2-user/RBM-Tender-App-main/app/utils/

# Restart your application to load the new backup system
sudo systemctl restart rbm-tender-app
```

### Step 3: Verify Backup System

```bash
# Check if backup system is working
sudo journalctl -u rbm-tender-app -f | grep backup

# You should see messages like:
# ✅ Backup created: backup_20250115_123456_auto_backup.sql
# 🗄️  Database: postgresql
```

## 🔍 **How It Works Now**

### Database Type Detection
1. **Checks `DATABASE_URL`** environment variable
2. **If PostgreSQL URL**: Uses PostgreSQL backup methods
3. **If SQLite file exists**: Uses SQLite backup methods
4. **If unknown**: Skips backup gracefully

### Backup Process
1. **PostgreSQL**: Creates SQL dump using `pg_dump`
2. **SQLite**: Copies database file directly
3. **Metadata**: Records database type, file size, hash, etc.
4. **Cleanup**: Removes old backups (keeps 10 most recent)

### Error Handling
- **PostgreSQL tools missing**: Skips backup with warning
- **Database connection failed**: Logs error and continues
- **Permission issues**: Logs error and continues
- **No more rapid-fire failures**: Intelligent backup scheduling

## 📊 **Expected Results**

### Before Fix
```
❌ Backup failed: [Errno 2] No such file or directory: 'app/instance/rbm_tender_app.db'
❌ Backup failed: [Errno 2] No such file or directory: 'app/instance/rbm_tender_app.db'
❌ Backup failed: [Errno 2] No such file or directory: 'app/instance/rbm_tender_app.db'
```

### After Fix
```
✅ Backup created: backup_20250115_123456_auto_backup.sql
   📁 Location: /home/ec2-user/RBM-Tender-App-main/app/instance/backups/backup_20250115_123456_auto_backup.sql
   📏 Size: 2048576 bytes
   🗄️  Database: postgresql
```

## 🔧 **Troubleshooting**

### Issue: "pg_dump: command not found"
**Solution**: Run the PostgreSQL client installation script:
```bash
sudo ./install-postgresql-client.sh
```

### Issue: "PostgreSQL backup failed: authentication failed"
**Solution**: Verify `DATABASE_URL` environment variable is set correctly:
```bash
echo $DATABASE_URL
# Should show: postgresql://username:password@host:port/database
```

### Issue: "Permission denied" errors
**Solution**: Ensure backup directory is writable:
```bash
sudo chown -R ec2-user:ec2-user /home/ec2-user/RBM-Tender-App-main/app/instance/backups/
sudo chmod 755 /home/ec2-user/RBM-Tender-App-main/app/instance/backups/
```

## 📋 **Backup File Formats**

### PostgreSQL Backups
- **File Extension**: `.sql`
- **Format**: SQL dump (text)
- **Size**: Larger than binary dumps but more portable
- **Restore**: Use `psql` or `pg_restore`

### SQLite Backups  
- **File Extension**: `.db`
- **Format**: Binary SQLite file
- **Size**: Compact binary format
- **Restore**: Copy file directly

## 🔒 **Security Features**

- **Password Masking**: Database URLs in metadata have passwords masked
- **File Permissions**: Backup files have restricted permissions
- **Error Logging**: Detailed error messages for troubleshooting
- **Graceful Degradation**: System continues working even if backup fails

## ✅ **Success Checklist**

- [ ] PostgreSQL client tools installed
- [ ] Updated backup manager deployed
- [ ] Application restarted
- [ ] Backup system detects PostgreSQL correctly
- [ ] No more "file not found" errors in logs
- [ ] PostgreSQL backups being created successfully
- [ ] Backup metadata includes database type
- [ ] Old backups cleaned up automatically

## 📚 **Additional Resources**

- [PostgreSQL pg_dump Documentation](https://www.postgresql.org/docs/current/app-pgdump.html)
- [PostgreSQL Backup and Restore Guide](https://www.postgresql.org/docs/current/backup.html)
- [Database Migration Documentation](docs/troubleshooting/2025-09-05-postgresql-migration-verification.md)

---

*This fix ensures your backup system works correctly with PostgreSQL in production while maintaining compatibility with SQLite in development.*
