#!/bin/bash

# SSL Setup Script for RBM Tender App
# This script sets up Let's Encrypt SSL certificates for HTTPS

set -e  # Exit on any error

echo "🔐 Setting up SSL certificates for RBM Tender App..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run this script as root (use sudo)"
    exit 1
fi

# Update system packages
echo "📦 Updating system packages..."
yum update -y

# Install certbot
echo "🔧 Installing Certbot..."
if ! command -v certbot &> /dev/null; then
    yum install -y epel-release
    yum install -y certbot python3-certbot-nginx
else
    echo "✅ Certbot already installed"
fi

# Stop nginx temporarily for certificate generation
echo "⏸️  Stopping nginx..."
systemctl stop nginx

# Generate SSL certificate
echo "🔐 Generating SSL certificate for rbm-intranet.com..."
certbot certonly \
    --standalone \
    --non-interactive \
    --agree-tos \
    --email admin@rbmsystems.com.au \
    -d rbm-intranet.com \
    -d www.rbm-intranet.com

# Verify certificate was created
if [ -f "/etc/letsencrypt/live/rbm-intranet.com/fullchain.pem" ]; then
    echo "✅ SSL certificate generated successfully!"
else
    echo "❌ Failed to generate SSL certificate"
    exit 1
fi

# Set proper permissions
echo "🔒 Setting certificate permissions..."
chmod 600 /etc/letsencrypt/live/rbm-intranet.com/privkey.pem
chmod 644 /etc/letsencrypt/live/rbm-intranet.com/fullchain.pem
chmod 644 /etc/letsencrypt/live/rbm-intranet.com/chain.pem

# Copy nginx configuration
echo "📝 Updating nginx configuration..."
cp /home/ec2-user/RBM-Tender-App-main/config/nginx.conf /etc/nginx/nginx.conf

# Test nginx configuration
echo "🧪 Testing nginx configuration..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx configuration is valid"
else
    echo "❌ Nginx configuration test failed"
    exit 1
fi

# Start nginx
echo "🚀 Starting nginx..."
systemctl start nginx
systemctl enable nginx

# Set up automatic certificate renewal
echo "🔄 Setting up automatic certificate renewal..."
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet --post-hook 'systemctl reload nginx'") | crontab -

echo "✅ SSL setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Update Cloudflare SSL/TLS mode to 'Full'"
echo "2. Test your site at https://rbm-intranet.com"
echo "3. Verify the SSL certificate is working"
echo ""
echo "🔗 To change Cloudflare SSL mode:"
echo "   - Go to Cloudflare Dashboard"
echo "   - SSL/TLS → Overview"
echo "   - Change from 'Flexible' to 'Full'"
