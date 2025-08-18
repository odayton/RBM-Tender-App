# app/models/products/product_model.py

from typing import Dict, Any, List, Optional
from sqlalchemy import Column, String, Text, Numeric, Integer, ForeignKey, UniqueConstraint, Boolean, Index, CheckConstraint
from sqlalchemy.orm import relationship
from decimal import Decimal
from app.models.base_model import BaseModel
from app.core.core_errors import ValidationError

class Product(BaseModel):
    """
    Represents a sellable product or service in a catalog.
    This can be a pump, an accessory, or a generic item.
    """
    __tablename__ = 'products'

    # Basic Information
    sku = Column(String(80), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    unit_price = Column(Numeric(10, 2), nullable=False, default=0.0)
    
    # User's Required Fields
    category = Column(String(100), index=True)  # Category
    series = Column(String(100))  # Series
    item_no = Column(String(100))  # Item No
    list_price_2025 = Column(Numeric(10, 2))  # 2025 List Price
    discount_code = Column(String(10), ForeignKey('discounts.code'), nullable=True)  # Disc Code
    nett_buy_price_gst = Column(Numeric(10, 2))  # Nett Buy Price (+GST)
    
    # Additional fields for better product management
    brand = Column(String(100))
    model_number = Column(String(100))
    weight_kg = Column(Numeric(8, 3))  # Weight in kilograms
    dimensions = Column(String(100))  # Format: "LxWxH cm"
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    stock_quantity = Column(Integer, default=0)
    reorder_level = Column(Integer, default=0)
    lead_time_days = Column(Integer, default=0)
    notes = Column(Text)

    # Relationships
    discount = relationship("Discount", back_populates="products")
    
    pump_assembly_id = Column(Integer, ForeignKey('pump_assemblies.id'), nullable=True)
    pump_assembly = relationship("PumpAssembly", back_populates="product", uselist=False)
    
    # Line items that use this product
    line_items = relationship("QuoteLineItem", back_populates="product")

    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint('pump_assembly_id', name='uq_product_pump_assembly_id'),
        CheckConstraint('unit_price >= 0', name='check_product_unit_price'),
        CheckConstraint('list_price_2025 >= 0', name='check_product_list_price'),
        CheckConstraint('nett_buy_price_gst >= 0', name='check_product_nett_price'),
        CheckConstraint('stock_quantity >= 0', name='check_product_stock_quantity'),
        CheckConstraint('reorder_level >= 0', name='check_product_reorder_level'),
        CheckConstraint('lead_time_days >= 0', name='check_product_lead_time'),
        Index('idx_product_category_active', 'category', 'is_active'),
        Index('idx_product_series', 'series'),
        Index('idx_product_item_no', 'item_no'),
        Index('idx_product_sku_name', 'sku', 'name'),
    )

    def validate(self) -> None:
        """Custom validation for product data."""
        super().validate()
        
        if not self.sku or len(self.sku.strip()) < 1:
            raise ValidationError("SKU is required and cannot be empty.")
        
        if not self.name or len(self.name.strip()) < 2:
            raise ValidationError("Product name must be at least 2 characters long.")
        
        if self.unit_price < 0:
            raise ValidationError("Unit price cannot be negative.")
        
        if self.list_price_2025 and self.list_price_2025 < 0:
            raise ValidationError("2025 List Price cannot be negative.")
        
        if self.nett_buy_price_gst and self.nett_buy_price_gst < 0:
            raise ValidationError("Nett Buy Price (+GST) cannot be negative.")
        
        if self.stock_quantity < 0:
            raise ValidationError("Stock quantity cannot be negative.")
        
        if self.reorder_level < 0:
            raise ValidationError("Reorder level cannot be negative.")
        
        if self.lead_time_days < 0:
            raise ValidationError("Lead time cannot be negative.")
        
        if self.weight_kg and self.weight_kg < 0:
            raise ValidationError("Weight cannot be negative.")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the product instance to a dictionary."""
        data = super().to_dict()
        data['discount_percentage'] = self.discount.percentage if self.discount else 0
        data['has_pump_assembly'] = bool(self.pump_assembly_id)
        data['discounted_price'] = float(self.get_discounted_price())
        data['is_low_stock'] = self.is_low_stock()
        data['is_out_of_stock'] = self.is_out_of_stock()
        data['usage_count'] = len(self.line_items)
        return data

    def get_discounted_price(self) -> Decimal:
        """Get the price after applying discount."""
        if self.discount and self.discount.is_valid():
            discount_amount = self.unit_price * (self.discount.percentage / Decimal('100'))
            return self.unit_price - discount_amount
        return self.unit_price

    def get_list_price_2025(self) -> Decimal:
        """Get the 2025 list price, fallback to unit_price if not set."""
        return self.list_price_2025 if self.list_price_2025 else self.unit_price

    def get_nett_buy_price_gst(self) -> Decimal:
        """Get the nett buy price including GST."""
        return self.nett_buy_price_gst if self.nett_buy_price_gst else self.unit_price

    def is_low_stock(self) -> bool:
        """Check if product is low on stock (below reorder level)."""
        return self.stock_quantity <= self.reorder_level

    def is_out_of_stock(self) -> bool:
        """Check if product is out of stock."""
        return self.stock_quantity <= 0

    def is_available(self) -> bool:
        """Check if product is available for sale."""
        return self.is_active and not self.is_out_of_stock()

    def get_availability_status(self) -> str:
        """Get the availability status of the product."""
        if not self.is_active:
            return "Inactive"
        elif self.is_out_of_stock():
            return "Out of Stock"
        elif self.is_low_stock():
            return "Low Stock"
        else:
            return "In Stock"

    def update_stock(self, quantity_change: int) -> None:
        """Update stock quantity (positive for additions, negative for reductions)."""
        new_quantity = self.stock_quantity + quantity_change
        if new_quantity < 0:
            raise ValidationError("Stock quantity cannot go below 0.")
        self.stock_quantity = new_quantity

    def get_total_value(self) -> Decimal:
        """Calculate total value of current stock."""
        return self.unit_price * self.stock_quantity

    def get_usage_statistics(self) -> Dict[str, Any]:
        """Get usage statistics for this product."""
        total_quantity_sold = sum(item.quantity for item in self.line_items)
        total_value_sold = sum(item.total_price for item in self.line_items)
        
        return {
            'total_quantity_sold': total_quantity_sold,
            'total_value_sold': float(total_value_sold),
            'usage_count': len(self.line_items),
            'average_quantity_per_use': total_quantity_sold / len(self.line_items) if self.line_items else 0
        }

    def get_similar_products(self, limit: int = 5) -> List['Product']:
        """Get similar products in the same category."""
        if not self.category:
            return []
        
        from app.extensions import db
        return Product.query.filter(
            Product.category == self.category,
            Product.id != self.id,
            Product.is_active == True
        ).limit(limit).all()

    def __repr__(self):
        return f"<Product(id={self.id}, sku='{self.sku}', name='{self.name}', active={self.is_active})>"