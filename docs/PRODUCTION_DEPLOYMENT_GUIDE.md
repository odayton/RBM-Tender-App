# Production Deployment Guide - RBM Tender App

## 🎯 Current Production Setup (September 2025)

### Overview
This document documents the **ACTUAL** production deployment currently running on EC2, which serves as the reference implementation for future deployments.

### ⚡ **Quick Deployment Process (GitHub Actions)**
```bash
# 1. Test production config locally
cp config/.env config/.env.backup
cp config/.env.production config/.env
py app_runner.py  # Select option 4: Production Mode

# 2. Run security and quality checks
py scripts/development/run_safety_scans.py
py scripts/development/run_tests.py

# 3. Restore development environment
cp config/.env.backup config/.env

# 4. Deploy via GitHub Actions (Git Flow)
git checkout develop
git checkout -b feature/your-feature-name
# Make changes, commit
git push origin feature/your-feature-name

# 5. Test on develop branch (full testing, no deployment)
git checkout develop
git merge feature/your-feature-name
git push origin develop

# 6. Deploy to production (only when develop tests pass)
git checkout main
git merge develop
git push origin main
# GitHub Actions automatically handles deployment to EC2
```

### 📋 **Pre-Deployment Checklist**
- [ ] Test with `config/.env.production` locally
- [ ] Verify login and session functionality
- [ ] Run security scans (no vulnerabilities)
- [ ] Run comprehensive tests (all passing)
- [ ] Validate environment configuration
- [ ] Have rollback plan ready

### 🧪 **Testing Status - ✅ FULLY OPERATIONAL**
- **43 Tests Passing** - 100% success rate across all test suites
- **Zero Test Failures** - Complete test suite stability achieved
- **Comprehensive Coverage** - Unit, Integration, Security, and Performance tests

### 🛡️ **Security Status - ✅ FULLY OPERATIONAL**
- **Zero Hardcoded Secrets** - All credentials managed through environment variables
- **Secure Secret Management** - Cryptographically secure key generation with fallbacks
- **Comprehensive Security Scanning** - Bandit and Safety integration with zero false positives
- **Two-Factor Authentication** - TOTP-based 2FA for admin users
- **Dependency Vulnerability Scanning** - Automated security checks for all dependencies

### Infrastructure
- **Cloud Provider**: AWS EC2 (ap-southeast-2 region)
- **Instance Type**: t3.medium
- **Operating System**: Amazon Linux 2
- **Public IP**: [Your EC2 Public IP]
- **Domain**: rbm-intranet.com (with www subdomain)

### Architecture
```
Internet → Cloudflare (HTTPS) → EC2 (HTTP port 80) → Nginx → Flask App (port 5000)
```

### Current Configuration

#### 1. Environment Variables (.env)

```bash
# Copy from your .env.production file
SECRET_KEY=your_secret_key_here
FLASK_ENV=production
HOST=0.0.0.0
PORT=5000
DATABASE_URL=your_database_url_here
LOG_LEVEL=INFO
```

#### 2. Database
- **Type**: PostgreSQL
- **Database Name**: rbm_tender_app
- **User**: [Configure in .env]
- **Host**: localhost:5432
- **Status**: ✅ Active and working

#### 3. Web Server Stack
- **Reverse Proxy**: Nginx (listening on port 80)
- **Application Server**: Gunicorn (running on port 5000)
- **Process Manager**: Systemd service (rbm-tender-app.service)
- **Static Files**: Served directly by Nginx

#### 4. Nginx Configuration
Location: `/etc/nginx/conf.d/rbm-intranet.conf`
```nginx
server {
    listen 80;
    server_name rbm-intranet.com www.rbm-intranet.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /opt/rbm-tender-app/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header Access-Control-Allow-Origin *;
        autoindex off;
    }
}
```

#### 5. Systemd Service
Location: `/etc/systemd/system/rbm-tender-app.service`

