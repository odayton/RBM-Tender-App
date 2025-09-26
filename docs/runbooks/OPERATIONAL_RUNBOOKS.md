# RBM Tender App - Operational Runbooks

## Table of Contents

1. [Emergency Response Procedures](#emergency-response-procedures)
2. [Database Operations](#database-operations)
3. [Application Deployment](#application-deployment)
4. [Monitoring and Alerting](#monitoring-and-alerting)
5. [Performance Optimization](#performance-optimization)
6. [Security Incident Response](#security-incident-response)
7. [Backup and Recovery](#backup-and-recovery)
8. [Feature Flag Management](#feature-flag-management)
9. [Circuit Breaker Management](#circuit-breaker-management)
10. [Troubleshooting Guide](#troubleshooting-guide)

---

## Emergency Response Procedures

### 🚨 Critical System Down

**Priority: P0 - Immediate Response Required**

#### Immediate Actions (0-5 minutes)
1. **Assess the situation**
   ```bash
   # Check application status
   curl -f http://localhost:5000/health
   
   # Check database connectivity
   psql -h localhost -U postgres -d rbm_tender_app -c "SELECT 1;"
   
   # Check system resources
   top
   df -h
   ```

2. **Check monitoring dashboards**
   - Access: `http://localhost:5000/monitoring/dashboard`
   - Review system metrics, database health, and application status

3. **Verify infrastructure**
   ```bash
   # Check if application process is running
   ps aux | grep python
   
   # Check if database is running
   systemctl status postgresql
   
   # Check disk space
   df -h | grep -E "(/|/var|/home)"
   ```

#### Escalation (5-15 minutes)
1. **If application is down:**
   - Restart application: `systemctl restart rbm-tender-app`
   - Check logs: `journalctl -u rbm-tender-app -f`
   - Verify database connectivity

2. **If database is down:**
   - Restart PostgreSQL: `systemctl restart postgresql`
   - Check database logs: `tail -f /var/log/postgresql/postgresql-*.log`
   - Verify disk space and permissions

3. **If infrastructure issues:**
   - Check AWS EC2 instance status
   - Verify Cloudflare DNS configuration
   - Review system logs for hardware issues

#### Recovery Verification (15-30 minutes)
1. **Test critical functionality**
   - User login: `http://localhost:5000/auth/login`
   - Deal creation: `http://localhost:5000/deals/create`
   - Quote generation: Test PDF generation
   - Database queries: Verify data integrity

2. **Monitor system stability**
   - Watch monitoring dashboard for 15 minutes
   - Check error rates and response times
   - Verify all services are healthy

### 🔥 High Error Rate

**Priority: P1 - Response within 15 minutes**

#### Immediate Actions
1. **Check error logs**
   ```bash
   # Application logs
   tail -f /var/log/rbm-tender-app/application.log
   
   # Database logs
   tail -f /var/log/postgresql/postgresql-*.log
   
   # System logs
   journalctl -u rbm-tender-app -f
   ```

2. **Identify error patterns**
   - Check monitoring dashboard for error trends
   - Review Prometheus metrics: `http://localhost:5000/metrics`
   - Analyze error types and frequency

3. **Check circuit breakers**
   ```bash
   # Check circuit breaker status
   curl http://localhost:5000/monitoring/api/health
   ```

#### Common Error Scenarios
1. **Database connection errors**
   - Check connection pool settings
   - Verify database server status
   - Review connection limits

2. **Memory issues**
   - Check memory usage: `free -h`
   - Review application memory settings
   - Consider restarting application

3. **External service failures**
   - Check circuit breaker status
   - Verify external API connectivity
   - Review fallback mechanisms

---

## Database Operations

### 🔄 Database Migration

#### Pre-Migration Checklist
1. **Create safety backup**
   ```bash
   # Using database safety manager
   python -c "
   from app.core.core_db_safety import get_database_safety_manager
   manager = get_database_safety_manager()
   result = manager.create_safety_backup()
   print(f'Backup created: {result}')
   "
   ```

2. **Run pre-migration safety check**
   ```bash
   python -c "
   from app.core.core_db_safety import get_database_safety_manager
   manager = get_database_safety_manager()
   check = manager.pre_migration_safety_check()
   print(f'Safety check status: {check[\"status\"]}')
   if check['blockers']:
       print(f'Blockers: {check[\"blockers\"]}')
   "
   ```

3. **Verify schema integrity**
   ```bash
   python -c "
   from app.core.core_db_safety import get_database_safety_manager
   manager = get_database_safety_manager()
   validation = manager.schema_validator.validate_schema_integrity()
   print(f'Schema validation: {validation[\"status\"]}')
   "
   ```

#### Migration Execution
1. **Run migration**
   ```bash
   # Activate virtual environment
   source venv/bin/activate
   
   # Run migration
   flask db upgrade
   
   # Verify migration
   flask db current
   ```

2. **Post-migration verification**
   ```bash
   # Test database connectivity
   python -c "
   from app import create_app, db
   app = create_app()
   with app.app_context():
       result = db.session.execute('SELECT 1').fetchone()
       print(f'Database test: {result[0]}')
   "
   ```

3. **Validate schema changes**
   ```bash
   python -c "
   from app.core.core_db_safety import get_database_safety_manager
   manager = get_database_safety_manager()
   validation = manager.schema_validator.validate_schema_integrity()
   print(f'Post-migration validation: {validation[\"status\"]}')
   "
   ```

### 💾 Backup Management

#### Automated Backup Verification
```bash
# Check recent backups
python -c "
from app.core.core_db_safety import get_database_safety_manager
manager = get_database_safety_manager()
backups = manager.backup_manager.list_backups()
print(f'Recent backups: {len(backups)}')
for backup in backups[:5]:
    print(f'- {backup[\"name\"]}: {backup[\"status\"]} ({backup[\"timestamp\"]})')
"
```

#### Manual Backup Creation
```bash
# Create manual backup
python -c "
from app.core.core_db_safety import get_database_safety_manager
manager = get_database_safety_manager()
result = manager.backup_manager.create_backup('manual_backup_$(date +%Y%m%d_%H%M%S)')
print(f'Backup result: {result}')
"
```

#### Backup Restoration
```bash
# Restore from backup (CAUTION: This will overwrite current data)
pg_restore -h localhost -U postgres -d rbm_tender_app -v /path/to/backup.sql

# Verify restoration
psql -h localhost -U postgres -d rbm_tender_app -c "SELECT COUNT(*) FROM users;"
```

---

## Application Deployment

### 🚀 Production Deployment

#### Pre-Deployment Checklist
1. **Verify all tests pass**
   ```bash
   # Run full test suite
   python scripts/development/run_tests.py
   
   # Check test coverage
   coverage report --show-missing
   ```

2. **Check feature flags**
   ```bash
   python -c "
   from app.core.core_feature_flags import feature_flags
   flags = feature_flags.get_all_flags()
   print(f'Active feature flags: {len([f for f in flags if f.enabled])}')
   "
   ```

3. **Verify circuit breakers**
   ```bash
   python -c "
   from app.core.core_circuit_breaker import get_circuit_breaker_stats
   stats = get_circuit_breaker_stats()
   print(f'Circuit breaker status: {stats}')
   "
   ```

#### Deployment Process
1. **Stop application**
   ```bash
   systemctl stop rbm-tender-app
   ```

2. **Update code**
   ```bash
   # Pull latest changes
   git pull origin main
   
   # Install dependencies
   pip install -r requirements/prod_requirements.txt
   ```

3. **Run database migrations**
   ```bash
   flask db upgrade
   ```

4. **Start application**
   ```bash
   systemctl start rbm-tender-app
   systemctl status rbm-tender-app
   ```

5. **Verify deployment**
   ```bash
   # Health check
   curl -f http://localhost:5000/health
   
   # Check monitoring dashboard
   curl http://localhost:5000/monitoring/dashboard
   ```

### 🔄 Blue-Green Deployment

#### Blue Environment (Current)
1. **Verify blue environment health**
   ```bash
   curl -f http://blue.rbm-tender-app.com/health
   ```

2. **Prepare green environment**
   ```bash
   # Deploy to green environment
   # (Implementation depends on your infrastructure)
   ```

#### Green Environment (New)
1. **Deploy and test green environment**
   ```bash
   # Run smoke tests
   python scripts/testing/smoke_tests.py
   ```

2. **Switch traffic to green**
   ```bash
   # Update Cloudflare DNS
   # Point production domain to green environment
   ```

3. **Monitor green environment**
   ```bash
   # Watch metrics for 15 minutes
   # Verify all functionality works
   ```

---

## Monitoring and Alerting

### 📊 Monitoring Dashboard

#### Access Monitoring
- **Main Dashboard**: `http://localhost:5000/monitoring/dashboard`
- **API Metrics**: `http://localhost:5000/metrics`
- **Health Check**: `http://localhost:5000/health`

#### Key Metrics to Monitor
1. **System Metrics**
   - CPU usage < 80%
   - Memory usage < 90%
   - Disk usage < 85%
   - Load average < 2.0

2. **Database Metrics**
   - Connection utilization < 80%
   - Cache hit ratio > 95%
   - Query response time < 100ms
   - Active connections < 50

3. **Application Metrics**
   - Error rate < 1%
   - Response time < 2s
   - Cache hit rate > 80%
   - Circuit breakers closed

### 🚨 Alerting Rules

#### Critical Alerts (P0)
- Application down for > 2 minutes
- Database down for > 1 minute
- Disk space < 10%
- Memory usage > 95%

#### Warning Alerts (P1)
- Error rate > 5%
- Response time > 5s
- CPU usage > 80%
- Database connections > 80%

#### Info Alerts (P2)
- Feature flag changes
- Circuit breaker state changes
- Backup completion
- Deployment events

---

## Performance Optimization

### ⚡ Application Performance

#### Database Optimization
1. **Check slow queries**
   ```sql
   SELECT query, mean_exec_time, calls 
   FROM pg_stat_statements 
   ORDER BY mean_exec_time DESC 
   LIMIT 10;
   ```

2. **Analyze query performance**
   ```sql
   EXPLAIN ANALYZE SELECT * FROM deals WHERE owner_id = 1;
   ```

3. **Check index usage**
   ```sql
   SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
   FROM pg_stat_user_indexes
   ORDER BY idx_scan DESC;
   ```

#### Caching Optimization
1. **Check cache performance**
   ```bash
   python -c "
   from app.core.core_caching import advanced_cache
   stats = advanced_cache.get_stats()
   print(f'Cache hit rate: {stats[\"hit_rate\"]}%')
   print(f'Memory usage: {stats[\"used_memory\"]}')
   "
   ```

2. **Clear cache if needed**
   ```bash
   python -c "
   from app.core.core_caching import clear_all_cache
   result = clear_all_cache()
   print(f'Cache cleared: {result}')
   "
   ```

#### Memory Optimization
1. **Check memory usage**
   ```bash
   # Application memory
   ps aux | grep python | grep rbm
   
   # System memory
   free -h
   
   # Memory by process
   pmap -x $(pgrep -f rbm-tender-app)
   ```

2. **Optimize memory settings**
   ```bash
   # Update application configuration
   # Adjust worker processes
   # Review memory limits
   ```

---

## Security Incident Response

### 🔒 Security Breach

#### Immediate Response (0-15 minutes)
1. **Assess the breach**
   - Check security logs
   - Identify affected systems
   - Determine scope of compromise

2. **Contain the threat**
   - Block suspicious IPs
   - Disable compromised accounts
   - Isolate affected systems

3. **Preserve evidence**
   - Capture system state
   - Save logs and metrics
   - Document timeline

#### Investigation (15-60 minutes)
1. **Analyze attack vector**
   - Review access logs
   - Check authentication attempts
   - Examine system changes

2. **Assess data exposure**
   - Check database access logs
   - Review file system changes
   - Identify compromised data

3. **Document findings**
   - Create incident report
   - Record evidence
   - Plan remediation

#### Recovery (1-4 hours)
1. **Patch vulnerabilities**
   - Apply security updates
   - Fix configuration issues
   - Update access controls

2. **Reset compromised accounts**
   - Force password changes
   - Revoke sessions
   - Enable 2FA

3. **Verify system integrity**
   - Run security scans
   - Check data integrity
   - Test functionality

---

## Feature Flag Management

### 🚩 Feature Flag Operations

#### Enable/Disable Features
```bash
# Enable a feature flag
python -c "
from app.core.core_feature_flags import update_feature_flag
result = update_feature_flag('new_quote_ui', enabled=True, rollout_percentage=100)
print(f'Feature flag updated: {result}')
"

# Disable a feature flag
python -c "
from app.core.core_feature_flags import update_feature_flag
result = update_feature_flag('beta_features', enabled=False, rollout_percentage=0)
print(f'Feature flag updated: {result}')
"
```

#### Gradual Rollout
```bash
# Gradual rollout (25% of users)
python -c "
from app.core.core_feature_flags import update_feature_flag
result = update_feature_flag('enhanced_search', enabled=True, rollout_percentage=25)
print(f'Feature flag updated: {result}')
"

# Increase rollout (50% of users)
python -c "
from app.core.core_feature_flags import update_feature_flag
result = update_feature_flag('enhanced_search', rollout_percentage=50)
print(f'Feature flag updated: {result}')
"
```

#### Feature Flag Monitoring
```bash
# Check feature flag status
python -c "
from app.core.core_feature_flags import feature_flags
stats = feature_flags.get_stats()
print(f'Total flags: {stats[\"total_flags\"]}')
print(f'Enabled flags: {stats[\"enabled_flags\"]}')
for flag in stats['flags']:
    print(f'- {flag[\"name\"]}: {flag[\"enabled\"]} ({flag[\"rollout_percentage\"]}%)')
"
```

---

## Circuit Breaker Management

### ⚡ Circuit Breaker Operations

#### Check Circuit Breaker Status
```bash
python -c "
from app.core.core_circuit_breaker import get_circuit_breaker_stats
stats = get_circuit_breaker_stats()
for name, breaker_stats in stats.items():
    print(f'{name}: {breaker_stats[\"current_state\"]} (Success rate: {breaker_stats[\"success_rate\"]}%)')
"
```

#### Reset Circuit Breakers
```bash
# Reset specific circuit breaker
python -c "
from app.core.core_circuit_breaker import reset_circuit_breaker
result = reset_circuit_breaker('database')
print(f'Circuit breaker reset: {result}')
"

# Reset all circuit breakers
python -c "
from app.core.core_circuit_breaker import reset_all_circuit_breakers
reset_all_circuit_breakers()
print('All circuit breakers reset')
"
```

#### Circuit Breaker Health Check
```bash
python -c "
from app.core.core_circuit_breaker import check_circuit_breaker_health
health = check_circuit_breaker_health()
print(f'Circuit breaker health: {health[\"status\"]}')
if health['unhealthy_breakers']:
    print(f'Unhealthy breakers: {health[\"unhealthy_breakers\"]}')
"
```

---

## Troubleshooting Guide

### 🔧 Common Issues

#### Application Won't Start
1. **Check logs**
   ```bash
   journalctl -u rbm-tender-app -f
   ```

2. **Verify dependencies**
   ```bash
   pip list | grep -E "(Flask|SQLAlchemy|psycopg2)"
   ```

3. **Check configuration**
   ```bash
   python -c "
   from app.core.core_config import config_dict
   print('Available configs:', list(config_dict.keys()))
   "
   ```

#### Database Connection Issues
1. **Test database connectivity**
   ```bash
   psql -h localhost -U postgres -d rbm_tender_app -c "SELECT 1;"
   ```

2. **Check connection pool**
   ```bash
   python -c "
   from app import create_app, db
   app = create_app()
   with app.app_context():
       result = db.session.execute('SELECT 1').fetchone()
       print(f'Database test: {result[0]}')
   "
   ```

3. **Review database logs**
   ```bash
   tail -f /var/log/postgresql/postgresql-*.log
   ```

#### Performance Issues
1. **Check system resources**
   ```bash
   top
   iostat -x 1
   ```

2. **Analyze database performance**
   ```sql
   SELECT * FROM pg_stat_activity WHERE state = 'active';
   ```

3. **Review application metrics**
   ```bash
   curl http://localhost:5000/metrics | grep -E "(http_requests|database_query)"
   ```

### 📞 Escalation Contacts

#### Primary Support
- **System Administrator**: [Contact Info]
- **Database Administrator**: [Contact Info]
- **Application Developer**: [Contact Info]

#### Emergency Contacts
- **On-Call Engineer**: [Contact Info]
- **Manager**: [Contact Info]
- **Security Team**: [Contact Info]

#### External Support
- **AWS Support**: [Support Case]
- **Cloudflare Support**: [Support Case]
- **PostgreSQL Support**: [Community/Commercial]

---

## Quick Reference Commands

### 🚀 Application Management
```bash
# Start application
systemctl start rbm-tender-app

# Stop application
systemctl stop rbm-tender-app

# Restart application
systemctl restart rbm-tender-app

# Check status
systemctl status rbm-tender-app

# View logs
journalctl -u rbm-tender-app -f
```

### 🗄️ Database Management
```bash
# Connect to database
psql -h localhost -U postgres -d rbm_tender_app

# Run migration
flask db upgrade

# Check migration status
flask db current

# Create backup
pg_dump -h localhost -U postgres rbm_tender_app > backup.sql
```

### 📊 Monitoring Commands
```bash
# Health check
curl -f http://localhost:5000/health

# Metrics
curl http://localhost:5000/metrics

# Monitoring dashboard
curl http://localhost:5000/monitoring/dashboard
```

### 🔧 Debugging Commands
```bash
# Check Python environment
python --version
pip list

# Check database connectivity
python -c "from app import create_app, db; app = create_app(); print('OK')"

# Check feature flags
python -c "from app.core.core_feature_flags import feature_flags; print(feature_flags.get_stats())"

# Check circuit breakers
python -c "from app.core.core_circuit_breaker import get_circuit_breaker_stats; print(get_circuit_breaker_stats())"
```

---

*Last Updated: January 15, 2025*
*Version: 1.0*
*Maintained by: RBM Development Team*


