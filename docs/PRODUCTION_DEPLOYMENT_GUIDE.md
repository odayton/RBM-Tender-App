# Production Deployment Guide - RBM Tender App

## 🎯 Current Production Setup (August 2025)

### Overview
This document documents the **ACTUAL** production deployment currently running on EC2, which serves as the reference implementation for future deployments.

### Infrastructure
- **Cloud Provider**: AWS EC2 (ap-southeast-2 region)
- **Instance Type**: t2.micro or similar
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
- **Type**: PostgreSQL (migrated from SQLite)
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
        alias /home/ec2-user/RBM-Tender-App-main/RBM-Tender-App-main/app/static/;
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
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/RBM-Tender-App-main/RBM-Tender-App-main
Environment=PATH=/home/ec2-user/.local/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=/home/ec2-user/.local/bin/gunicorn --workers 1 --bind 0.0.0.0:5000 --chdir /home/ec2-user/RBM-Tender-App-main/RBM-Tender-App-main "app:create_app()"
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
*/5 * * * * /home/ec2-user/RBM-Tender-App-main/scripts/deployment/update_cloudflare_dns.sh
```

#### 7. Security Group Rules
- **Port 22 (SSH)**: 0.0.0.0/0 ✅
- **Port 80 (HTTP)**: 0.0.0.0/0 ✅
- **Port 443 (HTTPS)**: 0.0.0.0/0 ✅

## 🚀 Deployment Options

### Option 1: Docker Deployment (Recommended for Development)

Use the provided deployment scripts:
- **Windows**: `deploy.bat`
- **Linux/macOS**: `deploy.sh`

These scripts handle:
- Environment setup
- SSL certificate generation
- Service orchestration
- Health checks

### Option 2: Native EC2 Deployment (Current Production)

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
cd /home/ec2-user/RBM-Tender-App-main/RBM-Tender-App-main
./scripts/deployment/update_cloudflare_dns.sh
```

## 📚 Additional Resources

- **[Main Documentation](README.md)** - Quick start and maintenance guide
- **[Full System Documentation](RBM_TENDER_APP_DOCUMENTATION.md)** - Complete technical reference
- **[Backup Manager](backup_manager.py)** - Automated backup system 