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

    # New Schema Fields (14 columns total)
    category = Column(String(100), index=True)  # 1. Category
    sub_category = Column(String(100))  # 2. SubCategory
    series = Column(String(100))  # 3. Series
    item_no = Column(String(100))  # 4. Item No
    description = Column(Text)  # 5. Description
    pack = Column(String(50))  # 6. Pack
    carton_qty = Column(Integer, default=1)  # 7. Carton Qty
    list_price = Column(Numeric(10, 2))  # 8. List price
    discount_code = Column(String(10), ForeignKey('discounts.code'), nullable=True)  # 9. Disc Code
    notes = Column(Text)  # 10. Note
    weight_kg = Column(Numeric(8, 3))  # 11. weight_kg
    dimensions = Column(String(100))  # 12. dimensions
    lead_time_days = Column(Integer, default=0)  # 13. lead_time_days
    is_active = Column(Boolean, default=True, nullable=False, index=True)  # 14. is_active

    # Relationships
    discount = relationship("Discount", back_populates="products")
    
    # Line items that use this product
    line_items = relationship("QuoteLineItem", back_populates="product")

    # Constraints and indexes
    __table_args__ = (
        CheckConstraint('list_price >= 0', name='check_product_list_price'),
        CheckConstraint('carton_qty >= 1', name='check_product_carton_qty'),
        CheckConstraint('lead_time_days >= 0', name='check_product_lead_time'),
        CheckConstraint('weight_kg >= 0', name='check_product_weight'),
        Index('idx_product_category_active', 'category', 'is_active'),
        Index('idx_product_series', 'series'),
        Index('idx_product_item_no', 'item_no'),
        Index('idx_product_sub_category', 'sub_category'),
    )

    def validate(self) -> None:
        """Custom validation for product data."""
        super().validate()
        
        if not self.item_no or len(self.item_no.strip()) < 1:
            raise ValidationError("Item No is required and cannot be empty.")
        
        if not self.description or len(self.description.strip()) < 2:
            raise ValidationError("Description must be at least 2 characters long.")
        
        if self.list_price and self.list_price < 0:
            raise ValidationError("List price cannot be negative.")
        
        if self.carton_qty < 1:
            raise ValidationError("Carton quantity must be at least 1.")
        
        if self.lead_time_days < 0:
            raise ValidationError("Lead time cannot be negative.")
        
        if self.weight_kg and self.weight_kg < 0:
            raise ValidationError("Weight cannot be negative.")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the product instance to a dictionary."""
        data = super().to_dict()
        data['discount_percentage'] = self.discount.percentage if self.discount else 0
        data['discounted_price'] = float(self.get_discounted_price())
        data['usage_count'] = len(self.line_items)
        return data

    def get_discounted_price(self) -> Decimal:
        """Get the price after applying discount."""
        if self.discount and self.discount.is_valid() and self.list_price:
            discount_amount = self.list_price * (self.discount.percentage / Decimal('100'))
            return self.list_price - discount_amount
        return self.list_price or Decimal('0.00')

    def get_effective_price(self) -> Decimal:
        """Get the effective price after applying discounts."""
        return self.get_discounted_price()

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
        return f"<Product(id={self.id}, item_no='{self.item_no}', description='{self.description}', active={self.is_active})>"