**Basic Configuration**:
```ini
[Unit]
Description=RBM Tender App
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/rbm-tender-app
Environment=PATH=/home/ubuntu/.local/bin:/usr/local/bin:/usr/bin:/bin
Environment=FLASK_ENV=production
Environment=FLASK_APP=app_runner.py
ExecStart=/usr/bin/python3 /opt/rbm-tender-app/app_runner.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**With Cloudflare Integration** (for DNS updates):
```ini
[Service]
# ... existing configuration ...
Environment="CLOUDFLARE_API_TOKEN=your_api_token_here"
Environment="CLOUDFLARE_ZONE_ID=your_zone_id_here"
Environment="CLOUDFLARE_RECORD_ID=your_record_id_here"
Environment="CLOUDFLARE_DOMAIN=rbm-intranet.com"
# ... rest of configuration ...
```

**Security Note**: Replace placeholder values with your actual Cloudflare credentials. Never commit these values to version control.

#### 6. Cloudflare Configuration
- **DNS Records**: 
  - rbm-intranet.com → [Your EC2 Public IP] (Proxied)
  - www.rbm-intranet.com → [Your EC2 Public IP] (Proxied)
- **SSL/TLS Mode**: Flexible
- **Proxy Status**: Enabled (orange cloud)
- **HTTPS**: Automatic (handled by Cloudflare)

#### 7. Automated DNS Updates
The system includes an automated Cloudflare DNS update script that keeps your domain pointing to the correct IP address when your server IP changes.

**Script Location**: `scripts/deployment/update_cloudflare_dns.sh`

**Features**:
- Automatically detects IP changes
- Updates Cloudflare DNS records
- Runs securely with environment variables
- No hardcoded credentials in the script

**Setup Required**:
- Cloudflare API token with Zone:DNS:Edit permissions
- Zone ID and Record ID from Cloudflare dashboard
- Environment variables configured in systemd service

**Usage**:

```bash
# Manual update
./scripts/deployment/update_cloudflare_dns.sh

# Automated updates (add to crontab)
# Check every 5 minutes for IP changes
*/5 * * * * /opt/rbm-tender-app/scripts/deployment/update_cloudflare_dns.sh
```

#### 7. Security Group Rules
- **Port 22 (SSH)**: 0.0.0.0/0 ✅
- **Port 80 (HTTP)**: 0.0.0.0/0 ✅
- **Port 443 (HTTPS)**: 0.0.0.0/0 ✅

## 🧪 **PRE-DEPLOYMENT TESTING (CRITICAL)**

### ⚠️ **ALWAYS Test Production Configuration Locally First**

Before deploying to production, you **MUST** test your changes with production-like configuration to avoid downtime and deployment failures.

#### **Step 1: Test with Production Environment Locally**

```bash
# 1. Backup your current development environment
cp config/.env config/.env.backup

# 2. Switch to production configuration for testing
cp config/.env.production config/.env

# 3. Start application in production mode
py app_runner.py
# Select option 4: Production Mode (SECURE) - EC2 Ready

# 4. Test critical functionality:
# - Login with production credentials
# - Session persistence
# - Database operations
# - File uploads
# - Monitoring endpoints
# - All business features

# 5. Restore development environment when testing is complete
cp config/.env.backup config/.env
```

#### **Step 2: Verify Production Configuration**

Ensure your `config/.env.production` matches your deployed production environment:

```bash
# Check production configuration
cat config/.env.production

# Verify these match your deployed production:
# - DATABASE_URL (database connection)
# - SECRET_KEY (security)
# - FLASK_CONFIG=production
# - FLASK_ENV=production
# - All feature flags and settings
```

#### **Step 3: Run Security and Quality Checks**

```bash
# Run security scans
py scripts/development/run_safety_scans.py

# Run comprehensive tests
py scripts/development/run_tests.py

