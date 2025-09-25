# CPU Credit Quick Reference - t3.medium
**Instance Type**: t3.medium  
**Issue**: CPU Credit Balance hitting 0  
**Last Updated**: 2025-01-15

## 🚨 **Immediate Actions**

### **Step 1: Check Current CPU Credit Status**
```bash
# SSH into your EC2 instance
ssh -i "your-key.pem" ec2-user@your-ec2-ip

# Check CPU credit balance (if CloudWatch agent is installed)
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUCreditBalance \
  --dimensions Name=InstanceId,Value=i-your-instance-id \
  --start-time 2025-01-15T00:00:00Z \
  --end-time 2025-01-15T23:59:59Z \
  --period 300 \
  --statistics Average
```

### **Step 2: Monitor CPU Usage in Real-Time**
```bash
# Install htop for better monitoring
sudo yum install htop -y

# Monitor CPU usage
htop

# Alternative: top command
top
```

### **Step 3: Check Application Performance**
```bash
# Check application logs
sudo journalctl -u rbm-tender-app -f

# Check database connections
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"

# Check system resources
free -h
df -h
```

---

## 📊 **t3.medium vs t2.micro Comparison**

| Metric | t2.micro | t3.medium | Improvement |
|--------|----------|-----------|-------------|
| **Baseline CPU** | 20% | 40% | 2x better |
| **CPU Credits/Hour** | 6 | 24 | 4x better |
| **CPU Credits/Day** | 144 | 576 | 4x better |
| **vCPUs** | 1 | 2 | 2x better |
| **Memory** | 1 GB | 4 GB | 4x better |

---

## 🔧 **Quick Fixes for CPU Credit Issues**

### **1. Optimize Database Queries**
```bash
# Check slow queries
sudo -u postgres psql -d rbm_tender_app -c "
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;"
```

### **2. Reduce Logging Verbosity**
```bash
# Check current log level
grep LOG_LEVEL /opt/rbm-tender-app/.env

# Temporarily reduce logging (if needed)
sudo nano /opt/rbm-tender-app/.env
# Change: LOG_LEVEL=WARNING
sudo systemctl restart rbm-tender-app
```

### **3. Optimize Application Settings**
```bash
# Check current application configuration
sudo systemctl status rbm-tender-app

# Restart application to clear memory
sudo systemctl restart rbm-tender-app
```

### **4. Monitor Background Processes**
```bash
# Check for resource-heavy processes
ps aux --sort=-%cpu | head -10

# Check system load
uptime
```

---

## 📈 **EC2 Dashboard Quick Setup**

### **Enable Detailed Monitoring (5 minutes)**
1. **AWS Console** → EC2 → Instances
2. **Select your instance** → Actions → Monitor and troubleshoot → Manage detailed monitoring
3. **Enable detailed monitoring** → Update

### **Create CPU Credit Alarm (3 minutes)**
1. **CloudWatch** → Alarms → Create alarm
2. **Metric**: AWS/EC2 → CPUCreditBalance
3. **Threshold**: Lower than 100
4. **Actions**: Create SNS topic for email notifications
5. **Create alarm**

### **View Real-Time Metrics**
1. **CloudWatch** → Metrics → EC2 → Per-Instance Metrics
2. **Select your instance**
3. **View CPUCreditBalance and CPUUtilization graphs**

---

## 🎯 **Performance Optimization for t3.medium**

### **Application-Level Optimizations**
```python
# In your Flask app, add performance monitoring
import psutil
import time

def log_system_stats():
    """Log system statistics for monitoring"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    
    if cpu_percent > 80:
        logger.warning(f"High CPU usage: {cpu_percent}%")
    
    if memory.percent > 85:
        logger.warning(f"High memory usage: {memory.percent}%")
```

### **Database Optimizations**
```bash
# Check PostgreSQL configuration
sudo -u postgres psql -c "SHOW max_connections;"
sudo -u postgres psql -c "SHOW shared_buffers;"
sudo -u postgres psql -c "SHOW work_mem;"

# Optimize for t3.medium (4GB RAM)
sudo nano /etc/postgresql/16/main/postgresql.conf
# Set: shared_buffers = 1GB
# Set: work_mem = 16MB
# Set: max_connections = 200
sudo systemctl restart postgresql
```

---

## 📱 **Mobile Monitoring Setup**

### **AWS Console Mobile App**
1. **Download** AWS Console mobile app
2. **Add your AWS account**
3. **Enable notifications** for CloudWatch alarms
4. **Quick access** to CPU credit metrics

### **Quick Dashboard Access**
- **Bookmark**: CloudWatch → Dashboards → Your dashboard
- **Mobile URL**: `https://console.aws.amazon.com/cloudwatch/home?region=ap-southeast-2#dashboards:`
- **Enable mobile notifications** for critical alarms

---

## 🚨 **Emergency Procedures**

### **If CPU Credits Hit 0**
1. **Immediate**: Check what's consuming CPU
2. **Short-term**: Restart application services
3. **Medium-term**: Optimize database queries
4. **Long-term**: Consider instance upgrade if needed

### **Emergency Commands**
```bash
# Check current CPU credit balance
aws cloudwatch get-metric-statistics --namespace AWS/EC2 --metric-name CPUCreditBalance --dimensions Name=InstanceId,Value=i-your-instance-id --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) --end-time $(date -u +%Y-%m-%dT%H:%M:%S) --period 300 --statistics Average

# Restart services to free up resources
sudo systemctl restart rbm-tender-app
sudo systemctl restart nginx

# Check system status
sudo systemctl status rbm-tender-app nginx postgresql
```

---

## 📊 **Monitoring Dashboard URLs**

### **Direct Links (replace with your instance ID)**
- **CPU Credits**: `https://console.aws.amazon.com/cloudwatch/home?region=ap-southeast-2#metricsV2:graph=~();query=AWS/EC2~27CPUCreditBalance~27InstanceId~27i-your-instance-id`
- **CPU Utilization**: `https://console.aws.amazon.com/cloudwatch/home?region=ap-southeast-2#metricsV2:graph=~();query=AWS/EC2~27CPUUtilization~27InstanceId~27i-your-instance-id`
- **All Metrics**: `https://console.aws.amazon.com/cloudwatch/home?region=ap-southeast-2#metricsV2:graph=~();query=AWS/EC2`

---

## 💡 **Key Insights for t3.medium**

1. **Much Better Performance**: 4x more CPU credits than t2.micro
2. **Higher Baseline**: 40% CPU baseline vs 20% for t2.micro
3. **More Memory**: 4GB vs 1GB allows for better caching
4. **Still Burstable**: Credits can still be depleted with heavy load

---

**🎯 Quick Action**: Enable detailed monitoring in EC2 dashboard and create a CPU credit alarm - this will give you immediate visibility into the issue!
