# Database Connection Limit Issues

## Problem
PostgreSQL errors indicating too many connections:
```
FATAL: sorry, too many clients already
FATAL: remaining connection slots are reserved for roles with the SUPERUSER attribute
```

## Quick Diagnosis

### 1. Check Current Connection Count
```bash
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"
```

### 2. Check Connection Limit
```bash
sudo -u postgres psql -c "SHOW max_connections;"
```

### 3. Check What's Using Connections
```bash
sudo -u postgres psql -c "SELECT application_name, count(*) FROM pg_stat_activity GROUP BY application_name;"
```

## Normal vs Problematic

**Normal:** 5-20 connections  
**Problematic:** 100+ connections  
**Critical:** 200+ connections (at or over limit)

## Common Causes

### 1. Connection Leak in Flask App

**Symptoms:**
- Hundreds of idle connections with empty `application_name`
- Single Flask process using 100+ connections
- Connections created rapidly and never closed

**Diagnosis:**
```bash
# Check for idle connections
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity WHERE application_name = '' AND state = 'idle';"

# Check Flask process
ps aux | grep python | grep rbm
```

**Solution:**
Add connection pool settings to `/opt/rbm-tender-app/config/.env`:
```bash
# Database Connection Pool Settings
SQLALCHEMY_ENGINE_OPTIONS={"pool_size": 5, "pool_recycle": 3600, "pool_pre_ping": True, "pool_timeout": 20}
```

Then restart the service:
```bash
sudo systemctl restart rbm-tender-app
```

### 2. Backup System Creating Too Many Connections

**Symptoms:**
- Backup failures in logs
- Connections created during backup operations
- `pg_dump` processes in connection list

**Check backup logs:**
```bash
sudo journalctl -u rbm-tender-app | grep -i backup
```

**Solution:**
- Ensure backup processes close connections properly
- Consider running backups during low-traffic periods
- Add connection limits to backup scripts

### 3. Multiple App Instances

**Symptoms:**
- Multiple Python processes running
- Each process using many connections

**Check running processes:**
```bash
ps aux | grep python | grep rbm
```

**Solution:**
```bash
# Kill duplicate processes
sudo pkill -f "app_runner.py"

# Restart service properly
sudo systemctl restart rbm-tender-app
```

### 4. Long-Running Queries

**Symptoms:**
- Connections in `active` state for long periods
- Specific queries running for hours

**Check active queries:**
```bash
sudo -u postgres psql -c "SELECT pid, state, query_start, query FROM pg_stat_activity WHERE state = 'active' ORDER BY query_start;"
```

**Solution:**
- Identify and optimize slow queries
- Kill problematic queries if necessary:
```bash
sudo -u postgres psql -c "SELECT pg_terminate_backend(<PID>);"
```

## Emergency Recovery

### 1. Kill Idle Connections
```bash
# Kill all idle connections with no application name
sudo -u postgres psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE application_name = '' AND state = 'idle';"
```

### 2. Restart PostgreSQL
```bash
sudo systemctl restart postgresql
```

### 3. Restart Flask App
```bash
sudo systemctl restart rbm-tender-app
```

### 4. Verify Recovery
```bash
# Check connection count
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"

# Test app functionality
curl -f http://localhost:5000/health
```

## Prevention

### 1. Configure Connection Pooling

Add to `/opt/rbm-tender-app/config/.env`:
```bash
# Database Connection Pool Settings
SQLALCHEMY_ENGINE_OPTIONS={"pool_size": 5, "pool_recycle": 3600, "pool_pre_ping": True, "pool_timeout": 20}
```

**What this does:**
- `pool_size: 5` - Maximum 5 connections per app instance
- `pool_recycle: 3600` - Recycle connections every hour
- `pool_pre_ping: True` - Test connections before use
- `pool_timeout: 20` - Timeout after 20 seconds

### 2. Monitor Connection Usage

**Regular monitoring:**
```bash
# Check connection count daily
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"

# Check for connection leaks
sudo -u postgres psql -c "SELECT application_name, count(*) FROM pg_stat_activity GROUP BY application_name;"
```

### 3. Increase PostgreSQL Connection Limit (if needed)

**Edit PostgreSQL configuration:**
```bash
sudo nano /etc/postgresql/16/main/postgresql.conf
```

**Find and change:**
```
max_connections = 200
```
**To:**
```
max_connections = 500
```

**Restart PostgreSQL:**
```bash
sudo systemctl restart postgresql
```

**Note:** Only increase if you've fixed the root cause of connection leaks.

## Monitoring Script

Create a monitoring script to check connections regularly:

```bash
#!/bin/bash
# /opt/rbm-tender-app/scripts/monitor_connections.sh

CONNECTIONS=$(sudo -u postgres psql -t -c "SELECT count(*) FROM pg_stat_activity;")
MAX_CONNECTIONS=$(sudo -u postgres psql -t -c "SHOW max_connections;")

echo "Current connections: $CONNECTIONS"
echo "Max connections: $MAX_CONNECTIONS"

if [ "$CONNECTIONS" -gt 100 ]; then
    echo "WARNING: High connection count detected!"
    sudo -u postgres psql -c "SELECT application_name, count(*) FROM pg_stat_activity GROUP BY application_name;"
fi
```

**Make it executable:**
```bash
chmod +x /opt/rbm-tender-app/scripts/monitor_connections.sh
```

**Add to crontab for regular monitoring:**
```bash
# Check every 5 minutes
*/5 * * * * /opt/rbm-tender-app/scripts/monitor_connections.sh >> /var/log/connection_monitor.log
```

## Troubleshooting Checklist

- [ ] Check current connection count
- [ ] Identify what's using connections
- [ ] Look for connection leaks in Flask app
- [ ] Check for multiple app instances
- [ ] Review backup system connections
- [ ] Check for long-running queries
- [ ] Apply connection pool settings
- [ ] Restart services if needed
- [ ] Monitor for recurrence
- [ ] Consider increasing max_connections if necessary
