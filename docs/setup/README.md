# RBM Tender App - Setup Guide

## 🚀 Quick Start

The fastest way to get your RBM Tender App deployed:

```bash
# Run the quick start script
./scripts/setup-quick-start.sh
```

This will:
- Generate SSH keys for GitHub Actions
- Create a random secret key
- Check your GitHub repository
- Create a deployment package
- Show you step-by-step instructions

## 📋 Manual Setup

If you prefer to set up manually, follow these guides:

### 1. Server Setup
- [AWS EC2 Setup Guide](AWS_EC2_SETUP.md)
- [Server Configuration](SERVER_CONFIGURATION.md)

### 2. GitHub Configuration
- [GitHub Secrets Setup](GITHUB_SECRETS_SETUP.md)
- [CI/CD Pipeline Configuration](CICD_CONFIGURATION.md)

### 3. Deployment
- [Deployment Checklist](DEPLOYMENT_CHECKLIST.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)

## 🔧 Prerequisites

Before you start, make sure you have:

- [ ] AWS EC2 instance (Ubuntu 22.04 LTS)
- [ ] Domain name (optional, can use IP)
- [ ] GitHub repository
- [ ] SSH access to your server

## 📚 Documentation

- [Complete Setup Guide](DEPLOYMENT_CHECKLIST.md)
- [GitHub Secrets Configuration](GITHUB_SECRETS_SETUP.md)
- [Server Setup Script](../scripts/deployment/setup-aws-ec2.sh)
- [Quick Start Script](../scripts/setup-quick-start.sh)

## 🆘 Need Help?

1. **Check the troubleshooting guide** in `docs/setup/TROUBLESHOOTING.md`
2. **Review the deployment checklist** in `docs/setup/DEPLOYMENT_CHECKLIST.md`
3. **Check server logs** using the monitoring commands
4. **Verify GitHub Actions** in your repository's Actions tab

## 🎯 What You'll Get

After successful setup, you'll have:

- ✅ **Automated CI/CD pipeline** with GitHub Actions
- ✅ **Production-ready server** with Nginx, PostgreSQL, Redis
- ✅ **SSL certificate** (if using custom domain)
- ✅ **Monitoring dashboard** with real-time metrics
- ✅ **Health checks** and automated rollback
- ✅ **Security features** (firewall, rate limiting, etc.)

## 🚀 Ready to Deploy?

1. Run `./scripts/setup-quick-start.sh`
2. Follow the instructions
3. Push to `main` branch
4. Monitor deployment in GitHub Actions
5. Access your app at `https://your-domain.com`

---

**Happy Deploying!** 🎉



