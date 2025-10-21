# SSL/HTTPS Setup Guide for RBM Tender App

**Date**: 2025-01-15  
**Purpose**: Enable HTTPS for secure connections between Cloudflare and your server  
**Status**: Ready for deployment

## 🎯 **Overview**

Your app is currently showing "not secure" because Cloudflare is in "Flexible" SSL/TLS mode, which means:
- **Browser ↔ Cloudflare**: HTTPS ✅ (secure)
- **Cloudflare ↔ Your Server**: HTTP ❌ (not secure)

This guide will set up HTTPS on your server so you can change Cloudflare to "Full" mode for complete end-to-end encryption.

## 🔧 **Solution Architecture**

After setup:
- **Browser ↔ Cloudflare**: HTTPS ✅ (secure)
- **Cloudflare ↔ Your Server**: HTTPS ✅ (secure)
- **Result**: Fully secure connection with green lock icon

## 📋 **Prerequisites**

- [ ] AWS EC2 instance running
- [ ] Domain `rbm-intranet.com` pointing to your server
- [ ] Nginx installed and configured
- [ ] Ports 80 and 443 open in security groups
- [ ] Root/sudo access to the server

## 🚀 **Deployment Steps**

### Step 1: Deploy SSL Configuration

1. **Upload the updated nginx configuration:**
   ```bash
   # Copy the updated nginx.conf to your server
   scp -i your-key.pem config/nginx.conf ec2-user@your-server-ip:/home/ec2-user/
   ```

2. **Upload the SSL setup script:**
   ```bash
   # Copy the SSL setup script
   scp -i your-key.pem scripts/deployment/setup-ssl.sh ec2-user@your-server-ip:/home/ec2-user/
   ```

### Step 2: Run SSL Setup Script

SSH into your server and run:

```bash
# Make script executable
chmod +x setup-ssl.sh

# Run the SSL setup script
sudo ./setup-ssl.sh
```

This script will:
- Install Certbot (Let's Encrypt client)
- Generate SSL certificates for your domain
- Update nginx configuration
- Set up automatic certificate renewal
- Start nginx with HTTPS enabled

### Step 3: Update Cloudflare SSL Mode

1. **Go to Cloudflare Dashboard**
2. **Navigate to**: SSL/TLS → Overview
3. **Change SSL/TLS encryption mode** from:
   - ❌ **Flexible** (current - HTTP between Cloudflare and server)
   - ✅ **Full** (target - HTTPS between Cloudflare and server)

### Step 4: Test HTTPS

1. **Test direct server access:**
   ```bash
   curl -I https://your-server-ip/
   ```

2. **Test through domain:**
   ```bash
   curl -I https://rbm-intranet.com/
   ```

3. **Verify in browser:**
   - Visit `https://rbm-intranet.com`
   - Check for green lock icon
   - Verify "Secure" status in address bar

## 🔍 **Troubleshooting**

### Common Issues

#### 1. Certificate Generation Fails
**Error**: `Failed to generate SSL certificate`

**Solutions**:
- Verify domain DNS points to your server
- Check port 80 is open and accessible
- Ensure no other service is using port 80

```bash
# Check if port 80 is free
sudo netstat -tlnp | grep :80

# Check DNS resolution
nslookup rbm-intranet.com
```

#### 2. Nginx Configuration Errors
**Error**: `nginx: configuration file test failed`

**Solutions**:
- Check nginx syntax: `sudo nginx -t`
- Verify SSL certificate paths exist
- Check file permissions

```bash
# Test nginx config
sudo nginx -t

# Check certificate files
ls -la /etc/letsencrypt/live/rbm-intranet.com/
```

#### 3. Cloudflare SSL Errors
**Error**: 525 or 526 errors after changing to Full mode

**Solutions**:
- Verify server SSL certificate is valid
- Check Cloudflare can reach your server on port 443
- Ensure SSL certificate includes all required domains

### Verification Commands

```bash
# Check SSL certificate details
openssl x509 -in /etc/letsencrypt/live/rbm-intranet.com/fullchain.pem -text -noout

# Test SSL connection
openssl s_client -connect rbm-intranet.com:443 -servername rbm-intranet.com

# Check nginx status
sudo systemctl status nginx

# Check certificate renewal
sudo certbot renew --dry-run
```

## 🔒 **Security Features Added**

### SSL/TLS Configuration
- **Protocols**: TLSv1.2 and TLSv1.3 only
- **Ciphers**: Strong encryption ciphers
- **HSTS**: HTTP Strict Transport Security enabled
- **OCSP Stapling**: Enabled for better performance

### Security Headers
- `Strict-Transport-Security`: Forces HTTPS for 1 year
- `X-Frame-Options`: Prevents clickjacking
- `X-Content-Type-Options`: Prevents MIME sniffing
- `X-XSS-Protection`: XSS protection
- `Referrer-Policy`: Controls referrer information

### Automatic Renewal
- Certificates auto-renew every 90 days
- Nginx automatically reloaded after renewal
- Cron job runs daily to check for renewal

## 📊 **Performance Impact**

### Expected Changes
- **Initial Connection**: Slightly slower due to SSL handshake
- **Subsequent Connections**: Faster with SSL session caching
- **Overall**: Minimal impact, improved security

### Optimizations Included
- **HTTP/2**: Enabled for better performance
- **SSL Session Caching**: Reduces handshake overhead
- **Keep-Alive**: Maintains connections for better performance

## 🔄 **Maintenance**

### Certificate Renewal
Certificates automatically renew, but you can manually check:

```bash
# Check renewal status
sudo certbot renew --dry-run

# Force renewal (if needed)
sudo certbot renew --force-renewal
```

### Monitoring
Set up monitoring for:
- Certificate expiration (90 days)
- SSL/TLS errors in logs
- HTTPS accessibility

## 📚 **Additional Resources**

- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Cloudflare SSL/TLS Modes](https://developers.cloudflare.com/ssl/origin-configuration/ssl-modes/)
- [Nginx SSL Configuration](https://nginx.org/en/docs/http/configuring_https_servers.html)
- [SSL Labs Test](https://www.ssllabs.com/ssltest/) - Test your SSL configuration

## ✅ **Success Checklist**

- [ ] SSL certificates generated successfully
- [ ] Nginx configured with HTTPS
- [ ] HTTP traffic redirects to HTTPS
- [ ] Cloudflare SSL mode changed to "Full"
- [ ] Site accessible via HTTPS
- [ ] Green lock icon shows in browser
- [ ] SSL certificate auto-renewal configured
- [ ] Security headers properly set
- [ ] Performance testing completed

## 🆘 **Support**

If you encounter issues:
1. Check the troubleshooting section above
2. Review nginx error logs: `sudo tail -f /var/log/nginx/error.log`
3. Check Cloudflare SSL/TLS settings
4. Verify server firewall and security group settings

---

*This guide ensures your RBM Tender App has complete end-to-end HTTPS encryption for maximum security.*
