# Production Deployment
**Frequency**: As needed  
**Duration**: 10-15 minutes  
**Last Updated**: 2025-01-15  

---

## 🚀 **Pre-Deployment Checklist**

### **Before Starting:**
- [ ] All tests pass locally
- [ ] Code reviewed and approved
- [ ] Database migrations tested
- [ ] Staging environment verified
- [ ] Team notified of deployment
- [ ] Backup created (if needed)

---

## 📋 **Deployment Steps**

### **Step 1: Pre-Deployment Verification (2 minutes)**

```bash
# Run tests locally
pytest tests/ -v

# Check current production status
curl -I https://rbm-intranet.com

# Verify database connectivity
flask db current
```

### **Step 2: Create Backup (3 minutes)**

```bash
# Create database backup
flask db backup --description "pre-deployment-backup"

# Verify backup was created
ls -la app/instance/backups/
```

### **Step 3: Deploy to Production (5 minutes)**

#### **Option A: GitHub Actions Deployment (Recommended)**

```bash
# Push to main branch (triggers automatic CI/CD)
git push origin main

# Monitor deployment in GitHub Actions
# - Go to GitHub repository → Actions tab
# - Watch CI/CD pipeline progress
# - All steps handled automatically:
#   * Quality checks and security scanning
#   * Comprehensive testing (43 tests)
#   * Build deployment package
#   * Deploy to EC2 server
#   * Health checks and verification
```

#### **Option B: Manual Deployment (Emergency Only)**

```bash
# SSH into production server
ssh -i RBM-App-Key-Updated.pem ec2-user@54.253.118.23

# Navigate to app directory
cd /opt/rbm-tender-app

# Pull latest changes
git pull origin main

# Install dependencies
pip install -r requirements/base_requirements.txt

# Run database migrations
flask migrate upgrade

# Restart application
sudo systemctl restart rbm-tender-app

# Wait for restart
sleep 30
```

### **Step 4: Verification (3 minutes)**

```bash
# Check application health
curl http://54.253.118.23:5000/health

# Check website access
curl -I https://rbm-intranet.com

# Test critical functionality
curl https://rbm-intranet.com/auth/login

# Check application logs
sudo journalctl -u rbm-tender-app -n 20
```

### **Step 5: Post-Deployment (2 minutes)**
- [ ] Verify all features work
- [ ] Check error logs
- [ ] Monitor performance
- [ ] Update deployment log
- [ ] Notify team of successful deployment

---

## 🔄 **Rollback Procedure**

### **If Deployment Fails:**

```bash
# Stop the application
sudo systemctl stop rbm-tender-app

# Revert to previous commit
git reset --hard HEAD~1

# Restore database if needed
flask db restore backup_file.db

# Restart application
sudo systemctl start rbm-tender-app

# Verify rollback
curl http://54.253.118.23:5000/health
```

---

## 📊 **Monitoring Checklist**

### **Immediate (First 5 minutes):**
- [ ] Application responds to health check
- [ ] Website loads correctly
- [ ] No error messages in logs
- [ ] Database connections working
- [ ] All critical features functional

### **First Hour:**
- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Verify user functionality
- [ ] Monitor database performance
- [ ] Check external integrations

### **First Day:**
- [ ] Review application logs
- [ ] Check user feedback
- [ ] Monitor system resources
- [ ] Verify backup procedures
- [ ] Update documentation

---

## 🚨 **Emergency Contacts**

### **If Deployment Fails:**
- **Primary**: You (developer)
- **Backup**: [Add backup contact]
- **Business**: [Add business stakeholder]

### **If Rollback Needed:**
- **Database Issues**: Check PostgreSQL logs
- **Application Issues**: Check Gunicorn logs
- **Network Issues**: Check AWS/Cloudflare status

---

## 📝 **Deployment Log Template**

```markdown
# Deployment Log - [DATE]

**Deployment Time**: [TIME]
**Deployed By**: [NAME]
**Version**: [COMMIT HASH]

**Pre-Deployment**:
- [ ] Tests passed
- [ ] Backup created
- [ ] Team notified

**Deployment**:
- [ ] Code deployed
- [ ] Migrations run
- [ ] Application restarted
- [ ] Health check passed

**Post-Deployment**:
- [ ] Features verified
- [ ] Performance checked
- [ ] Logs reviewed
- [ ] Team notified

**Issues Encountered**: [List any problems]
**Resolution**: [How issues were resolved]
**Next Steps**: [Any follow-up actions]
```

---

## 💡 **Best Practices**

### **Before Deployment:**
- Always test in staging first
- Create database backups
- Notify team of deployment
- Have rollback plan ready

### **During Deployment:**
- Monitor logs closely
- Test critical functionality
- Keep team updated
- Document any issues

### **After Deployment:**
- Monitor for at least 1 hour
- Check user feedback
- Update documentation
- Plan next improvements

---

**🎯 Pro Tip**: Keep this runbook open during deployments and follow it step-by-step!

