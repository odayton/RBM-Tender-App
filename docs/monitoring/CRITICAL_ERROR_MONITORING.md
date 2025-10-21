# Critical Error Monitoring Guide

## 📋 Overview

Your application now has a dedicated **critical errors log** that captures production issues with full context, making it easy to identify and fix bugs that weren't caught in testing.

---

## 📁 Log Files Structure

### Log Files Location
```
instance/logs/
├── app.log          # All application events (INFO, WARNING, ERROR, CRITICAL)
├── errors.log       # ERROR and CRITICAL level only
├── critical.log     # CRITICAL level ONLY (unhandled exceptions)
└── requests.log     # HTTP request logs
```

---

## 🎯 Critical Error Log (`critical.log`)

### What Gets Logged Here

**ONLY critical unhandled exceptions:**
- Pages that crash unexpectedly
- Database connection failures
- Unhandled Python exceptions
- System-level errors
- Production bugs not caught in testing ⭐

### What's Captured

Every critical error includes:
```
✅ Full stack trace
✅ URL that failed
✅ HTTP method (GET/POST)
✅ Route/endpoint name
✅ User who encountered it (email)
✅ User's IP address
✅ Timestamp
✅ User agent (browser info)
✅ Form data (excluding passwords)
✅ Full exception details
```

### Example Critical Log Entry

```
2025-10-14 10:30:45,123 [CRITICAL] app core_errors:173: UNHANDLED EXCEPTION: AttributeError: 'NoneType' object has no attribute 'name' | URL: http://rbm-intranet.com/deals/view/123 | Method: GET | Endpoint: deals.view_deal | User: john@rbm.com
Traceback (most recent call last):
  File "/opt/rbm-tender-app/app/features/deals/routes.py", line 45, in view_deal
    deal_name = deal.customer.name
AttributeError: 'NoneType' object has no attribute 'name'

Extra context:
{
  "url": "http://rbm-intranet.com/deals/view/123",
  "method": "GET",
  "endpoint": "deals.view_deal",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
  "ip_address": "192.168.1.100",
  "timestamp": "2025-10-14T10:30:45.123456",
  "user_id": 5,
  "user_email": "john@rbm.com"
}
```

---

## 📊 Log Rotation Settings

### `critical.log`
- **Max file size:** 2 MB per file
- **Backup count:** 5 files
- **Total max space:** 12 MB (2MB × 6 files)
- **Retention:** Automatically deleted when 6th file is full

### Rotation Example
```
critical.log     ← Current (0-2 MB)
critical.log.1   ← Backup 1
critical.log.2   ← Backup 2
critical.log.3   ← Backup 3
critical.log.4   ← Backup 4
critical.log.5   ← Oldest (deleted on next rotation)
```

---

## 🔍 How to Monitor Critical Errors

### 1. Check for Recent Critical Errors

**PowerShell (Windows):**
```powershell
# Check if critical.log exists and show recent errors
Get-Content instance\logs\critical.log -Tail 50
```

**Linux/Mac:**
```bash
# Show last 50 lines
tail -n 50 instance/logs/critical.log

# Watch for new errors in real-time
tail -f instance/logs/critical.log
```

### 2. Count Critical Errors Today

**PowerShell:**
```powershell
# Count lines with today's date
$today = Get-Date -Format "yyyy-MM-dd"
(Get-Content instance\logs\critical.log | Select-String $today).Count
```

**Linux:**
```bash
# Count critical errors today
grep "$(date +%Y-%m-%d)" instance/logs/critical.log | wc -l
```

### 3. Search for Specific Errors

**PowerShell:**
```powershell
# Find AttributeError occurrences
Get-Content instance\logs\critical.log | Select-String "AttributeError"

# Find errors on specific page
Get-Content instance\logs\critical.log | Select-String "/deals/view"
```

**Linux:**
```bash
# Find specific error types
grep "AttributeError" instance/logs/critical.log

# Find errors by user
grep "user_email.*john@rbm.com" instance/logs/critical.log
```

---

## 🚨 Production Monitoring Workflow

### Daily Check (Morning Routine)

```bash
# On production server
cd /opt/rbm-tender-app

# Check if any critical errors occurred
if [ -f instance/logs/critical.log ]; then
    echo "Critical errors in last 24 hours:"
    grep "$(date +%Y-%m-%d)" instance/logs/critical.log | wc -l
    
    # Show recent errors
    tail -n 20 instance/logs/critical.log
fi
```

### After Deployment

```bash
# Watch for critical errors in real-time
tail -f instance/logs/critical.log

# In another terminal, test the application
# Any crashes will appear immediately
```

### Weekly Review

```bash
# Count critical errors by day
for i in {0..6}; do
    date=$(date -d "$i days ago" +%Y-%m-%d)
    count=$(grep "$date" instance/logs/critical.log 2>/dev/null | wc -l)
    echo "$date: $count critical errors"
done
```

---

## 📧 Alert Integration (Optional)

### Option 1: Simple Email Alert Script

Create `scripts/monitoring/check_critical_errors.sh`:
```bash
#!/bin/bash
# Check for new critical errors and send email

CRITICAL_LOG="/opt/rbm-tender-app/instance/logs/critical.log"
LAST_CHECK="/tmp/last_critical_check"

if [ -f "$CRITICAL_LOG" ]; then
    # Get new errors since last check
    if [ -f "$LAST_CHECK" ]; then
        NEW_ERRORS=$(comm -13 "$LAST_CHECK" "$CRITICAL_LOG")
    else
        NEW_ERRORS=$(cat "$CRITICAL_LOG")
    fi
    
    if [ ! -z "$NEW_ERRORS" ]; then
        # Send email (requires mail/sendmail configured)
        echo "$NEW_ERRORS" | mail -s "Critical Errors Detected" your@email.com
    fi
    
    # Save current state
    cp "$CRITICAL_LOG" "$LAST_CHECK"
fi
```

