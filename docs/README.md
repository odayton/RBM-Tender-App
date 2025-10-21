# RBM Tender App - Documentation

Welcome to the RBM Tender App documentation! This directory contains comprehensive documentation organized by topic.

---

## 📚 Documentation Structure

### 🏠 Main Documentation
- **[RBM_TENDER_APP_DOCUMENTATION.md](RBM_TENDER_APP_DOCUMENTATION.md)** - Complete application documentation and technical reference

---

## 📂 Documentation Categories

### 💾 [Database](database/)
Database management, migrations, and schema changes
- [Database Migration Workflow](database/DATABASE_MIGRATION_WORKFLOW.md) - Complete migration guide with rules and best practices
- [Migration Checklist](database/MIGRATION_CHECKLIST.md) - Quick reference for daily migration tasks
- [Migration Workflow Diagram](database/MIGRATION_WORKFLOW_DIAGRAM.md) - Visual flowcharts and decision trees

### 🚀 [Deployment](deployment/)
Deployment guides, CI/CD pipelines, and production processes
- [Production Deployment Guide](deployment/PRODUCTION_DEPLOYMENT_GUIDE.md) - Complete production deployment procedures
- [GitHub Actions Deployment Summary](deployment/GITHUB_ACTIONS_DEPLOYMENT_SUMMARY.md) - CI/CD pipeline documentation
- [Branch Deployment Guide](deployment/BRANCH_DEPLOYMENT_GUIDE.md) - Git workflow and branch management

### 🔧 [Infrastructure](infrastructure/)
Server infrastructure, SSL, DNS, and networking
- [SSL/HTTPS Setup Guide](infrastructure/SSL_HTTPS_SETUP_GUIDE.md) - SSL certificate configuration
- [Cloudflare SSL Settings](infrastructure/CLOUDFLARE_SSL_SETTINGS.md) - Cloudflare configuration guide

### 💾 [Backup](backup/)
Backup systems and data protection
- [Smart Backup System](backup/SMART_BACKUP_SYSTEM.md) - Automated backup system documentation
- [Backup System Fix](backup/BACKUP_SYSTEM_FIX.md) - Backup troubleshooting and improvements

### 🧪 [Testing](testing/)
Testing frameworks, strategies, and guidelines
- [Enhanced Testing System](testing/ENHANCED_TESTING_SYSTEM.md) - Comprehensive testing documentation

### 📋 [Planning](planning/)
Project plans, roadmaps, and feature integration documents
- [Comprehensive Upgrade Plan](planning/COMPREHENSIVE_UPGRADE_PLAN.md) - Complete modernization roadmap
- [Pump Database Integration Plan](planning/PUMP_DATABASE_INTEGRATION_PLAN.md) - Pump feature integration plan

### 🎨 [Frontend](frontend/)
Frontend development guides and styling
- [Tailwind CSS Guide](frontend/TAILWIND_CSS_GUIDE.md) - Tailwind CSS implementation and usage

### 🔒 [Security](security/)
Security features, fixes, and best practices
- [Security Features](security/SECURITY_FEATURES.md) - Application security features
- [Security Fixes Summary](security/SECURITY_FIXES_SUMMARY.md) - Security updates and patches

### 📊 [Monitoring](monitoring/)
Application and infrastructure monitoring
- [Critical Error Monitoring](monitoring/CRITICAL_ERROR_MONITORING.md) - Production bug tracking and alerts
- [EC2 Dashboard Monitoring Guide](monitoring/EC2_DASHBOARD_MONITORING_GUIDE.md) - AWS monitoring setup
- [CPU Credit Quick Reference](monitoring/CPU_CREDIT_QUICK_REFERENCE.md) - EC2 instance monitoring

### 📖 [Runbooks](runbooks/)
Operational procedures and emergency response
- [Operational Runbooks](runbooks/OPERATIONAL_RUNBOOKS.md) - Day-to-day operations
- [Production Deployment](runbooks/production-deployment.md) - Deployment procedures
- [Emergency Website Down](runbooks/emergency-website-down.md) - Emergency response guide

