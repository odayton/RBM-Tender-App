# Cloudflare SSL Settings for HTTPS Setup

## 🎯 **Current Issue**
Your site shows "Not Secure" because Cloudflare is in "Flexible" SSL/TLS mode.

## 🔧 **Solution**
Change Cloudflare SSL/TLS mode from "Flexible" to "Full" after setting up HTTPS on your server.

## 📋 **Steps to Fix**

### 1. First: Set up HTTPS on your server
- Run the SSL setup script: `sudo ./setup-ssl.sh`
- This will generate SSL certificates and configure nginx for HTTPS

### 2. Then: Update Cloudflare Settings

1. **Login to Cloudflare Dashboard**
2. **Select your domain**: rbm-intranet.com
3. **Go to**: SSL/TLS → Overview
4. **Change Encryption mode** from:
   - ❌ **Flexible** (current setting)
   - ✅ **Full** (new setting)

### 3. Verify the change
- Wait 5-10 minutes for changes to propagate
- Visit your site: https://rbm-intranet.com
- Look for the green lock icon in your browser

## 🔍 **SSL/TLS Mode Explanations**

| Mode | Browser ↔ Cloudflare | Cloudflare ↔ Server | Use Case |
|------|---------------------|---------------------|----------|
| **Off** | HTTP | HTTP | Not recommended |
| **Flexible** | HTTPS | HTTP | Temporary (current) |
| **Full** | HTTPS | HTTPS | **Target (recommended)** |
| **Full (Strict)** | HTTPS | HTTPS + Valid Cert | Most secure |

## ✅ **Expected Result**
After changing to "Full" mode:
- ✅ Browser ↔ Cloudflare: HTTPS (secure)
- ✅ Cloudflare ↔ Server: HTTPS (secure)
- ✅ Green lock icon in browser
- ✅ "Secure" status in address bar

## 🆘 **If You Get Errors**
If you see 525/526 errors after changing to Full mode:
1. Verify SSL certificates are properly installed on your server
2. Check that nginx is running with HTTPS enabled
3. Ensure port 443 is open in your AWS security groups
4. Test direct HTTPS access to your server IP

---

*This is a quick reference. See the full SSL_HTTPS_SETUP_GUIDE.md for complete instructions.*
