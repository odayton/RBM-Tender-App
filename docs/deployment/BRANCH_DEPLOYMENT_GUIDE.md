# Branch-Based Deployment Guide
## Safe Production Testing Strategy

### 🎯 **Overview**
This guide explains how to safely test changes using our Git Flow branching strategy with a persistent `develop` branch for integration testing before production deployment.

---

## 🌿 **Branch Strategy (Git Flow)**

### **Branch Structure**
```
main (production) ← Only gets code from develop
  ↑
develop (integration) ← Always exists, gets code from feature branches
  ↑
feature/* (development) ← Your work branches
```

### **Supported Branch Patterns**
- `main` - Production branch (deploys to production)
- `develop` - Integration branch (full testing, no deployment)
- `feature/*` - Feature branches (e.g., `feature/new-dashboard`)
- `test/*` - Test branches (e.g., `test/payment-integration`)

### **Deployment Flow**
```
feature/branch → develop (full testing) → main (production deployment)
```

---

## 🚀 **Step-by-Step Process**

### **Step 1: Start from Develop Branch**
```bash
# Always start from the develop branch
git checkout develop
git pull origin develop  # Get latest changes

# Create feature branch from develop
git checkout -b feature/your-feature-name
```

### **Step 2: Make Your Changes**
```bash
# Make your code changes
# Edit files, add features, fix bugs, etc.

# Commit your changes
git add .
git commit -m "Add new payment integration for testing"
```

### **Step 3: Test on Develop Branch**
```bash
# Push feature branch
git push origin feature/your-feature-name

# Merge to develop (triggers full testing, NO deployment)
git checkout develop
git merge feature/your-feature-name
git push origin develop

# Monitor testing in GitHub Actions
# Go to: GitHub Repository → Actions tab → Watch testing progress
```

### **Step 4: Deploy to Production**
```bash
# When develop tests pass, merge to main (deploys to production)
git checkout main
git merge develop
git push origin main

# Monitor deployment in GitHub Actions
# Go to: GitHub Repository → Actions tab → Watch deployment progress
```

### **Step 4: Test in Production**
```bash
# SSH into your production server
ssh -i "your-key.pem" ubuntu@your-server-ip

# Monitor application logs
sudo journalctl -u rbm-tender-app -f

# Test your changes thoroughly:
# - Login/logout functionality
# - New features
# - Database operations
# - File uploads
# - All critical business functions
```

### **Step 5: Decision Point**

#### **✅ If Testing Passes:**
```bash
# Merge to main branch
git checkout main
git pull origin main
git merge feature/your-feature-name
git push origin main

# Clean up test branch
git branch -d feature/your-feature-name
git push origin --delete feature/your-feature-name
```

#### **❌ If Testing Fails:**
```bash
# Switch back to main branch
git checkout main

# Deploy main branch to production (rollback)
git push origin main

# Delete the failed branch
git branch -D feature/your-feature-name
git push origin --delete feature/your-feature-name
```

---

## 🔧 **GitHub Actions Configuration**

### **Automatic Deployment Triggers**
The CI/CD pipeline automatically deploys when you push to:
- `main` branch (production)
- `feature/*` branches (testing)
- `test/*` branches (testing)

### **Deployment Process**
1. **Quality Checks** - Security scanning, linting
2. **Testing** - Unit, integration, security tests
3. **Build** - Create deployment package
4. **Deploy** - Deploy to production server
5. **Verification** - Health checks and smoke tests

### **Branch Information Display**
During deployment, you'll see:
```
🚀 Deploying branch: feature/your-feature-name
📋 Full ref: refs/heads/feature/your-feature-name
```

---

## 🛡️ **Safety Features**

### **Automatic Backups**
- Every deployment creates a backup of the current version
- Backups are stored in `/opt/rbm-tender-app.backup.TIMESTAMP`
- Automatic rollback capability if deployment fails

### **Health Checks**
- Application health endpoint verification
- Database connectivity checks
- Service status monitoring
- Automatic rollback on health check failures

### **Zero-Downtime Deployment**
- Service is stopped only during file replacement
- Quick restart process minimizes downtime
- Health checks ensure service is running before completion

---

## 📋 **Best Practices**

### **Branch Naming Convention**
```bash
# Feature branches
feature/dashboard-redesign
feature/payment-integration
feature/user-management

# Test branches
test/database-optimization
test/new-authentication
test/performance-improvements
```

### **Testing Checklist**
Before merging to main, verify:
- [ ] **Authentication** - Login/logout works correctly
- [ ] **Database Operations** - CRUD operations function properly
- [ ] **File Uploads** - File handling works as expected
- [ ] **API Endpoints** - All endpoints respond correctly
- [ ] **Monitoring** - Health checks and monitoring work
- [ ] **Performance** - No significant performance degradation
- [ ] **Error Handling** - Error pages and messages work correctly

### **Rollback Strategy**
If a deployment fails or causes issues:
1. **Immediate**: Push to main branch to trigger rollback
2. **Manual**: SSH into server and restore from backup
3. **Emergency**: Use rollback script if available

---

## 🚨 **Emergency Procedures**

### **Quick Rollback**
```bash
# If something goes wrong, immediately push main branch
git checkout main
git push origin main
# This will deploy the last known good version
```

### **Manual Rollback**
```bash
# SSH into production server
ssh -i "your-key.pem" ubuntu@your-server-ip

# Stop the service
sudo systemctl stop rbm-tender-app

# Restore from backup
sudo rm -rf /opt/rbm-tender-app
sudo mv /opt/rbm-tender-app.backup.TIMESTAMP /opt/rbm-tender-app

# Restart service
sudo systemctl start rbm-tender-app
sudo systemctl status rbm-tender-app
```

### **Check Service Status**
```bash
# Check if service is running
sudo systemctl status rbm-tender-app

# Check application logs
sudo journalctl -u rbm-tender-app --no-pager -l -n 50

# Check health endpoint
curl http://localhost/health
```

---

## 📊 **Monitoring and Verification**

### **Deployment Verification**
```bash
# Check deployment status
curl http://your-domain.com/health

# Monitor logs in real-time
sudo journalctl -u rbm-tender-app -f

# Check service status
sudo systemctl status rbm-tender-app
```

### **Performance Monitoring**
- Monitor response times
- Check database connection usage
- Verify memory and CPU usage
- Test critical user workflows

---

## 💡 **Tips and Tricks**

### **Testing Strategy**
1. **Start Small** - Test minor changes first
2. **Incremental Testing** - Add features gradually
3. **User Workflow Testing** - Test complete user journeys
4. **Edge Case Testing** - Test error conditions and edge cases

### **Communication**
- **Notify Team** - Let team know when testing in production
- **Document Changes** - Keep clear records of what's being tested
- **Monitor Closely** - Watch logs and metrics during testing

### **Branch Management**
- **Clean Up** - Delete test branches after merging
- **Descriptive Names** - Use clear, descriptive branch names
- **One Feature Per Branch** - Keep branches focused on single features

---

## 🔗 **Related Documentation**
- [Production Deployment Guide](PRODUCTION_DEPLOYMENT_GUIDE.md)
- [Troubleshooting Guide](troubleshooting/README.md)
- [GitHub Actions Workflow](.github/workflows/ci-cd.yml)

---

**💡 Pro Tip**: Always test in production with a rollback plan ready. The branch deployment strategy gives you the safety net to experiment while maintaining production stability!

