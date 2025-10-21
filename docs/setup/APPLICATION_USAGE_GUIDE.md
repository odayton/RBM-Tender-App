# RBM Tender App - Usage Guide

## Quick Start

### Development
```bash
# Set environment
export FLASK_ENV=development  # or set in .env file

# Run with Flask CLI (recommended)
flask run

# OR run with manage.py
python manage.py dev

# OR run directly
python wsgi.py
```

### Testing Production Config Locally
```bash
# Test production settings locally
python manage.py prod-test

# Or use Flask CLI
FLASK_ENV=production python wsgi.py
```

### Production Deployment
```bash
# Use Gunicorn (recommended)
FLASK_ENV=production gunicorn -w 4 -b 0.0.0.0:5000 wsgi:application

# OR use systemd service (current EC2 setup)
sudo systemctl start rbm-tender-app
```

---

## File Structure

### `wsgi.py` - Main Entry Point
**Purpose:** Single entry point for all environments  
**Used by:** Gunicorn, Flask CLI, production servers

**Features:**
- Environment-based configuration
- Proper logging (no print statements)
- Security validation for production
- WSGI-compliant

**Usage:**
```bash
# Development
FLASK_ENV=development python wsgi.py

# Production (Gunicorn)
FLASK_ENV=production gunicorn wsgi:application
```

### `manage.py` - Development CLI
**Purpose:** Development and maintenance commands  
**Used by:** Developers for local development

**Available Commands:**
```bash
python manage.py dev              # Run development server
python manage.py prod-test        # Test production config
python manage.py shell            # Interactive Python shell
python manage.py test             # Run test suite
python manage.py test --coverage  # Run tests with coverage
python manage.py db-migrate "msg" # Create migration
python manage.py db-upgrade       # Apply migrations
python manage.py info             # Show configuration
```

### `config/.env` - Environment Variables
**Purpose:** Store environment-specific configuration  
**Security:** Never commit to Git (in .gitignore)

**Required Variables:**
- `FLASK_ENV` - Environment name (development/production/testing)
- `SECRET_KEY` - Minimum 32 characters
- `DATABASE_URL` - PostgreSQL connection string

---

## Environment Configuration

### Development
```bash
# In .env file
FLASK_ENV=development
DATABASE_URL=postgresql://user:pass@localhost/rbm_dev
SECRET_KEY=dev-secret-key-change-in-production

# Run
python manage.py dev
# OR
flask run
```

**Features:**
- Debug mode enabled
- Auto-reload on code changes
- Detailed error pages
- Localhost only (127.0.0.1)

### Production
```bash
# In .env file (on server)
FLASK_ENV=production
DATABASE_URL=postgresql://user:pass@production-db/rbm_prod
SECRET_KEY=<64-character-secure-key>
HOST=0.0.0.0
PORT=5000

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:application
```

**Features:**
- Debug mode disabled
- Security headers enabled
- Rate limiting active
- Production-optimized

### Testing
```bash
# In .env file or environment
FLASK_ENV=testing
TEST_DATABASE_URL=postgresql://user:pass@localhost/rbm_test

# Run tests
python manage.py test
# OR
pytest
```

---

## Migration from Old app_runner.py

### Old Way (Interactive Menu)
```bash
python app_runner.py
# Select option 1-4 from menu
```

### New Way (Environment Variables)
```bash
# Development
FLASK_ENV=development python manage.py dev

# Production testing
FLASK_ENV=production python manage.py prod-test

# Actual production
FLASK_ENV=production gunicorn wsgi:application
```

### Comparison

| Old Approach | New Approach |
|--------------|--------------|
| Interactive menu | Environment variables |
| Print statements | Proper logging |
| Mixed dev/prod code | Separate concerns |
| Manual mode selection | Automatic based on FLASK_ENV |
| One file for everything | wsgi.py (prod) + manage.py (dev) |

---

## Benefits of New Approach

### 1. Industry Standard
- Follows 12-Factor App principles
- WSGI-compliant for any server
- Compatible with all deployment tools

### 2. Better Security
- No print statements exposing data
- Proper logging with levels
- Environment-based config
- Validates production settings

### 3. Automation Friendly
- No interactive prompts
- CI/CD compatible
- Scriptable
- Docker-ready

### 4. Cleaner Separation
- `wsgi.py` - Production entry point
- `manage.py` - Development tools
- Clear responsibilities

### 5. More Flexible
- Works with Flask CLI
- Works with any WSGI server
- Easy to extend
- Standard Python practices

---

## Common Workflows

### Daily Development
```bash
# Start development server
python manage.py dev

# Make changes, server auto-reloads

# Run tests
python manage.py test
```

### Creating Migrations
```bash
# Create migration
python manage.py db-migrate "Add user email field"

# Review generated file
# migrations/versions/xxx_add_user_email_field.py

# Apply migration
python manage.py db-upgrade

# Test it works
python manage.py dev
```

### Debugging
```bash
# Start interactive shell
python manage.py shell

# Test queries
>>> from app.models import User
>>> User.query.first()
>>> db.session.query(User).count()
```

### Pre-Deployment Testing
```bash
# Test production config locally
python manage.py prod-test

# Verify everything works
# Then deploy to actual production
```

---

## EC2 Production Setup

### Option 1: Keep Current Systemd Service
```ini
# /etc/systemd/system/rbm-tender-app.service
[Service]
ExecStart=/opt/rbm-tender-app/venv/bin/python /opt/rbm-tender-app/wsgi.py
Environment=FLASK_ENV=production
```

### Option 2: Use Gunicorn (Recommended)
```ini
# /etc/systemd/system/rbm-tender-app.service
[Service]
ExecStart=/opt/rbm-tender-app/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 wsgi:application
Environment=FLASK_ENV=production
```

---

## Troubleshooting

### "Missing required environment variables"
```bash
# Check your .env file
cat config/.env

# Ensure it has:
# FLASK_ENV=development
# DATABASE_URL=postgresql://...
# SECRET_KEY=...
```

### "Module not found"
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements/base_requirements.txt
```

### "Database connection failed"
```bash
# Test database connection
python manage.py shell
>>> from app import db
>>> db.engine.connect()
```

---

## Summary

**For Development:**
```bash
python manage.py dev
```

**For Production:**
```bash
FLASK_ENV=production gunicorn wsgi:application
```

**For Testing:**
```bash
python manage.py test
```

**For Maintenance:**
```bash
python manage.py --help
```

Simple, standard, secure! 🎯

