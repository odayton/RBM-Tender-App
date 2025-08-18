# RBM Tender App

A comprehensive tender and quote management system for RBM Systems.

## 🚀 Quick Start

1. **Start the application**:
   ```bash
   python app_runner.py
   ```

2. **Choose your mode**:
   - **Development Mode**: Manual login required
   - **Easy Development Mode**: Auto-login enabled (recommended)
   - **Testing Mode**: In-memory database

3. **Login credentials**:
   - **Email**: `admin@rbm.com`
   - **Password**: Use the temporary password system

## 📚 Documentation

All documentation has been organized in the `docs/` folder:

- **[📖 Quick Start & Maintenance](docs/README.md)** - Daily operations and data safety guide
- **[🚀 Production Deployment](docs/PRODUCTION_DEPLOYMENT_GUIDE.md)** - Deployment options and production setup
- **[🔧 Technical Reference](docs/RBM_TENDER_APP_DOCUMENTATION.md)** - Complete system documentation
- **[📋 Documentation Index](docs/INDEX.md)** - Navigation guide for all documentation

## 📁 Key Files & Directories

- `app/instance/rbm_tender_app.db` - Main database (DO NOT DELETE)
- `data/discounts.csv` - Discount codes
- `data/products.csv` - Product catalog
- `backup_manager.py` - Comprehensive backup system
- `docs/` - All documentation and guides

## 🔧 Recent Updates

- ✅ Fixed database schema issues
- ✅ Added zebra striping to PDF tables
- ✅ Improved password management system
- ✅ Enhanced PDF styling and formatting
- ✅ Organized documentation into `docs/` folder

## 📋 Features

- **Deal Management**: Create and track sales opportunities
- **Quote Generation**: Professional PDF quotes with zebra striping
- **User Management**: Role-based access control
- **Product Catalog**: SKU-based product management
- **Discount System**: Flexible discount codes and rules

## 🚨 Data Safety Reminder

**This is a business application with real data. Always:**
- Create backups before making changes
- Never delete the database without permission
- Follow the backup guide for all maintenance tasks
- Test changes on a copy first

---

**For detailed information, see the [Documentation](docs/) folder.** 