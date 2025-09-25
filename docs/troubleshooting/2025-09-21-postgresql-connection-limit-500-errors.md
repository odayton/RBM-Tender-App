# PostgreSQL Connection Limit and 500 Errors
**Date**: 2025-09-21  
**Severity**: High  
**Status**: Resolved  
**Tags**: #database #postgresql #deployment #production

## 🎯 **Issue Summary**
Production application experiencing 500 errors on `/deals/` and `/auth/login` endpoints due to PostgreSQL connection limit exceeded.

## 🔍 **Symptoms**
- 500 errors on `/deals/` endpoint
- 500 errors on POST `/auth/login` requests
- 500 errors on `/favicon.ico` requests
- Application logs showing: `FATAL: remaining connection slots are reserved for roles with the SUPERUSER attribute`
- PostgreSQL showing 103 active connections with max_connections = 100
- OOM (Out of Memory) killer terminating application process

## 🔧 **Root Cause**
1. **PostgreSQL Connection Limit**: Default `max_connections = 100` was exceeded (103 active connections)
2. **Database User Configuration**: `odayton` user existed but had no password set
3. **Connection Pool Issues**: Application creating too many database connections without proper cleanup

## ✅ **Solution**

### Step 1: Fix Database User Authentication
```bash
# Connect to PostgreSQL as superuser
sudo -u postgres psql -d postgres

# Set password for odayton user
ALTER USER odayton WITH PASSWORD 'MadeInItaly1953!';

# Grant proper permissions
GRANT ALL PRIVILEGES ON DATABASE rbm_tender_app TO odayton;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO odayton;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO odayton;
```

### Step 2: Increase PostgreSQL Connection Limit
```bash
# Edit PostgreSQL configuration
sudo nano /etc/postgresql/16/main/postgresql.conf

# Change max_connections from 100 to 200
max_connections = 200

# Restart PostgreSQL to apply changes
sudo systemctl restart postgresql
```

### Step 3: Verify Configuration
```bash
# Check new connection limit
sudo -u postgres psql -c "SHOW max_connections;"

# Test database connection
PGPASSWORD='MadeInItaly1953!' psql -h localhost -U odayton -d rbm_tender_app -c "SELECT version();"

# Restart application
sudo systemctl restart rbm-tender-app
```

## 🛡️ **Prevention**

### 1. **Production Database Setup Checklist**
- [ ] Create dedicated database user with proper password
- [ ] Set appropriate PostgreSQL connection limits (recommend 200+ for production)
- [ ] Configure connection pooling in application
- [ ] Monitor connection usage regularly

### 2. **Environment Configuration**
Ensure `.env` file contains correct database credentials:
```bash
DATABASE_URL=postgresql://odayton:MadeInItaly1953!@localhost:5432/rbm_tender_app
SQLALCHEMY_DATABASE_URI=postgresql://odayton:MadeInItaly1953!@localhost:5432/rbm_tender_app
```

### 3. **Monitoring**
```bash
# Check active connections
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"

# Monitor connection usage
sudo -u postgres psql -c "SELECT pid, usename, application_name, client_addr, state FROM pg_stat_activity WHERE state = 'active';"
```

## 🔗 **Related Issues**
- [2025-09-05-postgresql-migration-verification.md](2025-09-05-postgresql-migration-verification.md)
- [2025-09-05-postgres-sync-improvements.md](2025-09-05-postgres-sync-improvements.md)

## 📚 **Resources**
- PostgreSQL Connection Management: https://www.postgresql.org/docs/current/runtime-config-connection.html
- Connection Pooling Best Practices: https://www.postgresql.org/docs/current/runtime-config-connection.html#RUNTIME-CONFIG-CONNECTION-POOLING

## 💡 **Key Lessons Learned**
1. **Default PostgreSQL connection limits are too low for production applications**
2. **Database users must have proper passwords set, even if they exist**
3. **Monitor connection usage proactively to prevent connection exhaustion**
4. **OOM killer indicates memory pressure - check both application and database resource usage**
5. **Test database connections immediately after deployment to catch auth issues early**