**Add to cron:**
```bash
# Check every 15 minutes
*/15 * * * * /path/to/check_critical_errors.sh
```

### Option 2: Slack/Discord Webhook

Create `scripts/monitoring/critical_to_slack.py`:
```python
import requests
import os
from datetime import datetime, timedelta

CRITICAL_LOG = "instance/logs/critical.log"
SLACK_WEBHOOK = os.environ.get('SLACK_WEBHOOK_URL')

# Get errors from last 15 minutes
recent_errors = []
cutoff_time = datetime.now() - timedelta(minutes=15)

with open(CRITICAL_LOG, 'r') as f:
    for line in f:
        if cutoff_time.strftime('%Y-%m-%d %H:%M') in line:
            recent_errors.append(line)

if recent_errors and SLACK_WEBHOOK:
    message = {
        "text": f"🚨 Critical Errors Detected ({len(recent_errors)})",
        "attachments": [{
            "color": "danger",
            "text": "\n".join(recent_errors[:5])  # First 5 errors
        }]
    }
    requests.post(SLACK_WEBHOOK, json=message)
```

---

## 🎯 What You Can Do Now

### Immediate Actions

1. **Test the new critical log:**
   ```bash
   # Start your app
   python manage.py dev
   
   # Trigger a test error (create a route that fails)
   # Check instance/logs/critical.log
   ```

2. **Set up monitoring routine:**
   - Check `critical.log` daily
   - Review after deployments
   - Watch in real-time during testing

3. **Create alerts (optional):**
   - Email alerts for new critical errors
   - Slack/Discord notifications
   - Automated monitoring

---

## 📋 Common Critical Errors to Watch For

### 1. Database Errors
```
CRITICAL: Database connection lost
CRITICAL: PostgreSQL max connections exceeded
```
**Fix:** Check database status, increase connection pool

### 2. Missing Data Errors
```
CRITICAL: AttributeError: 'NoneType' object has no attribute 'name'
```
**Fix:** Add null checks, improve data validation

### 3. Configuration Errors
```
CRITICAL: SECRET_KEY not set
CRITICAL: Missing required environment variable
```
**Fix:** Check .env file on production server

### 4. Import Errors
```
CRITICAL: ModuleNotFoundError: No module named 'xyz'
```
**Fix:** Check requirements.txt, reinstall dependencies

---

## 🛠️ Debugging with Critical Logs

### Step 1: Identify the Error
```bash
# Open critical.log
cat instance/logs/critical.log
```

### Step 2: Extract Context
Look for:
- **URL** - Which page failed?
- **User** - Who encountered it?
- **Timestamp** - When did it happen?
- **Stack trace** - Where in the code?

### Step 3: Reproduce Locally
```bash
# Try to access the same URL
# Use the same data/conditions
# Add debug logging
```

### Step 4: Fix and Test
```bash
# Fix the code
# Test locally
# Create migration if needed
# Deploy to production
```

### Step 5: Verify Fix
```bash
# Monitor critical.log after deployment
# Ensure error doesn't reoccur
```

---

## 📊 Log File Comparison

| Log File | Level | What's Logged | Rotation | Use Case |
|----------|-------|---------------|----------|----------|
| **app.log** | INFO+ | All app events | 1MB, 3 backups | General monitoring |
| **errors.log** | ERROR+ | Errors & critical | 1MB, 3 backups | Error review |
| **critical.log** | CRITICAL only | Unhandled exceptions | 2MB, 5 backups | **Production bug hunting** ⭐ |
| **requests.log** | INFO | HTTP requests | Daily, 7 days | Performance tracking |

---

## 🎯 Why This is Powerful

### Before (without critical.log)
```
❌ Errors mixed with other logs
❌ Hard to find production issues
❌ Limited context captured
❌ Must search through all logs
```

### After (with critical.log)
```
✅ Critical errors isolated
✅ Full context captured (user, URL, form data)
✅ Stack traces included
✅ Easy to review production issues
✅ Know exactly who hit the bug
✅ Can reproduce with exact conditions
```

---

## 💡 Pro Tips

### 1. Check After Every Deployment
```bash
# SSH to production
ssh your-server
cd /opt/rbm-tender-app

# Check for new critical errors
tail -n 50 instance/logs/critical.log
```

### 2. Set Up Log Monitoring Dashboard
Add to your monitoring dashboard to show:
- Critical error count (last 24 hours)
- Last critical error timestamp
- Alert if > 0 critical errors

### 3. Regular Review
- **Daily:** Quick check for any critical errors
- **Weekly:** Review patterns and trends
- **Monthly:** Analyze if certain errors repeat

### 4. Proactive Monitoring
```bash
# Create alias for quick checks
alias check-critical='tail -n 50 /opt/rbm-tender-app/instance/logs/critical.log'
```

---

## ✅ Summary

**You now have:**
- ✅ Dedicated `critical.log` file for production bugs
- ✅ Full context captured (URL, user, form data, stack trace)
- ✅ Automatic rotation (2MB × 6 files = 12MB max)
- ✅ Password filtering (won't log sensitive data)
- ✅ Easy to monitor and review

**When a user hits a bug in production:**
1. Exception is caught automatically
2. Full details saved to `critical.log`
3. You see exactly what happened
4. You can reproduce and fix it
5. User gets a generic error message (secure)

**This is exactly what you need to catch production issues!** 🎯

---

**Next time you deploy, any unhandled exceptions will be captured in `instance/logs/critical.log` with full context!**

