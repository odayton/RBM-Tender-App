# RBM Tender App

A comprehensive tender and quote management system for RBM Systems.

## 🚨 CRITICAL: Data Safety First

**⚠️ IMPORTANT: This database contains real business data. NEVER delete or reset the database without explicit permission from the business owner.**

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
   - **Password**: Use the temporary password system (see maintenance section)

## 📁 Key Files & Directories

- `app/instance/rbm_tender_app.db` - Main database (DO NOT DELETE)
- `data/discounts.csv` - Discount codes
- `data/products.csv` - Product catalog
- `backup_manager.py` - Comprehensive backup system

## 🔧 Recent Updates

- ✅ Fixed database schema issues
- ✅ Added zebra striping to PDF tables
- ✅ Improved password management system
- ✅ Enhanced PDF styling and formatting

## 📋 Features

- **Deal Management**: Create and track sales opportunities
- **Quote Generation**: Professional PDF quotes with zebra striping
- **User Management**: Role-based access control
- **Product Catalog**: SKU-based product management
- **Discount System**: Flexible discount codes and rules

## 🛠️ Maintenance & Data Safety

### Database Location
The main database file is located at:
```
RBM-Tender-App-main/app/instance/rbm_tender_app.db
```

**Note**: The database file is created when the application first runs. If you don't see it, start the application first.

### Backup Instructions

#### Automatic Backup (Recommended)
The application has a built-in backup system. To create a backup:

1. **Start the application**:
   ```bash
   python app_runner.py
   ```

2. **Navigate to Admin Panel**:
   - Log in as admin (`admin@rbm.com`)
   - Go to Admin → Dashboard
   - Look for backup options

#### Manual Backup (Emergency)
If the automatic backup isn't working:

1. **Stop the application** (Ctrl+C if running)

2. **Copy the database file**:
   ```bash
   # Windows
   copy "RBM-Tender-App-main\app\instance\rbm_tender_app.db" "RBM-Tender-App-main\app\instance\rbm_tender_app_backup_$(date +%Y%m%d_%H%M%S).db"
   
   # Or manually copy the file with a timestamp
   ```

3. **Store backup securely**:
   - Keep backups in a separate location
   - Use descriptive names with timestamps
   - Consider cloud storage for important backups

### Database Schema Status

#### ✅ Recently Fixed Issues
- **Quote Line Items**: Added missing `custom_description` column
- **Discounts Table**: Added missing `is_active`, `valid_from`, `valid_until` columns
- **Zebra Striping**: Added light grey alternating rows to PDF tables

#### 📊 Current Data
- **Discounts**: 5 discount codes loaded (P1, H1, C1, WC1, ZIL1)
- **Admin User**: `admin@rbm.com` (temporary password system)
- **Sample Deal**: "Lorimer St" with line items for testing

### 🚫 What NOT to Do

#### ❌ Never Delete
- The main database file (`rbm_tender_app.db`)
- Any existing deals, quotes, or customer data
- User accounts without permission
- Discount codes or product data

#### ❌ Never Reset
- The entire database without explicit permission
- User passwords without proper procedures
- Quote data or deal information

### 🔑 Key Credentials

#### Admin Access
- **Email**: `admin@rbm.com`
- **Password**: Use the temporary password system
- **Role**: Full administrator access

#### Password Reset Process
1. Log in as admin
2. Go to Admin → Manage Users
3. Click the key icon next to any user
4. Share the generated temporary password
5. User must change password on first login

### Common Maintenance Tasks

#### Adding New Users
1. Log in as admin
2. Go to Admin → Register User
3. Fill in user details (no password needed)
4. System generates temporary password
5. Share temporary password with user

#### Loading Data
- **Discounts**: Use `data/discounts.csv` (already loaded)
- **Products**: Use `data/products.csv` (if needed)
- **Custom Data**: Follow existing import patterns

## 📞 Support

For detailed system documentation, see:
- **[Full Documentation](RBM_TENDER_APP_DOCUMENTATION.md)** - Complete system documentation
- **[Production Deployment](PRODUCTION_DEPLOYMENT_GUIDE.md)** - Production setup guide

## ⚠️ Data Safety Reminder

**This is a business application with real data. Always:**
- Create backups before making changes
- Never delete the database without permission
- Follow the backup guide for all maintenance tasks
- Test changes on a copy first

---

**For detailed backup and maintenance procedures, see the sections above in this guide.** 