### ⚙️ [Setup](setup/)
Initial setup, configuration, and onboarding
- [Application Usage Guide](setup/APPLICATION_USAGE_GUIDE.md) - How to run the application (wsgi.py & manage.py)
- [Deployment Checklist](setup/DEPLOYMENT_CHECKLIST.md) - Pre-deployment verification
- [GitHub Secrets Setup](setup/GITHUB_SECRETS_SETUP.md) - CI/CD configuration
- [Setup README](setup/README.md) - Setup documentation

### 🔍 [Troubleshooting](troubleshooting/)
Issue resolution, debugging guides, and incident reports
- [Troubleshooting README](troubleshooting/README.md) - Troubleshooting index
- [PostgreSQL Safety Protocols](troubleshooting/postgresql-safety-protocols.md)
- [Deployment Health Check Failures](troubleshooting/deployment-health-check-failures.md)
- **Incident Reports:**
  - [Cloudflare 522 Error (2025-08-28)](troubleshooting/2025-08-28-cloudflare-522-error.md)
  - [PostgreSQL Sync Improvements (2025-09-05)](troubleshooting/2025-09-05-postgres-sync-improvements.md)
  - [PostgreSQL Migration Verification (2025-09-05)](troubleshooting/2025-09-05-postgresql-migration-verification.md)
  - [Login Session Troubleshooting (2025-09-19)](troubleshooting/2025-09-19-login-session-troubleshooting.md)
  - [PostgreSQL Connection Limit Errors (2025-09-21)](troubleshooting/2025-09-21-postgresql-connection-limit-500-errors.md)
  - [Database Connection Limit (2025-09-26)](troubleshooting/2025-09-26-database-connection-limit.md)
  - [Deployment Health Check Failures (2025-09-26)](troubleshooting/2025-09-26-deployment-health-check-failures.md)

---

## 🚀 Quick Start Guides

### For Developers
1. Start with [RBM_TENDER_APP_DOCUMENTATION.md](RBM_TENDER_APP_DOCUMENTATION.md) for overview
2. Review [Setup](setup/) for initial configuration
3. Check [Database Migration Workflow](database/DATABASE_MIGRATION_WORKFLOW.md) before making schema changes
4. Use [Migration Checklist](database/MIGRATION_CHECKLIST.md) for daily development

### For Deployment
1. Review [Production Deployment Guide](deployment/PRODUCTION_DEPLOYMENT_GUIDE.md)
2. Check [GitHub Actions Deployment Summary](deployment/GITHUB_ACTIONS_DEPLOYMENT_SUMMARY.md)
3. Follow [Deployment Checklist](setup/DEPLOYMENT_CHECKLIST.md)
4. Keep [Runbooks](runbooks/) handy for operations

### For Troubleshooting
1. Check [Troubleshooting](troubleshooting/) directory
2. Review incident reports for similar issues
3. Follow [Emergency Website Down](runbooks/emergency-website-down.md) for critical issues

---

## 📖 Documentation Conventions

### File Naming
- `UPPERCASE_WITH_UNDERSCORES.md` - Major documentation files
- `lowercase-with-hyphens.md` - Runbooks and procedures
- `YYYY-MM-DD-description.md` - Dated incident reports

### Documentation Updates
When updating documentation:
1. Keep the file in the appropriate category folder
2. Update this README if adding new major documents
3. Cross-reference related documents
4. Include date of last update in the document

---

## 🔍 Finding Documentation

### By Topic
Use the category folders above to browse by topic area.

### By Search
Use your editor's search feature (Ctrl+Shift+F in most editors) to search across all documentation.

### By Cross-Reference
Major documents include links to related documentation.

---

## 📝 Contributing to Documentation

When adding or updating documentation:
1. Place files in the appropriate category folder
2. Use clear, descriptive file names
3. Include a table of contents for long documents
4. Cross-reference related documents
5. Update this README for major additions
6. Follow the existing formatting conventions

---

## 📞 Support

For questions or issues:
1. Check the relevant category folder
2. Review troubleshooting guides
3. Check incident reports for similar issues
4. Consult the main documentation

---

**Last Updated:** October 2025