# Verify no hardcoded credentials
py -m bandit -r app -f json
```

#### **Step 4: Environment Validation**

```bash
# Test environment loading
FLASK_CONFIG=production python -c "from app import create_app; app = create_app(); print('✅ Production config loads successfully')"
```

### ✅ **Deployment Readiness Checklist**

Before pushing to production, verify:
- [ ] **Production config tested locally** - Application works with production settings
- [ ] **Login functionality verified** - Can authenticate with production credentials  
- [ ] **Session persistence confirmed** - Sessions work correctly
- [ ] **Database operations tested** - All CRUD operations work
- [ ] **Security scans passed** - No vulnerabilities or hardcoded secrets
- [ ] **All tests passing** - Comprehensive test suite passes
- [ ] **Environment validation** - Production config loads without errors
- [ ] **Rollback plan ready** - Know how to revert if deployment fails

---

## 🚀 Deployment Options

### Option 1: GitHub Actions CI/CD (Recommended - Current Production)

**Automated deployment via GitHub Actions:**
- Push to `main` branch triggers automatic deployment
- Comprehensive testing and security scanning
- Automated backup creation before deployment
- Health checks and rollback capabilities
- Zero-downtime deployment process

**Process:**
1. Local testing with production config
2. `git push origin main`
3. GitHub Actions handles everything automatically

### Option 2: Manual Deployment (Emergency Only)

**Manual deployment for emergency situations:**
- Direct SSH access to EC2 server
- Manual git pull and service restart
- Use only when GitHub Actions is unavailable

### Option 3: Docker Deployment (Development Only)

This is the current production setup without Docker, using Cloudflare for domain management.

#### Prerequisites
- AWS EC2 instance running Ubuntu/Debian
- PostgreSQL database (can be on same EC2 or RDS)
- Cloudflare account with domain configured
- Python 3.8+ installed

#### Step 1: EC2 Setup

##### Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install PostgreSQL (if using local database)
sudo apt install postgresql postgresql-contrib -y

# Install nginx for reverse proxy
sudo apt install nginx -y

# Install other dependencies
sudo apt install build-essential python3-dev libpq-dev -y
```

##### Create Application User

```bash
# Create user for the app
sudo useradd -m -s /bin/bash rbmapp
sudo usermod -aG sudo rbmapp
sudo su - rbmapp
```

#### Step 2: Deploy Application

##### Clone and Setup

```bash
# Clone your repository
git clone <your-repo-url>
cd RBM-Tender-App-main

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements/prod_requirements.txt
```

##### Environment Configuration

```bash
# Copy production environment template
cp env.production .env

# Edit .env with your actual values
nano .env
```

**Required .env variables:**

```bash
FLASK_ENV=production
DATABASE_URL=your_database_url_here
SECRET_KEY=your_secret_key_here
HOST=0.0.0.0
PORT=5000
LOG_LEVEL=INFO
DOMAIN=rbm-intranet.com
```

#### Step 3: Database Setup

##### PostgreSQL Configuration

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE rbm_tender_app;
CREATE USER your_username WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE rbm_tender_app TO your_username;
\q

# Test connection
psql -h localhost -U your_username -d rbm_tender_app
```

##### PostgreSQL Production Configuration

**CRITICAL**: For production deployments, configure PostgreSQL connection limits:

```bash
# Edit PostgreSQL configuration
sudo nano /etc/postgresql/16/main/postgresql.conf

# Increase max_connections for production (default 100 is too low)
max_connections = 200

# Restart PostgreSQL to apply changes
sudo systemctl restart postgresql

# Verify configuration
sudo -u postgres psql -c "SHOW max_connections;"
```

**Database User Setup**:
```bash
# Ensure database user has proper password and permissions
sudo -u postgres psql -d postgres -c "ALTER USER your_username WITH PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE rbm_tender_app TO your_username;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_username;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_username;"
```

**Connection Monitoring**:
```bash
# Monitor active connections
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"

# View active connections
sudo -u postgres psql -c "SELECT pid, usename, application_name, client_addr, state FROM pg_stat_activity WHERE state = 'active';"

# Terminate idle connections if needed
sudo -u postgres psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND pid <> pg_backend_pid();"
```

##### Run Migrations

```bash
# Activate virtual environment
source venv/bin/activate

# Run database migrations
flask db upgrade
```

#### Step 4: Nginx Configuration

##### Install and Configure Nginx

```bash
# Install nginx
sudo apt install nginx -y

# Copy nginx configuration
sudo cp nginx.conf /etc/nginx/sites-available/rbm-intranet
sudo ln -s /etc/nginx/sites-available/rbm-intranet /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

#### Step 5: Application Service

##### Create Systemd Service

```bash
sudo nano /etc/systemd/system/rbm-tender-app.service
```

Add the following content:
```ini
[Unit]
Description=RBM Tender App
After=network.target

[Service]
Type=simple
User=rbmapp
WorkingDirectory=/home/rbmapp/RBM-Tender-App-main
Environment=PATH=/home/rbmapp/venv/bin
ExecStart=/home/rbmapp/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 app:create_app()
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

##### Start the Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Start and enable the service
sudo systemctl start rbm-tender-app
sudo systemctl enable rbm-tender-app

# Check status
sudo systemctl status rbm-tender-app
```

