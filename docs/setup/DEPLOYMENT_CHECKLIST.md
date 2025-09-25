# RBM Tender App - Deployment Setup Checklist

## ✅ Pre-Deployment Checklist

### 1. AWS EC2 Instance Setup
- [ ] Launch EC2 instance (Ubuntu 22.04 LTS) - t3.medium recommended
- [ ] Configure security groups:
  - [ ] SSH (22) - Your IP only
  - [ ] HTTP (80) - 0.0.0.0/0
  - [ ] HTTPS (443) - 0.0.0.0/0
- [ ] Connect to instance via SSH
- [ ] Run server setup script:
  ```bash
  sudo ./scripts/deployment/setup-aws-ec2.sh your-domain.com
  ```

### 2. Domain Configuration
- [ ] Point your domain to EC2 instance IP
- [ ] Update Cloudflare DNS (if using Cloudflare)
- [ ] Wait for DNS propagation (5-15 minutes)

### 3. SSH Key Setup
- [ ] Generate SSH key pair for GitHub Actions:
  ```bash
  ssh-keygen -t rsa -b 4096 -C "github-actions@rbm-tender-app"
  ```
- [ ] Add public key to server:
  ```bash
  # Copy public key to server
  cat ~/.ssh/github_actions_rsa.pub | ssh ubuntu@your-server-ip "cat >> ~/.ssh/authorized_keys"
  ```
- [ ] Test SSH connection:
  ```bash
  ssh -i ~/.ssh/github_actions_rsa ubuntu@your-server-ip
  ```

### 4. GitHub Repository Setup
- [ ] Go to your GitHub repository
- [ ] Navigate to Settings → Secrets and variables → Actions
- [ ] Add the following secrets:

#### Required Secrets:
- [ ] `SSH_PRIVATE_KEY` - Contents of `~/.ssh/github_actions_rsa`
- [ ] `SSH_USER` - `ubuntu` (or your server username)
- [ ] `SSH_HOST` - Your EC2 instance public IP or domain
- [ ] `APP_HOST` - Your domain name (e.g., `rbm-tender-app.yourdomain.com`)

#### Optional Secrets (for notifications):
- [ ] `SLACK_WEBHOOK_URL` - Slack webhook URL
- [ ] `TEAMS_WEBHOOK_URL` - Teams webhook URL
- [ ] `EMAIL_RECIPIENTS` - Comma-separated email addresses

### 5. Environment Configuration
- [ ] Update `config/production.env` with your settings:
  - [ ] Change `SECRET_KEY` to a secure random string
  - [ ] Update `APP_URL` to your domain
  - [ ] Update `MONITORING_URL` to your domain
  - [ ] Add Sentry DSN if using error tracking
  - [ ] Configure email settings if needed

### 6. Database Setup
- [ ] Connect to PostgreSQL:
  ```bash
  sudo -u postgres psql -d rbm_tender_app
  ```
- [ ] Verify database is accessible
- [ ] Test connection from application

### 7. SSL Certificate (Optional)
- [ ] If using custom domain, SSL will be automatically configured
- [ ] If using IP only, skip SSL setup

## 🚀 Deployment Process (GitHub Actions)

### 1. Automated Deployment via GitHub Actions
- [ ] Test production config locally first
- [ ] Push your code to `main` branch
- [ ] Go to GitHub Actions tab
- [ ] Monitor the CI/CD pipeline automatically
- [ ] Verify deployment success
- [ ] Check health endpoints

### 2. Post-Deployment Verification
- [ ] Check application health: `https://your-domain.com/health`
- [ ] Test login functionality
- [ ] Verify monitoring dashboard: `https://your-domain.com/monitoring/dashboard`
- [ ] Check metrics endpoint: `https://your-domain.com/metrics`

### 3. Monitoring Setup
- [ ] Access monitoring dashboard
- [ ] Verify all metrics are collecting
- [ ] Test health check automation
- [ ] Configure alerting (if using notifications)

## 🔧 Troubleshooting

### Common Issues:

#### 1. SSH Connection Failed
```bash
# Check SSH key permissions
chmod 600 ~/.ssh/github_actions_rsa
chmod 644 ~/.ssh/github_actions_rsa.pub

# Test connection
ssh -i ~/.ssh/github_actions_rsa -v ubuntu@your-server-ip
```

#### 2. Database Connection Failed
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check database exists
sudo -u postgres psql -l | grep rbm_tender_app

# Test connection
psql -h localhost -U rbm_tender_app -d rbm_tender_app
```

#### 3. Application Won't Start
```bash
# Check service status
sudo systemctl status rbm-tender-app

# Check logs
sudo journalctl -u rbm-tender-app -f

# Check application directory
ls -la /opt/rbm-tender-app/
```

#### 4. Nginx Issues
```bash
# Check Nginx status
sudo systemctl status nginx

# Test configuration
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log
```

## 📞 Support Commands

### Useful Commands:
```bash
# Monitor system
monitor-rbm-tender-app

# Check application logs
sudo journalctl -u rbm-tender-app -f

# Check Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Check database logs
sudo tail -f /var/log/postgresql/postgresql-*.log

# Restart services
sudo systemctl restart rbm-tender-app
sudo systemctl restart nginx
sudo systemctl restart postgresql
sudo systemctl restart redis-server

# Check disk space
df -h

# Check memory usage
free -h

# Check running processes
htop
```

## 🎯 Success Criteria

Your deployment is successful when:
- [ ] Application responds at `https://your-domain.com`
- [ ] Health check passes: `https://your-domain.com/health`
- [ ] Monitoring dashboard loads: `https://your-domain.com/monitoring/dashboard`
- [ ] All services are running: `monitor-rbm-tender-app`
- [ ] No errors in logs: `sudo journalctl -u rbm-tender-app`
- [ ] Database is accessible and responsive
- [ ] SSL certificate is valid (if using custom domain)

## 📋 Next Steps After Deployment

1. **Configure Monitoring Alerts** (optional)
2. **Set up Regular Backups** (automated)
3. **Configure Log Rotation** (already set up)
4. **Set up SSL Certificate Renewal** (automated)
5. **Configure Firewall Rules** (already set up)
6. **Test Rollback Procedures** (important!)

---

**Need Help?** Check the troubleshooting section above or review the logs for specific error messages.



