from sqlalchemy import Column, String, Text, Numeric
# THIS IS THE FIX: Using an absolute import path from the 'app' root
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

    def __repr__(self):
        return f"<Product(id={self.id}, sku='{self.sku}', name='{self.name}')>"