#### Step 6: SSL Setup

##### Option A: Cloudflare (Recommended)
1. Sign up at https://cloudflare.com
2. Add your domain
3. Configure DNS to point to your EC2 IP
4. Set SSL/TLS to "Full (strict)"
5. Enable "Always Use HTTPS"

#### Step 7: Cloudflare DNS Automation Setup

**Purpose**: Automatically update DNS records when your server IP changes.

**Prerequisites**:
- Cloudflare account with domain configured
- API token with Zone:DNS:Edit permissions

**Step 7a: Create Cloudflare API Token**
1. Go to Cloudflare Dashboard → Profile → API Tokens
2. Click "Create Token"
3. Use "Edit zone DNS" template
4. Set Zone Resources to include your domain
5. Copy the generated token

**Step 7b: Get Zone and Record IDs**
1. **Zone ID**: Go to domain overview page, copy from right sidebar
2. **Record ID**: Use API call to list DNS records:

   ```bash
   curl -X GET "https://api.cloudflare.com/client/v4/zones/YOUR_ZONE_ID/dns_records" \
        -H "Authorization: Bearer YOUR_API_TOKEN" \
        -H "Content-Type: application/json"
   ```

**Step 7c: Configure Systemd Service**
Add environment variables to your service file:
```ini
[Service]
# ... existing configuration ...
Environment="CLOUDFLARE_API_TOKEN=your_api_token_here"
Environment="CLOUDFLARE_ZONE_ID=your_zone_id_here"
Environment="CLOUDFLARE_RECORD_ID=your_record_id_here"
Environment="CLOUDFLARE_DOMAIN=rbm-intranet.com"
```

**Step 7d: Test DNS Update Script**

```bash
# Test manual update
./scripts/deployment/update_cloudflare_dns.sh

# Set up automated updates (optional)
crontab -e
# Add: */5 * * * * /path/to/your/script.sh
```

##### Option B: Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d rbm-intranet.com -d www.rbm-intranet.com

# Set up auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🔄 **GitHub Actions CI/CD Pipeline**

### **Current CI/CD Workflow (Fully Automated)**

Your GitHub Actions pipeline (`.github/workflows/ci-cd.yml`) handles complete deployment:

#### **Pipeline Jobs:**

**1. Quality Checks Job**
- Security scanning with Bandit
- Dependency vulnerability checks with Safety
- Code quality analysis
- Linting and formatting checks

**2. Testing Job**
- PostgreSQL and Redis service setup
- Database migrations
- Unit tests (43 tests total)
- Integration tests
- Security tests
- Performance tests
- Coverage reporting

**3. Build Job** (main branch only)
- Create deployment package
- Package application files
- Generate deployment script
- Upload artifacts

**4. Deploy Job** (main branch only)
- SSH into EC2 server using GitHub secrets
- Create automatic backup of current deployment
- Upload new deployment package
- Run deployment script on server
- Health check verification
- Success/failure notifications

**5. Post-Deployment Verification**
- Smoke tests on all endpoints
- Performance checks
- Database connectivity verification
- Monitoring dashboard validation

#### **Deployment Process:**
```bash
# 1. Local testing (required)
cp config/.env.production config/.env
py app_runner.py  # Test production mode
cp config/.env.backup config/.env  # Restore dev config

# 2. Push to GitHub (triggers automatic deployment)
git add .
git commit -m "Your deployment message"
git push origin main

# 3. Monitor GitHub Actions (automatic)
# - Go to GitHub repository → Actions tab
# - Watch deployment progress
# - All steps handled automatically
```

#### **Automatic Features:**
- ✅ **Zero-downtime deployment**
- ✅ **Automatic backup creation**
- ✅ **Health checks and rollback**
- ✅ **Comprehensive testing**
- ✅ **Security scanning**
- ✅ **Performance monitoring**

### **Environment Variable Management**

#### **GitHub Secrets Setup**
Configure these secrets in your GitHub repository:

