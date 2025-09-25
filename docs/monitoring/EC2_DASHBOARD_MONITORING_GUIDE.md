# EC2 Dashboard Monitoring Configuration Guide
**Instance Type**: t3.medium  
**Purpose**: Configure comprehensive monitoring from AWS EC2 Dashboard  
**Last Updated**: 2025-01-15

## 🎯 **Overview**

This guide helps you configure comprehensive monitoring for your t3.medium EC2 instance directly from the AWS EC2 Dashboard. This will help you track CPU credit balance, performance metrics, and identify resource bottlenecks.

---

## 📊 **EC2 Dashboard Monitoring Setup**

### **Step 1: Enable Detailed Monitoring**

1. **Navigate to EC2 Dashboard**
   - Go to AWS Console → EC2 → Instances
   - Select your t3.medium instance

2. **Enable Detailed Monitoring**
   - Right-click on your instance → "Monitor and troubleshoot" → "Manage detailed monitoring"
   - OR: Go to Actions → Monitor and troubleshoot → Manage detailed monitoring
   - **Enable detailed monitoring** (costs ~$2/month but provides 1-minute metrics)
   - Click "Update"

### **Step 2: Configure CloudWatch Alarms**

#### **CPU Credit Balance Alarm (Critical)**
1. **Go to CloudWatch** → Alarms → Create alarm
2. **Metric**: EC2 → Per-Instance Metrics → `CPUCreditBalance`
3. **Instance**: Select your t3.medium instance
4. **Conditions**:
   - **Threshold type**: Static
   - **Alarm condition**: Lower than 50
   - **Datapoints to alarm**: 1 out of 1
5. **Actions**: 
   - Create SNS topic for email notifications
   - Add your email address
6. **Name**: `RBM-App-Low-CPU-Credits`
7. **Click "Create alarm"**

#### **CPU Utilization Alarm**
1. **Create new alarm** → CloudWatch → Alarms → Create alarm
2. **Metric**: EC2 → Per-Instance Metrics → `CPUUtilization`
3. **Conditions**:
   - **Threshold type**: Static
   - **Alarm condition**: Greater than 80%
   - **Datapoints to alarm**: 2 out of 3
4. **Actions**: Same SNS topic as above
5. **Name**: `RBM-App-High-CPU-Usage`
6. **Click "Create alarm"**

#### **Memory Utilization Alarm**
1. **Create new alarm** → Custom metrics → `MemoryUtilization`
2. **Note**: You'll need to install CloudWatch agent for memory metrics
3. **Conditions**:
   - **Threshold type**: Static
   - **Alarm condition**: Greater than 85%
4. **Name**: `RBM-App-High-Memory-Usage`

#### **Disk Space Alarm**
1. **Create new alarm** → Custom metrics → `DiskSpaceUtilization`
2. **Conditions**:
   - **Threshold type**: Static
   - **Alarm condition**: Greater than 80%
4. **Name**: `RBM-App-Low-Disk-Space`

---

## 📈 **Key Metrics to Monitor**

### **t3.medium Specific Metrics**

#### **CPU Credits**
- **CPUCreditBalance**: Remaining CPU credits
- **CPUCreditUsage**: Credits consumed per minute
- **Baseline Performance**: 40% CPU baseline (vs 20% for t2.micro)
- **Burst Credits**: Earns 24 credits/hour (vs 6 for t2.micro)

#### **Performance Metrics**
- **CPUUtilization**: Current CPU usage percentage
- **NetworkIn/NetworkOut**: Network traffic
- **DiskReadOps/DiskWriteOps**: Disk I/O operations
- **StatusCheckFailed**: System and instance health checks

### **Application-Specific Metrics**
- **Database Connections**: PostgreSQL connection pool usage
- **Response Times**: Application response times
- **Error Rates**: 4xx and 5xx HTTP errors
- **Memory Usage**: Application memory consumption

---

## 🔧 **CloudWatch Agent Installation**

### **Step 1: Install CloudWatch Agent**
```bash
# SSH into your EC2 instance
ssh -i "your-key.pem" ec2-user@your-ec2-ip

# Download and install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
sudo rpm -U ./amazon-cloudwatch-agent.rpm
```

### **Step 2: Configure CloudWatch Agent**
```bash
# Create configuration file
sudo nano /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json
```

**Configuration for t3.medium:**
```json
{
    "metrics": {
        "namespace": "RBM-Tender-App",
        "metrics_collected": {
            "cpu": {
                "measurement": [
                    "cpu_usage_idle",
                    "cpu_usage_iowait",
                    "cpu_usage_user",
                    "cpu_usage_system"
                ],
                "metrics_collection_interval": 60,
                "totalcpu": false
            },
            "disk": {
                "measurement": [
                    "used_percent"
                ],
                "metrics_collection_interval": 60,
                "resources": [
                    "*"
                ]
            },
            "diskio": {
                "measurement": [
                    "io_time",
                    "read_bytes",
                    "write_bytes",
                    "reads",
                    "writes"
                ],
                "metrics_collection_interval": 60,
                "resources": [
                    "*"
                ]
            },
            "mem": {
                "measurement": [
                    "mem_used_percent"
                ],
                "metrics_collection_interval": 60
            },
            "netstat": {
                "measurement": [
                    "tcp_established",
                    "tcp_time_wait"
                ],
                "metrics_collection_interval": 60
            },
            "swap": {
                "measurement": [
                    "swap_used_percent"
                ],
                "metrics_collection_interval": 60
            }
        }
    },
    "logs": {
        "logs_collected": {
            "files": {
                "collect_list": [
                    {
                        "file_path": "/var/log/nginx/access.log",
                        "log_group_name": "RBM-App-Nginx-Access",
                        "log_stream_name": "{instance_id}-nginx-access"
                    },
                    {
                        "file_path": "/var/log/nginx/error.log",
                        "log_group_name": "RBM-App-Nginx-Error",
                        "log_stream_name": "{instance_id}-nginx-error"
                    },
                    {
                        "file_path": "/var/log/postgresql/postgresql-*.log",
                        "log_group_name": "RBM-App-PostgreSQL",
                        "log_stream_name": "{instance_id}-postgresql"
                    }
                ]
            }
        }
    }
}
```

