# Emergency: Website Down
**Priority**: CRITICAL  
**Time to Fix**: < 15 minutes  
**Last Updated**: 2025-01-15  

---

## 🚨 **Emergency Response**

### **Step 1: Quick Assessment (2 minutes)**

```bash
# Check if website is accessible
curl -I https://rbm-intranet.com

# Check if server is responding
curl -I http://54.253.118.23:5000

# Check if Cloudflare is working
curl -I https://rbm-intranet.com --resolve rbm-intranet.com:443:173.245.48.0
```

### **Step 2: Server Health Check (3 minutes)**

```bash
# SSH into server
ssh -i RBM-App-Key-Updated.pem ec2-user@54.253.118.23

# Check if application is running
sudo systemctl status rbm-tender-app

# Check if Gunicorn is running
ps aux | grep gunicorn

# Check application logs
sudo journalctl -u rbm-tender-app -n 50
```

### **Step 3: Quick Fixes (5 minutes)**

#### **If Application is Down:**

```bash
# Restart the application
sudo systemctl restart rbm-tender-app

# Wait 30 seconds
sleep 30

# Check if it's working
curl http://localhost:5000/health
```

#### **If Server is Unreachable:**

```bash
# Check EC2 instance status
aws ec2 describe-instances --instance-ids i-093e42e2d2839132f

# If instance is stopped, start it
aws ec2 start-instances --instance-ids i-093e42e2d2839132f
```

#### **If Cloudflare is the Issue:**
1. Go to Cloudflare Dashboard
2. Check SSL/TLS mode (should be "Flexible")
3. Purge cache if needed
4. Check DNS records

### **Step 4: Verification (3 minutes)**

```bash
# Test website access
curl -I https://rbm-intranet.com

# Test direct server access
curl -I http://54.253.118.23:5000

# Test application health
curl http://54.253.118.23:5000/health
```

### **Step 5: Documentation (2 minutes)**
- Update this runbook if new steps were needed
- Document what caused the issue
- Add to troubleshooting documentation

---

## 📞 **Emergency Contacts**

### **If Still Down After 15 Minutes:**
- **AWS Support**: If server/network issues
- **Cloudflare Support**: If DNS/CDN issues
- **Domain Registrar**: If domain issues

### **Escalation Contacts:**
- **Primary Contact**: You (developer)
- **Backup Contact**: [Add backup contact]
- **Business Contact**: [Add business stakeholder]

---

## 🔧 **Common Issues & Quick Fixes**

### **Issue: 522 Error**
- **Cause**: Cloudflare can't reach server
- **Fix**: Check SSL/TLS mode, restart application

### **Issue: 500 Error**
- **Cause**: Application error
- **Fix**: Check logs, restart application

### **Issue: 404 Error**
- **Cause**: Route not found
- **Fix**: Check application routing, restart

### **Issue: Database Connection**
- **Cause**: PostgreSQL connection issues
- **Fix**: Check database service, restart if needed

---

## 📊 **Post-Incident Actions**

### **Within 1 Hour:**
- [ ] Document what happened
- [ ] Update troubleshooting documentation
- [ ] Identify root cause
- [ ] Plan prevention measures

### **Within 24 Hours:**
- [ ] Review incident response
- [ ] Update runbooks if needed
- [ ] Implement monitoring improvements
- [ ] Schedule follow-up review

---

**💡 Pro Tip**: Keep this runbook printed or easily accessible on your phone for emergencies!

