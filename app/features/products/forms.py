"""
Product Management Forms

This module contains forms for managing products in the RBM Tender App.
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DecimalField, IntegerField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, Email, ValidationError
from wtforms.widgets import TextArea
from app.models.products.product_model import Product
from app.extensions import db

class ProductForm(FlaskForm):
    """Form for creating and editing products."""
    
    # Basic Information
    sku = StringField('SKU', validators=[
        DataRequired(message='SKU is required'),
        Length(min=1, max=80, message='SKU must be between 1 and 80 characters')
    ])
    
    name = StringField('Product Name', validators=[
        DataRequired(message='Product name is required'),
        Length(min=2, max=200, message='Product name must be between 2 and 200 characters')
    ])
    
    description = TextAreaField('Description', validators=[
        Optional(),
        Length(max=1000, message='Description cannot exceed 1000 characters')
    ])
    
    # Pricing
    unit_price = DecimalField('Unit Price ($)', validators=[
        DataRequired(message='Unit price is required'),
        NumberRange(min=0, message='Unit price must be positive')
    ])
    
    # User's Required Fields
    category = StringField('Category', validators=[
        DataRequired(message='Category is required'),
        Length(max=100, message='Category cannot exceed 100 characters')
    ])
    
    series = StringField('Series', validators=[
        Optional(),
        Length(max=100, message='Series cannot exceed 100 characters')
    ])
    
    item_no = StringField('Item No', validators=[
        Optional(),
        Length(max=100, message='Item number cannot exceed 100 characters')
    ])
    
    list_price_2025 = DecimalField('2025 List Price ($)', validators=[
        Optional(),
        NumberRange(min=0, message='List price must be positive')
    ])
    
    nett_buy_price_gst = DecimalField('Nett Buy Price (+GST) ($)', validators=[
        Optional(),
        NumberRange(min=0, message='Buy price must be positive')
    ])
    
    discount_code = StringField('Disc Code', validators=[
        Optional(),
        Length(max=10, message='Discount code cannot exceed 10 characters')
    ])
    
    brand = StringField('Brand', validators=[
        Optional(),
        Length(max=100, message='Brand cannot exceed 100 characters')
    ])
    
    model_number = StringField('Model Number', validators=[
        Optional(),
        Length(max=100, message='Model number cannot exceed 100 characters')
    ])
    
    # Physical Properties
    weight_kg = DecimalField('Weight (kg)', validators=[
        Optional(),
        NumberRange(min=0, message='Weight must be positive')
    ])
    
    dimensions = StringField('Dimensions (LxWxH cm)', validators=[
        Optional(),
        Length(max=100, message='Dimensions cannot exceed 100 characters')
    ])
    
    # Inventory Management
    stock_quantity = IntegerField('Stock Quantity', validators=[
        DataRequired(message='Stock quantity is required'),
        NumberRange(min=0, message='Stock quantity must be positive')
    ])
    
    reorder_level = IntegerField('Reorder Level', validators=[
        DataRequired(message='Reorder level is required'),
        NumberRange(min=0, message='Reorder level must be positive')
    ])
    
    lead_time_days = IntegerField('Lead Time (days)', validators=[
        DataRequired(message='Lead time is required'),
        NumberRange(min=0, message='Lead time must be positive')
    ])
    
    # Status
    is_active = BooleanField('Active')
    
    # Additional Information
    notes = TextAreaField('Notes', validators=[
        Optional(),
        Length(max=1000, message='Notes cannot exceed 1000 characters')
    ])
    
    def validate_sku(self, field):
        """Validate that SKU is unique."""
        # Check if this is an edit operation
        product_id = getattr(self, '_product_id', None)
        
        existing_product = Product.query.filter_by(sku=field.data).first()
        if existing_product and existing_product.id != product_id:
            raise ValidationError('SKU must be unique. This SKU is already in use.')
    
    def set_product_id(self, product_id):
        """Set the product ID for validation during edit operations."""
        self._product_id = product_id

class ProductSearchForm(FlaskForm):
    """Form for searching products."""
    
    search_term = StringField('Search', validators=[
        Optional(),
        Length(max=100, message='Search term cannot exceed 100 characters')
    ])
    
    category = StringField('Category', validators=[
        Optional(),
        Length(max=100, message='Category cannot exceed 100 characters')
    ])
    
    series = StringField('Series', validators=[
        Optional(),
        Length(max=100, message='Series cannot exceed 100 characters')
    ])
    
    item_no = StringField('Item No', validators=[
        Optional(),
        Length(max=100, message='Item number cannot exceed 100 characters')
    ])
    
    brand = StringField('Brand', validators=[
        Optional(),
        Length(max=100, message='Brand cannot exceed 100 characters')
    ])
    
    availability = SelectField('Availability', choices=[
        ('', 'All'),
        ('in_stock', 'In Stock'),
        ('low_stock', 'Low Stock'),
        ('out_of_stock', 'Out of Stock'),
        ('inactive', 'Inactive')
    ])
    
    price_range = SelectField('Price Range', choices=[
        ('', 'All Prices'),
        ('0-100', '$0 - $100'),
        ('100-500', '$100 - $500'),
        ('500-1000', '$500 - $1,000'),
        ('1000+', '$1,000+')
    ])

class ProductBulkActionForm(FlaskForm):
    """Form for bulk actions on products."""
    
    action = SelectField('Action', choices=[
        ('', 'Select Action'),
        ('activate', 'Activate Selected'),
        ('deactivate', 'Deactivate Selected'),
        ('delete', 'Delete Selected'),
        ('export', 'Export Selected')
    ], validators=[DataRequired(message='Please select an action')])
    
    product_ids = StringField('Product IDs', validators=[
        DataRequired(message='Please select at least one product')
    ])

class ProductImportForm(FlaskForm):
    """Form for importing products from CSV."""
    
    csv_file = FileField('CSV File', validators=[
        DataRequired(message='Please select a CSV file'),
        FileAllowed(['csv'], message='Only CSV files are allowed')
    ])
    
    update_existing = BooleanField('Update existing products')
    skip_errors = BooleanField('Skip rows with errors')

class ProductExportForm(FlaskForm):
    """Form for exporting products."""
    
    format = SelectField('Export Format', choices=[
        ('csv', 'CSV'),
        ('excel', 'Excel'),
        ('pdf', 'PDF')
    ], validators=[DataRequired(message='Please select an export format')])
    
    include_inactive = BooleanField('Include inactive products')
    include_metadata = BooleanField('Include metadata') 