### **Step 3: Start CloudWatch Agent**
```bash
# Start the agent
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config \
    -m ec2 \
    -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json \
    -s

# Check status
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -m ec2 -s
```

---

## 📊 **Dashboard Configuration**

### **Step 1: Create Custom Dashboard**
1. **Go to CloudWatch** → Dashboards → Create dashboard
2. **Dashboard name**: `RBM-Tender-App-Monitoring`

### **Step 2: Add Widgets**

#### **CPU Credits Widget**
1. **Add widget** → Line chart
2. **Metrics**: 
   - `AWS/EC2` → `CPUCreditBalance` (your instance)
   - `AWS/EC2` → `CPUCreditUsage` (your instance)
3. **Title**: "CPU Credits (t3.medium)"
4. **Y-axis**: 0-1000 (for balance), 0-50 (for usage)

#### **CPU Utilization Widget**
1. **Add widget** → Line chart
2. **Metrics**: `AWS/EC2` → `CPUUtilization` (your instance)
3. **Title**: "CPU Utilization %"
4. **Y-axis**: 0-100

#### **Memory Usage Widget**
1. **Add widget** → Line chart
2. **Metrics**: `RBM-Tender-App` → `mem_used_percent` (your instance)
3. **Title**: "Memory Usage %"
4. **Y-axis**: 0-100

#### **Disk Usage Widget**
1. **Add widget** → Line chart
2. **Metrics**: `RBM-Tender-App` → `disk_used_percent` (your instance)
3. **Title**: "Disk Usage %"
4. **Y-axis**: 0-100

#### **Network Traffic Widget**
1. **Add widget** → Line chart
2. **Metrics**: 
   - `AWS/EC2` → `NetworkIn` (your instance)
   - `AWS/EC2` → `NetworkOut` (your instance)
3. **Title**: "Network Traffic"

---

## 🚨 **Alert Configuration**

### **Email Notifications Setup**
1. **Go to SNS** → Topics → Create topic
2. **Topic name**: `RBM-App-Alerts`
3. **Create subscription**:
   - **Protocol**: Email
   - **Endpoint**: Your email address
   - **Confirm subscription** (check your email)

### **Critical Alerts to Configure**
1. **Low CPU Credits** (< 50 credits)
2. **High CPU Usage** (> 80% for 5 minutes)
3. **High Memory Usage** (> 85%)
4. **Low Disk Space** (< 20% free)
5. **Application Health Check Failed**
6. **Database Connection Issues**

---

## 📱 **Mobile App Configuration**

### **AWS Console Mobile App**
1. **Download**: AWS Console mobile app
2. **Configure**: Add your AWS account
3. **Enable notifications** for CloudWatch alarms
4. **Set up**: Quick access to your dashboard

---

## 🔍 **Troubleshooting CPU Credit Issues**

### **Identify High CPU Usage Patterns**
1. **Check CloudWatch Metrics** → CPU Utilization over time
2. **Look for spikes** during:
   - Application startup
   - Database migrations
   - Heavy user activity
   - Background tasks

### **Optimize for t3.medium**
1. **Baseline Performance**: 40% CPU (vs 20% for t2.micro)
2. **Credit Earning**: 24 credits/hour (vs 6 for t2.micro)
3. **Better Burst Capacity**: Can handle more sustained load

### **Performance Optimizations**
1. **Database Query Optimization**
2. **Application Caching**
3. **Background Task Scheduling**
4. **Resource Monitoring**

---

## 📋 **Monitoring Checklist**

### **Daily Checks**
- [ ] CPU Credit Balance > 100
- [ ] CPU Utilization < 60%
- [ ] Memory Usage < 70%
- [ ] Disk Space > 30%
- [ ] Application Health Checks Passing

### **Weekly Reviews**
- [ ] Review CloudWatch dashboards
- [ ] Check alarm history
- [ ] Analyze performance trends
- [ ] Review cost implications
- [ ] Update monitoring thresholds

### **Monthly Optimization**
- [ ] Review instance sizing
- [ ] Optimize application performance
- [ ] Update monitoring configuration
- [ ] Review alerting rules

---

## 💰 **Cost Considerations**

### **CloudWatch Costs (t3.medium)**
- **Basic Monitoring**: Free (5-minute metrics)
- **Detailed Monitoring**: ~$2/month (1-minute metrics)
- **Custom Metrics**: $0.30 per metric per month
- **Logs**: $0.50 per GB ingested

### **Recommended Configuration**
- **Enable detailed monitoring** for critical metrics
- **Use basic monitoring** for less critical metrics
- **Set up log retention** (7-30 days)
- **Monitor costs** monthly

---

## 🎯 **Next Steps**

1. **Enable detailed monitoring** on your t3.medium instance
2. **Configure CloudWatch alarms** for CPU credits
3. **Install CloudWatch agent** for custom metrics
4. **Create monitoring dashboard**
5. **Set up email notifications**
6. **Test alerting system**

---

**💡 Pro Tip**: With t3.medium, you have much better CPU credit performance than t2.micro, but monitoring will help you optimize usage and catch issues early!
