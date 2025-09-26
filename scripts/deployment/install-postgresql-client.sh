#!/bin/bash

# PostgreSQL Client Installation Script
# This script installs PostgreSQL client tools for database backups

set -e  # Exit on any error

echo "🐘 Installing PostgreSQL client tools..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run this script as root (use sudo)"
    exit 1
fi

# Detect OS
if [ -f /etc/redhat-release ]; then
    # RHEL/CentOS/Amazon Linux
    OS="rhel"
    echo "📦 Detected RHEL/CentOS/Amazon Linux"
elif [ -f /etc/debian_version ]; then
    # Debian/Ubuntu
    OS="debian"
    echo "📦 Detected Debian/Ubuntu"
else
    echo "❌ Unsupported operating system"
    exit 1
fi

# Install PostgreSQL client based on OS
if [ "$OS" = "rhel" ]; then
    # Amazon Linux 2 / CentOS / RHEL
    echo "📥 Installing PostgreSQL client for RHEL/CentOS..."
    
    # Update package list
    yum update -y
    
    # Install PostgreSQL client
    yum install -y postgresql15
    
    # Verify installation
    if command -v pg_dump &> /dev/null; then
        echo "✅ PostgreSQL client installed successfully"
        pg_dump --version
    else
        echo "❌ PostgreSQL client installation failed"
        exit 1
    fi
    
elif [ "$OS" = "debian" ]; then
    # Ubuntu / Debian
    echo "📥 Installing PostgreSQL client for Debian/Ubuntu..."
    
    # Update package list
    apt-get update
    
    # Install PostgreSQL client
    apt-get install -y postgresql-client-15
    
    # Verify installation
    if command -v pg_dump &> /dev/null; then
        echo "✅ PostgreSQL client installed successfully"
        pg_dump --version
    else
        echo "❌ PostgreSQL client installation failed"
        exit 1
    fi
fi

echo ""
echo "🎉 PostgreSQL client tools installed successfully!"
echo ""
echo "📋 Available tools:"
echo "   - pg_dump: Create database backups"
echo "   - pg_restore: Restore database backups"
echo "   - psql: PostgreSQL interactive terminal"
echo ""
echo "🔧 Test the installation:"
echo "   pg_dump --version"
echo ""
echo "💡 The backup system will now be able to create PostgreSQL backups."
