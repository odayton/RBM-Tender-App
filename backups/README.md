# RBM Tender App - Backup Management

## 📁 Backup Structure

This directory follows industry best practices for backup organization:

```
backups/
├── database/           # Database backups (SQL dumps, exports)
├── migrations/         # Migration rollback backups
├── config/            # Configuration file backups
├── instance/          # Instance data backups (uploads, sessions)
└── README.md          # This file
```

## 🔄 Backup Types

### Database Backups (`database/`)
- **Purpose**: Complete database exports and dumps
- **Format**: `.sql` files
- **Naming**: `{type}_backup_{YYYYMMDD_HHMMSS}.sql`
- **Examples**:
  - `postgres_complete_backup_20250920_105200.sql`
  - `sqlite_export_backup_20250920_105200.sql`

### Migration Backups (`migrations/`)
- **Purpose**: Pre-migration state backups for rollback
- **Format**: `.json` files
- **Naming**: `pre_{migration_name}_backup_{YYYYMMDD_HHMMSS}.json`
- **Examples**:
  - `pre_quote_snapshots_migration_20250824_174403.json`

### Configuration Backups (`config/`)
- **Purpose**: Configuration file backups before changes
- **Format**: Original file format (`.env`, `.conf`, etc.)
- **Naming**: `{filename}_backup_{YYYYMMDD_HHMMSS}.{ext}`
- **Examples**:
  - `.env_backup_20250920_105200.env`
  - `nginx.conf_backup_20250920_105200.conf`

### Instance Backups (`instance/`)
- **Purpose**: User uploads, sessions, and runtime data
- **Format**: Compressed archives
- **Naming**: `instance_backup_{YYYYMMDD_HHMMSS}.tar.gz`
- **Examples**:
  - `instance_backup_20250920_105200.tar.gz`

## 🛡️ Security Best Practices

1. **Never commit backups to version control**
2. **Use secure storage for production backups**
3. **Encrypt sensitive backup data**
4. **Regular backup rotation (keep only last 30 days)**
5. **Test restore procedures regularly**

## 📋 Backup Schedule

- **Database**: Daily automated backups
- **Config**: Before any configuration changes
- **Migrations**: Before each migration
- **Instance**: Weekly or before major updates

## 🔧 Backup Management Commands

```bash
# Create database backup
py scripts/utils/backup_manager.py --type database --output backups/database/

# Create config backup
cp config/.env backups/config/.env_backup_$(date +%Y%m%d_%H%M%S).env

# Create instance backup
tar -czf backups/instance/instance_backup_$(date +%Y%m%d_%H%M%S).tar.gz instance/

# List recent backups
ls -la backups/database/ | tail -10
```

## 🚨 Emergency Recovery

1. **Database Recovery**: Restore from latest SQL dump
2. **Config Recovery**: Restore from config backups
3. **Full Recovery**: Restore from complete instance backup
4. **Migration Rollback**: Use migration backups to revert schema changes
