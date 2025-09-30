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
    
    # New Schema Fields (Primary)
    category = StringField('Category', validators=[
        DataRequired(message='Category is required'),
        Length(max=200, message='Category cannot exceed 200 characters')
    ])
    
    sub_category = StringField('Sub Category', validators=[
        Optional(),
        Length(max=200, message='Sub Category cannot exceed 200 characters')
    ])
    
    series = StringField('Series', validators=[
        Optional(),
        Length(max=200, message='Series cannot exceed 200 characters')
    ])
    
    item_no = StringField('Item No', validators=[
        DataRequired(message='Item No is required'),
        Length(max=200, message='Item number cannot exceed 200 characters')
    ])
    
    description = TextAreaField('Description', validators=[
        DataRequired(message='Description is required'),
        Length(max=2000, message='Description cannot exceed 2000 characters')
    ])
    
    nett = DecimalField('Nett ($)', validators=[
        Optional(),
        NumberRange(min=0, message='Nett price must be positive')
    ])
    
    discount_code = StringField('Disc Code', validators=[
        Optional(),
        Length(max=10, message='Discount code cannot exceed 10 characters')
    ])
    
    notes = TextAreaField('Notes', validators=[
        Optional(),
        Length(max=1000, message='Notes cannot exceed 1000 characters')
    ])
    
    # Physical Properties
    weight_kg = DecimalField('Weight (kg)', validators=[
        Optional(),
        NumberRange(min=0, message='Weight must be positive')
    ])
    
    dimensions = StringField('Dimensions', validators=[
        Optional(),
        Length(max=200, message='Dimensions cannot exceed 200 characters')
    ])
    
    # Management Fields
    lead_time_days = IntegerField('Lead Time (days)', validators=[
        Optional(),
        NumberRange(min=0, message='Lead time must be positive')
    ])
    
    # Status
    is_active = BooleanField('Active')
    
    # Legacy Fields (for backward compatibility)
    sku = StringField('SKU (Legacy)', validators=[
        Optional(),
        Length(max=80, message='SKU cannot exceed 80 characters')
    ])
    
    name = StringField('Product Name (Legacy)', validators=[
        Optional(),
        Length(max=200, message='Product name cannot exceed 200 characters')
    ])
    
    unit_price = DecimalField('Unit Price (Legacy) ($)', validators=[
        Optional(),
        NumberRange(min=0, message='Unit price must be positive')
    ])
    
    brand = StringField('Brand (Legacy)', validators=[
        Optional(),
        Length(max=100, message='Brand cannot exceed 100 characters')
    ])
    
    model_number = StringField('Model Number (Legacy)', validators=[
        Optional(),
        Length(max=100, message='Model number cannot exceed 100 characters')
    ])
    
    stock_quantity = IntegerField('Stock Quantity (Legacy)', validators=[
        Optional(),
        NumberRange(min=0, message='Stock quantity must be positive')
    ])
    
    reorder_level = IntegerField('Reorder Level (Legacy)', validators=[
        Optional(),
        NumberRange(min=0, message='Reorder level must be positive')
    ])
    
    def validate_item_no(self, field):
        """Validate that Item No is unique."""
        # Check if this is an edit operation
        product_id = getattr(self, '_product_id', None)
        
        existing_product = Product.query.filter_by(item_no=field.data).first()
        if existing_product and existing_product.id != product_id:
            raise ValidationError('Item No must be unique. This Item No is already in use.')
    
    def validate_sku(self, field):
        """Validate that SKU is unique (legacy)."""
        if not field.data:
            return
            
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
        Length(max=200, message='Search term cannot exceed 200 characters')
    ])
    
    category = StringField('Category', validators=[
        Optional(),
        Length(max=200, message='Category cannot exceed 200 characters')
    ])
    
    sub_category = StringField('Sub Category', validators=[
        Optional(),
        Length(max=200, message='Sub Category cannot exceed 200 characters')
    ])
    
    series = StringField('Series', validators=[
        Optional(),
        Length(max=200, message='Series cannot exceed 200 characters')
    ])
    
    item_no = StringField('Item No', validators=[
        Optional(),
        Length(max=200, message='Item number cannot exceed 200 characters')
    ])
    
    brand = StringField('Brand (Legacy)', validators=[
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