# app/models/products/product_model.py

from sqlalchemy import Column, String, Text, Numeric, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base_model import BaseModel

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

    def __repr__(self):
        return f"<Product(id={self.id}, sku='{self.sku}', name='{self.name}')>"