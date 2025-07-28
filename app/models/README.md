# RBM Tender App - Data Models Documentation

## Overview

This document describes the core data models for the RBM Tender App, including their relationships, validation rules, and usage patterns.

## Core Models

### 1. User Model (`app/models/user_model.py`)

**Purpose**: Manages user accounts and authentication.

**Key Fields**:
- `username`: Unique username for login
- `email`: Unique email address
- `password_hash`: Hashed password (not accessible directly)
- `first_name`, `last_name`: User's full name
- `phone_number`: Contact information
- `role`: User role (Admin, Sales, Manager, Viewer)
- `is_active`: Account status
- `last_login`: Timestamp of last login

**Relationships**:
- `deals`: One-to-many relationship with Deal model (deals owned by user)

**Key Methods**:
- `verify_password(password)`: Check password against hash
- `has_role(role_name)`: Check if user has specific role
- `is_admin()`, `is_sales()`, `is_manager()`, `is_viewer()`: Role check methods
- `can_manage_users()`: Check if user can manage other users
- `can_view_admin_panel()`: Check admin panel access
- `get_role_display_name()`: Get user-friendly role name

**Validation Rules**:
- Email must be valid format
- Username must be at least 3 characters
- Role is required

### 2. Company Model (`app/models/customers/company_model.py`)

**Purpose**: Represents customer companies.

**Key Fields**:
- `company_name`: Unique company name
- `address`: Company address

**Relationships**:
- `contacts`: One-to-many with Contact model
- `deals`: Many-to-many with Deal model
- `quote_streams`: One-to-many with QuoteRecipient model

**Key Methods**:
- `get_primary_contact()`: Get first contact for company
- `to_dict()`: Include contact and deal counts

**Validation Rules**:
- Company name must be at least 2 characters

### 3. Contact Model (`app/models/customers/customer_model.py`)

**Purpose**: Represents people associated with companies.

**Key Fields**:
- `name`: Contact's full name
- `email`: Unique email address
- `phone_number`: Contact phone
- `position`: Job title/position
- `company_id`: Foreign key to Company

**Relationships**:
- `company`: Many-to-one with Company model
- `deals`: Many-to-many with Deal model

**Key Methods**:
- `get_full_info()`: Get formatted contact information
- `to_dict()`: Include company name and deal count

**Validation Rules**:
- Email must be valid format
- Name is required

### 4. Deal Model (`app/models/deals/deal_models.py`)

**Purpose**: Represents sales opportunities and projects.

**Key Fields**:
- `project_name`: Unique project name
- `stage`: Deal stage (Sales Lead, Proposal, etc.)
- `deal_type`: Type of deal (HVAC, Plumbing, etc.)
- `state`: Australian state
- `total_amount`: Deal value
- `owner_id`: Foreign key to User (deal owner)

**Relationships**:
- `owner`: Many-to-one with User model
- `recipients`: One-to-many with QuoteRecipient model
- `contacts`: Many-to-many with Contact model
- `companies`: Many-to-many with Company model

**Key Methods**:
- `get_total_quotes_value()`: Calculate total quote value
- `get_latest_quote()`: Get most recent quote
- `can_be_edited_by(user)`: Check edit permissions

**Validation Rules**:
- Project name must be at least 3 characters
- Owner must be assigned

### 5. Product Model (`app/models/products/product_model.py`)

**Purpose**: Represents sellable products and services.

**Key Fields**:
- `sku`: Unique product SKU
- `name`: Product name
- `description`: Product description
- `unit_price`: Product price
- `discount_code`: Foreign key to Discount model
- `pump_assembly_id`: Foreign key to PumpAssembly model

**Relationships**:
- `discount`: Many-to-one with Discount model
- `pump_assembly`: One-to-one with PumpAssembly model

**Key Methods**:
- `get_discounted_price()`: Calculate price after discount
- `to_dict()`: Include discount percentage and pump assembly info

**Validation Rules**:
- SKU is required
- Product name must be at least 2 characters
- Unit price cannot be negative

## Quote System Models

### 6. QuoteRecipient Model

**Purpose**: Links deals to companies for quote generation.

**Key Fields**:
- `deal_id`: Foreign key to Deal
- `company_id`: Foreign key to Company

