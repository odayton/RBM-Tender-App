# app/models/products/product_model.py

from typing import Dict, Any
from sqlalchemy import Column, String, Text, Numeric, Integer, ForeignKey, UniqueConstraint
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

    sku = Column(String(80), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    unit_price = Column(Numeric(10, 2), nullable=False, default=0.0)

    # This relationship links to the 'products' field in the Discount model
    discount_code = Column(String(10), ForeignKey('discounts.code'), nullable=True)
    discount = relationship("Discount", back_populates="products")
    
    pump_assembly_id = Column(Integer, ForeignKey('pump_assemblies.id'), nullable=True)
    pump_assembly = relationship("PumpAssembly", back_populates="product", uselist=False)

    __table_args__ = (
        UniqueConstraint('pump_assembly_id', name='uq_product_pump_assembly_id'),
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

    def to_dict(self) -> Dict[str, Any]:
        """Convert the product instance to a dictionary."""
        data = super().to_dict()
        data['discount_percentage'] = self.discount.percentage if self.discount else 0
        data['has_pump_assembly'] = bool(self.pump_assembly_id)
        return data

    def get_discounted_price(self) -> Decimal:
        """Get the price after applying discount."""
        if self.discount:
            discount_amount = self.unit_price * (self.discount.percentage / Decimal('100'))
            return self.unit_price - discount_amount
        return self.unit_price

    def __repr__(self):
        return f"<Product(id={self.id}, sku='{self.sku}', name='{self.name}')>"