# Deployment Health Check Failures

## Problem
GitHub Actions deployment fails with health check errors:
```
Run for i in {1..5}; do
Attempt 1: http://***/health
Attempt 2: http://***/health
Attempt 3: http://***/health
Attempt 4: http://***/health
Attempt 5: http://***/health
Health check failed
Error: Process completed with exit code 1.
```

## Quick Diagnosis

### 1. Check if the service is running
```bash
sudo systemctl status rbm-tender-app
```

**Expected output:**
```
● rbm-tender-app.service - RBM Tender App
     Loaded: loaded (/etc/systemd/system/rbm-tender-app.service; enabled; preset: enabled)
     Active: active (running) since [timestamp]
```

**If inactive (dead):**
- Service is not running
- Proceed to [Service Not Running](#service-not-running)

### 2. Test local health endpoint
```bash
curl -f http://localhost:5000/health
```

**Expected output:**
```json
{"service":"rbm-tender-app","status":"healthy","timestamp":"2025-08-08T01:00:00Z"}
```

**If connection refused:**
- Service is not listening on port 5000
- Proceed to [Service Not Listening](#service-not-listening)

### 3. Test external health endpoint
```bash
curl -f http://54.206.238.122/health
```

**If 502 Bad Gateway:**
- Nginx can't connect to Flask app
- Proceed to [Nginx Proxy Issues](#nginx-proxy-issues)

## Common Issues and Solutions

### Service Not Running

**Symptoms:**
- `systemctl status` shows `inactive (dead)`
- Service keeps restarting and failing

**Check service logs:**
```bash
sudo journalctl -u rbm-tender-app --since "10 minutes ago"
```

**Common causes:**

#### 1. Missing Environment Variables
**Error:** `❌ PRODUCTION ERROR: Missing required environment variables: SECRET_KEY, DATABASE_URL`

**Solution:**
```bash
# Check if .env file exists
ls -la /opt/rbm-tender-app/config/.env

# If missing, create it
sudo nano /opt/rbm-tender-app/config/.env
# Add required variables:
# SECRET_KEY=your-secret-key
# DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
```

#### 2. Database Connection Issues
**Error:** `FATAL: sorry, too many clients already`

**Solution:**
- See [Database Connection Limit](#database-connection-limit) troubleshooting guide

#### 3. Python Import Errors
**Error:** `ModuleNotFoundError` or `ImportError`

**Solution:**
```bash
# Check if virtual environment is working
/opt/rbm-tender-app/venv/bin/python -c "import app; print('OK')"

# Reinstall dependencies if needed
cd /opt/rbm-tender-app
/opt/rbm-tender-app/venv/bin/pip install -r requirements/prod_requirements.txt
```

### Service Not Listening

**Symptoms:**
- Service shows as running but `curl localhost:5000` fails
- `sudo ss -tlnp | grep :5000` shows nothing

**Check service logs:**
```bash
sudo journalctl -u rbm-tender-app --since "5 minutes ago" -f
```

**Common causes:**

#### 1. Flask App Startup Error
**Error:** App starts but crashes before binding to port

**Solution:**
```bash
# Test app startup manually
cd /opt/rbm-tender-app
sudo -u ubuntu /opt/rbm-tender-app/venv/bin/python app_runner.py
```

#### 2. Port Already in Use
**Error:** `Address already in use`

**Solution:**
```bash
# Find what's using port 5000
sudo lsof -i :5000

# Kill the process if needed
sudo kill -9 <PID>
```

### Nginx Proxy Issues

**Symptoms:**
- Local health check works but external fails with 502
- Nginx error logs show connection refused

**Check nginx status:**
```bash
sudo systemctl status nginx
sudo tail -20 /var/log/nginx/error.log
```

**Common causes:**

#### 1. Nginx Not Running
**Solution:**
```bash
sudo systemctl start nginx
sudo systemctl enable nginx
```

#### 2. Wrong Proxy Configuration
**Check nginx config:**
```bash
sudo cat /etc/nginx/sites-available/rbm-tender-app
```

**Should contain:**
```nginx
location / {
    proxy_pass http://127.0.0.1:5000;
    proxy_redirect off;
}
```

## Manual Recovery Steps

### 1. Stop and Restart Service
```bash
sudo systemctl stop rbm-tender-app
sudo systemctl start rbm-tender-app
sudo systemctl status rbm-tender-app
```

### 2. Reset Service Failure Count
```bash
sudo systemctl reset-failed rbm-tender-app
sudo systemctl start rbm-tender-app
```

### 3. Check All Dependencies
```bash
# PostgreSQL
sudo systemctl status postgresql

# Redis
sudo systemctl status redis

# Nginx
sudo systemctl status nginx
```

### 4. Test Full Stack
```bash
# Test database
sudo -u postgres psql -c "SELECT 1;"

# Test Redis
redis-cli ping

# Test Flask app
curl -f http://localhost:5000/health

# Test nginx proxy
curl -f http://54.206.238.122/health
```

## Prevention

### 1. Monitor Service Health
```bash
# Set up monitoring
sudo systemctl status rbm-tender-app --no-pager
```

### 2. Check Logs Regularly
```bash
# Monitor service logs
sudo journalctl -u rbm-tender-app --since "1 hour ago"
```

### 3. Test Deployments
```bash
# Test health endpoint after deployments
curl -f http://54.206.238.122/health
```

## Emergency Rollback

If deployment fails and service won't start:

```bash
# Stop the service
sudo systemctl stop rbm-tender-app

# Restore from backup (if available)
sudo cp /opt/rbm-tender-app/backup/app_runner.py /opt/rbm-tender-app/app_runner.py

# Start service
sudo systemctl start rbm-tender-app

# Verify it's working
curl -f http://localhost:5000/health
```
