# Login and Session Troubleshooting Guide

## Overview
This document provides a comprehensive guide for troubleshooting login and session issues in the RBM Tender App. It covers the complete resolution process for login forms that refresh/clear fields and session persistence problems.

## Common Symptoms
- Login form refreshes and clears fields after clicking login
- User gets redirected back to login page after successful authentication
- 500 Internal Server Error on login attempts
- 502 Bad Gateway errors
- Rate limit exceeded errors
- Session not persisting between requests

## Root Causes Identified
1. **Configuration Issues**: App defaulting to DevelopmentConfig instead of ProductionConfig
2. **Flask-Session Missing**: Session management not properly configured
3. **Rate Limiting Issues**: Decorator expecting different parameter format
4. **Session Cookie Security**: Secure cookies preventing HTTP session persistence
5. **Malformed Systemd Service**: Service file syntax errors preventing proper startup

## Complete Troubleshooting Process

### Step 1: Initial Diagnosis
```bash
# Check service status
sudo systemctl status rbm-tender-app

# Check recent logs
sudo journalctl -u rbm-tender-app --lines=20

# Check for errors
sudo journalctl -u rbm-tender-app --since "10 minutes ago" | grep -i "error\|exception\|traceback"
```

### Step 2: Test Login Functionality
```bash
# Test login page (GET)
curl -X GET http://localhost:5000/auth/login -v

# Test login functionality (POST)
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=owen@rbmsystems.com.au&password=admin123" -v
```

### Step 3: Check Configuration Issues
```bash
# Check environment variables
echo $FLASK_CONFIG
echo $FLASK_ENV

# Test app creation manually
python -c "from app import create_app; app = create_app(); print('App created successfully')"
```

**Expected Error**: `ConfigurationError: DEV_DATABASE_URL must be set for development environment`

**Solution**: Fix the `create_app()` function in `app/__init__.py` to not default to DevelopmentConfig.

### Step 4: Fix Configuration Loading
**File**: `app/__init__.py`

**Problem**: App defaults to DevelopmentConfig when no config_class is specified.

**Fix**: Replace the else block in `create_app()`:
```python
# OLD CODE (PROBLEMATIC)
else:
    # Default to development if no config specified
    from .core.core_config import DevelopmentConfig
    logger.info("No config specified, using default DevelopmentConfig")
    app.config.from_object(DevelopmentConfig)
    config_instance = DevelopmentConfig()
    config_instance.init_app(app)
    app._config_initialized = True

# NEW CODE (FIXED)
else:
    # Let CoreInitializer handle configuration loading based on FLASK_CONFIG
    logger.info("No config specified, CoreInitializer will load based on FLASK_CONFIG environment variable")
```

### Step 5: Install and Configure Flask-Session
```bash
# Install Flask-Session
pip install Flask-Session
```

**File**: `app/extensions.py`
**Add**:
```python
from flask_session import Session

# Add to extensions
session = Session()
```

**File**: `app/core/core_init.py`
**Update**:
```python
def __init__(self, app: Flask, db, login_manager, migrate, csrf, limiter=None, session=None):
    # ... existing parameters ...
    self.session = session

def init_app(self):
    # ... existing calls ...
    self.init_session()

def init_session(self):
    """Initialize Flask-Session."""
    if self.session:
        self.session.init_app(self.app)
        core_logger.app_logger.info("Flask-Session Initialized.")
    else:
        core_logger.app_logger.warning("Flask-Session not provided. Using default session handling.")
```

**File**: `app/__init__.py`
**Update**:
```python
from .extensions import db, migrate, login_manager, csrf, limiter, session

# Update CoreInitializer call
core_initializer = CoreInitializer(app, db, login_manager, migrate, csrf, limiter, session)
```

### Step 6: Fix Rate Limiting Issues
**Problem**: `TypeError: sensitive_rate_limit() takes 0 positional arguments but 1 was given`

**File**: `app/core/core_rate_limiting.py`
**Fix**:
```python
def sensitive_rate_limit(limit: str = None):
    """Rate limit for sensitive operations."""
    if limit is None:
        limit = RateLimitConfig.DEFAULT_LIMITS['sensitive']
    return rate_limit(limit)
```

**Problem**: `AttributeError: 'set' object has no attribute 'limit'`

**Fix**: Update the `rate_limit` decorator:
```python
@wraps(f)
def decorated_function(*args, **kwargs):
    limiter = current_app.extensions.get('limiter')
    if limiter:
        # Handle case where limiter is a set containing the Limiter object
        if isinstance(limiter, set):
            limiter = next(iter(limiter))
        return limiter.limit(limit)(f)(*args, **kwargs)
    return f(*args, **kwargs)
```

### Step 7: Fix Session Cookie Security
**Problem**: `SESSION_COOKIE_SECURE = True` prevents cookies from being sent over HTTP.

