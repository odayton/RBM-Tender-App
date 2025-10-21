# app/models/pumps/pump_series.py

from sqlalchemy import Column, String, Text, Boolean
from app.models.base_model import BaseModel


class PumpSeries(BaseModel):
    """
    Model for pump series (NBG, NK, CR, CRE, MAGNA, etc.)
    Stores series-level configuration including pump curve URL patterns
    """
    __tablename__ = 'pump_series'
    
    series_code = Column(String(20), unique=True, nullable=False, index=True)
    series_name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Pump curve link configuration
    curve_url_pattern = Column(String(500))
    series_path = Column(String(100))  # Path segment for Grundfos URLs
    
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    from sqlalchemy.orm import relationship
    pumps = relationship("Pump", back_populates="series", cascade="all, delete-orphan")
    drip_trip_trays = relationship("DripTripTray", back_populates="series")
    
    def __repr__(self):
        return f"<PumpSeries {self.series_code}: {self.series_name}>"
    
    def generate_pump_curve_url(self, pump_name, part_number):
        """
        Generate pump curve URL for a pump in this series
        
        Args:
            pump_name: Pump name (e.g., "CR 15-3")
            part_number: Manufacturer part number (e.g., "96501699")
        
        Returns:
            Full URL to Grundfos pump curve or None if not configured
        """
        if not self.series_path or not part_number:
            return None
        
        # Generate model slug from pump name
        # Example: "CR 15-3" → "cr-15-3"
        model_slug = pump_name.lower().replace(' ', '-').replace('/', '-')
        
        # Build full URL
        base_url = "https://product-selection.grundfos.com/au/products"
        full_url = f"{base_url}/{self.series_path}/{model_slug}-{part_number}"
        
        return full_url