**Relationships**:
- `deal`: Many-to-one with Deal model
- `company`: Many-to-one with Company model
- `quotes`: One-to-many with Quote model

### 7. Quote Model

**Purpose**: Represents individual quotes within a deal.

**Key Fields**:
- `recipient_id`: Foreign key to QuoteRecipient
- `revision`: Quote revision number
- `notes`: Quote notes
- `created_at`: Creation timestamp

**Relationships**:
- `recipient`: Many-to-one with QuoteRecipient model
- `options`: One-to-many with QuoteOption model

**Key Methods**:
- `total_price`: Calculate total quote value
- `gst`: Calculate GST amount
- `grand_total`: Calculate total including GST

### 8. QuoteOption Model

**Purpose**: Represents different options within a quote.

**Key Fields**:
- `quote_id`: Foreign key to Quote
- `name`: Option name
- `freight_charge`: Freight cost

**Relationships**:
- `quote`: Many-to-one with Quote model
- `line_items`: One-to-many with QuoteLineItem model

**Key Methods**:
- `total_price`: Calculate option total including freight
- `subtotal`: Calculate subtotal excluding freight
- `gst`: Calculate GST amount
- `grand_total`: Calculate total including GST

### 9. QuoteLineItem Model

**Purpose**: Represents individual items within a quote option.

**Key Fields**:
- `option_id`: Foreign key to QuoteOption
- `product_id`: Foreign key to Product (optional)
- `quantity`: Item quantity
- `unit_price`: Unit price
- `notes`: Item notes
- `discount`: Discount percentage
- `display_order`: Display order
- `custom_sku`, `custom_name`: For non-catalog items

**Relationships**:
- `option`: Many-to-one with QuoteOption model
- `product`: Many-to-one with Product model

**Key Methods**:
- `total_price`: Calculate final price including discounts

## Supporting Models

### 10. Discount Model

**Purpose**: Manages product discounts.

**Key Fields**:
- `code`: Unique discount code
- `percentage`: Discount percentage

**Relationships**:
- `products`: One-to-many with Product model

## Role-Based Access Control

### User Roles

1. **Admin**: Full system access, can manage users and all data
2. **Manager**: Can view admin panel, manage deals, limited user management
3. **Sales**: Can create and manage their own deals, view products
4. **Viewer**: Read-only access to assigned data

### Permission Methods

- `user.is_admin()`: Check if user is admin
- `user.is_sales()`: Check if user is sales
- `user.is_manager()`: Check if user is manager
- `user.is_viewer()`: Check if user is viewer
- `user.can_manage_users()`: Check if user can manage other users
- `user.can_view_admin_panel()`: Check if user can access admin panel
- `deal.can_be_edited_by(user)`: Check if user can edit specific deal

## Validation and Error Handling

All models inherit from `BaseModel` which provides:
- Automatic timestamp management (`created_at`, `updated_at`)
- Basic validation framework
- Error handling with `ValidationError`

Custom validation is implemented in each model's `validate()` method.

## Usage Examples

### Creating a User
```python
user = User(
    username='john_doe',
    email='john@example.com',
    first_name='John',
    last_name='Doe',
    role=UserRole.SALES
)
user.password = 'secure_password'
user.save()
```

### Creating a Deal
```python
deal = Deal(
    project_name='Office Building HVAC',
    stage=DealStage.PROPOSAL,
    deal_type=DealType.HVAC,
    state=AustralianState.NSW,
    owner_id=user.id
)
deal.companies = [company]
deal.contacts = [contact]
deal.save()
```

### Checking Permissions
```python
if user.can_manage_users():
    # Show user management interface
    
if deal.can_be_edited_by(current_user):
    # Show edit buttons
```

## Database Migrations

Models are managed through Flask-Migrate. To create a new migration:

```bash
flask db migrate -m "Description of changes"
flask db upgrade
```

## Best Practices

1. **Always validate data** before saving
2. **Use relationship methods** instead of direct foreign key access
3. **Check permissions** before allowing operations
4. **Use the `to_dict()` method** for API responses
5. **Leverage model methods** for business logic
6. **Handle errors gracefully** with try-catch blocks 