**File**: `app/core/core_config.py`
**Fix**: In `ProductionConfig` class:
```python
class ProductionConfig(Config):
    # ... existing code ...
    SESSION_COOKIE_SECURE = False  # Set to False for HTTP connections
    REMEMBER_COOKIE_SECURE = False  # Set to False for HTTP connections
```

### Step 8: Adjust Rate Limits
**File**: `app/core/core_rate_limiting.py`
**Fix**: Increase rate limits for testing:
```python
DEFAULT_LIMITS = {
    'general': '100/minute',
    'auth': '20/minute',  # Increased from 5 to 20
    'admin': '20/minute',
    'api': '60/minute',
    'sensitive': '10/minute',  # Increased from 3 to 10
    'upload': '10/minute',
    'download': '30/minute'
}
```

### Step 9: Fix Systemd Service (if needed)
**Problem**: Malformed systemd service file.

**File**: `/etc/systemd/system/rbm-tender-app.service`
**Check for**:
- `[Unit]` header on same line as `ExecStart`
- Proper section separation

**Fix**: Ensure proper format:
```ini
[Unit]
Description=RBM Tender App
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/rbm-tender-app
Environment=DATABASE_URL=postgresql://...
ExecStart=/opt/rbm-tender-app/venv/bin/python /opt/rbm-tender-app/app_runner.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Step 10: Create Session Directory
```bash
# Create session directory
mkdir -p /opt/rbm-tender-app/instance/sessions
chown ubuntu:ubuntu /opt/rbm-tender-app/instance/sessions
```

### Step 11: Restart and Test
```bash
# Restart service
sudo systemctl restart rbm-tender-app

# Check status
sudo systemctl status rbm-tender-app

# Monitor logs
sudo journalctl -u rbm-tender-app -f

# Test login
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=owen@rbmsystems.com.au&password=admin123" -v
```

## Verification Steps

### 1. Check Service Status
```bash
sudo systemctl status rbm-tender-app
```
**Expected**: `Active: active (running)`

### 2. Check Logs for Success
```bash
sudo journalctl -u rbm-tender-app --lines=10
```
**Expected**: No errors, service started successfully

### 3. Test Login Endpoint
```bash
curl -X GET http://localhost:5000/auth/login -v
```
**Expected**: `HTTP/1.1 200 OK`

### 4. Test Login Functionality
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=owen@rbmsystems.com.au&password=admin123" -v
```
**Expected**: `HTTP/1.1 302 Found` (redirect after successful login)

### 5. Check Session Files
```bash
ls -la /opt/rbm-tender-app/instance/sessions/
```
**Expected**: Session files created after login

### 6. Test Browser Login
- Navigate to: `http://54.206.238.122`
- Login with: `owen@rbmsystems.com.au` / `admin123`
- **Expected**: Successful login, redirected to home page, session persists

## Common Error Messages and Solutions

### "ConfigurationError: DEV_DATABASE_URL must be set"
**Cause**: App defaulting to DevelopmentConfig
**Solution**: Fix `create_app()` function to let CoreInitializer handle config

### "AttributeError: 'set' object has no attribute 'limit'"
**Cause**: Rate limiter stored as set instead of Limiter object
**Solution**: Fix rate limiting decorator to handle set case

### "TypeError: sensitive_rate_limit() takes 0 positional arguments"
**Cause**: Function called with arguments but doesn't accept them
**Solution**: Update function signature to accept optional limit parameter

### "502 Bad Gateway"
**Cause**: Flask app not running or crashed
**Solution**: Check service status and logs, restart service

### "Rate limit exceeded"
**Cause**: Rate limits too restrictive
**Solution**: Increase rate limits in configuration

### Login redirects back to login page
**Cause**: Session cookies not being sent (SECURE flag)
**Solution**: Set `SESSION_COOKIE_SECURE = False` for HTTP connections

## Prevention Measures

1. **Always test configuration loading** after changes
2. **Use proper environment variables** for different environments
3. **Test rate limiting** with realistic limits
4. **Verify session configuration** matches deployment environment
5. **Monitor logs** during deployment and testing
6. **Test login flow** end-to-end after any authentication changes

## Files Modified During Resolution

1. `app/__init__.py` - Fixed configuration loading
2. `app/extensions.py` - Added Flask-Session
3. `app/core/core_init.py` - Added session initialization
4. `app/core/core_rate_limiting.py` - Fixed rate limiting decorators
5. `app/core/core_config.py` - Fixed session cookie security
6. `/etc/systemd/system/rbm-tender-app.service` - Fixed service file format

## Environment Variables Required

```bash
FLASK_CONFIG=production
FLASK_ENV=production
DATABASE_URL=postgresql://user:pass@localhost:5432/db
SECRET_KEY=your-secret-key
# ... other required variables
```

## Dependencies Added

```bash
pip install Flask-Session
```

---

**Last Updated**: September 19, 2025
**Resolved By**: AI Assistant
**Status**: ✅ RESOLVED - Login and session persistence working correctly