- `SSH_PRIVATE_KEY` - Private key for EC2 access
- `SSH_USER` - EC2 username (ubuntu)
- `SSH_HOST` - EC2 public IP or domain
- `TEST_SECRET_KEY` - Test secret key for CI/CD testing
- `PRODUCTION_SECRET_KEY` - Production secret key (for actual deployment)

#### **Local vs Production Environment**
- **Local Testing**: Use `config/.env.production` for pre-deployment testing
- **CI/CD Testing**: Use GitHub secrets for automated testing
- **Production**: Use actual production environment variables on server

## 🔧 Maintenance and Monitoring

### Check Application Status

```bash
# Check service status
sudo systemctl status rbm-tender-app

# Check nginx status
sudo systemctl status nginx

# Check logs
sudo journalctl -u rbm-tender-app -f
sudo tail -f /var/log/nginx/error.log
```

### Database Maintenance

```bash
# Connect to database
psql -h localhost -U your_username -d rbm_tender_app

# Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Backup Strategy

```bash
# Database backup
pg_dump -h localhost -U your_username rbm_tender_app > backup_$(date +%Y%m%d_%H%M%S).sql

# Application backup
tar -czf app_backup_$(date +%Y%m%d_%H%M%S).tar.gz /home/rbmapp/RBM-Tender-App-main
```

### DNS Management

```bash
# Check current DNS status
./scripts/deployment/update_cloudflare_dns.sh

# View Cloudflare DNS records
curl -X GET "https://api.cloudflare.com/client/v4/zones/YOUR_ZONE_ID/dns_records" \
     -H "Authorization: Bearer YOUR_API_TOKEN" \
     -H "Content-Type: application/json"

# Manual DNS update (if needed)
./scripts/deployment/update_cloudflare_dns.sh
```

## 🚨 Troubleshooting

### Common Issues

#### Application Won't Start

```bash
# Check logs
sudo journalctl -u rbm-tender-app -f

# Check environment variables
sudo -u rbmapp cat /home/rbmapp/RBM-Tender-App-main/.env

# Check database connection
sudo -u rbmapp psql -h localhost -U your_username -d rbm_tender_app
```

#### PostgreSQL Connection Issues (500 Errors)

**Symptoms**: 500 errors on `/deals/`, `/auth/login`, application logs show "too many clients already"

**Root Cause**: PostgreSQL connection limit exceeded or database user authentication issues

**Solution**:
```bash
# 1. Check current connection count
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"

# 2. Check max_connections setting
sudo -u postgres psql -c "SHOW max_connections;"

# 3. If connections exceeded, increase limit
sudo nano /etc/postgresql/16/main/postgresql.conf
# Change: max_connections = 200
sudo systemctl restart postgresql

# 4. Fix database user authentication
sudo -u postgres psql -d postgres -c "ALTER USER your_username WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE rbm_tender_app TO your_username;"

# 5. Test connection
PGPASSWORD='your_password' psql -h localhost -U your_username -d rbm_tender_app -c "SELECT version();"

# 6. Restart application
sudo systemctl restart rbm-tender-app
```

**Prevention**: Always configure PostgreSQL with appropriate connection limits (200+) for production deployments.

#### Nginx Issues

```bash
# Check nginx configuration
sudo nginx -t

# Check nginx logs
sudo tail -f /var/log/nginx/error.log

# Restart nginx
sudo systemctl restart nginx
```

#### SSL Issues
- Verify Cloudflare DNS settings
- Check SSL/TLS mode in Cloudflare
- Ensure proxy status is enabled (orange cloud)

#### DNS Update Script Issues

```bash
# Check if environment variables are set
sudo systemctl show rbm-tender-app --property=Environment

# Verify API token permissions
curl -X GET "https://api.cloudflare.com/client/v4/user/tokens/verify" \
     -H "Authorization: Bearer YOUR_API_TOKEN"

# Check script permissions
ls -la scripts/deployment/update_cloudflare_dns.sh
chmod +x scripts/deployment/update_cloudflare_dns.sh

# Test script manually
cd /opt/rbm-tender-app
./scripts/deployment/update_cloudflare_dns.sh
```

## 📚 Additional Resources

- **[Main Documentation](README.md)** - Quick start and maintenance guide
- **[Full System Documentation](RBM_TENDER_APP_DOCUMENTATION.md)** - Complete technical reference
- **[Backup Manager](backup_manager.py)** - Automated backup system 