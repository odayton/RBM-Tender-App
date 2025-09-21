# app/models/deals/quote_snapshot.py

from typing import Dict, Any, Optional
from sqlalchemy import Column, String, Integer, ForeignKey, Text, DateTime, JSON, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import json

from ..base_model import BaseModel
from ...core.core_errors import ValidationError

class QuoteSnapshot(BaseModel):
    """Model for storing snapshots of quote options for version control."""
    __tablename__ = 'quote_snapshots'
    
    # Snapshot Details
    quote_option_id = Column(Integer, ForeignKey('quote_options.id'), nullable=False, index=True)
    version_number = Column(Integer, nullable=False, default=1)
    snapshot_name = Column(String(200), nullable=False, default="Auto-snapshot")
    
    # Snapshot Data (stored as JSON)
    line_items_data = Column(JSON, nullable=False)  # Serialized line items
    freight_charge = Column(String(50), nullable=False, default="0.00")
    lead_time_value = Column(String(20), nullable=True)
    lead_time_unit = Column(String(10), nullable=True, default='weeks')
    is_ex_stock_brisbane = Column(String(10), nullable=False, default='false')
    
    # Metadata
    created_by = Column(String(100), nullable=True)  # User who created the snapshot
    notes = Column(Text)
    
    # Relationships
    quote_option = relationship("QuoteOption", back_populates="snapshots")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_snapshot_option_version', 'quote_option_id', 'version_number'),
        Index('idx_snapshot_created_at', 'created_at'),
    )

    def validate(self) -> None:
        """Custom validation for snapshot data."""
        super().validate()
        
        if not self.quote_option_id:
            raise ValidationError("Quote option ID is required.")
        
        if self.version_number < 1:
            raise ValidationError("Version number must be at least 1.")
        
        if not self.line_items_data:
            raise ValidationError("Line items data is required.")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the snapshot instance to a dictionary."""
        data = super().to_dict()
        data['line_items_count'] = len(self.line_items_data) if self.line_items_data else 0
        data['total_value'] = self.calculate_total_value()
        return data

    def calculate_total_value(self) -> float:
        """Calculate total value from line items data."""
        if not self.line_items_data:
            return 0.0
        
        total = 0.0
        for item in self.line_items_data:
            quantity = item.get('quantity', 1)
            unit_price = float(item.get('unit_price', 0))
            discount = float(item.get('discount', 0))
            
            subtotal = quantity * unit_price
            discount_amount = subtotal * (discount / 100)
            total += subtotal - discount_amount
        
        return total

    @classmethod
    def create_snapshot(cls, quote_option_id: int, created_by: str = None, notes: str = None) -> 'QuoteSnapshot':
        """Create a new snapshot of a quote option."""
        from app.models.deals.deal_models import QuoteOption
        
        # Get the quote option
        quote_option = QuoteOption.query.get(quote_option_id)
        if not quote_option:
            raise ValidationError(f"Quote option {quote_option_id} not found.")
        
        # Get next version number
        latest_snapshot = cls.query.filter_by(quote_option_id=quote_option_id).order_by(cls.version_number.desc()).first()
        next_version = (latest_snapshot.version_number + 1) if latest_snapshot else 1
        
        # Prepare line items data
        line_items_data = []
        for item in quote_option.line_items:
            line_items_data.append({
                'product_id': item.product_id,
                'custom_sku': item.custom_sku,
                'custom_name': item.custom_name,
                'custom_description': item.custom_description,
                'quantity': item.quantity,
                'unit_price': str(item.unit_price),
                'discount': str(item.discount),
                'notes': item.notes,
                'display_order': item.display_order
            })
        
        # Create snapshot
        snapshot = cls(
            quote_option_id=quote_option_id,
            version_number=next_version,
            line_items_data=line_items_data,
            freight_charge=str(quote_option.freight_charge),
            lead_time_value=quote_option.lead_time_value,
            lead_time_unit=quote_option.lead_time_unit,
            is_ex_stock_brisbane=str(quote_option.is_ex_stock_brisbane).lower(),
            created_by=created_by,
            notes=notes
        )
        
        return snapshot

    @classmethod
    def get_snapshots_for_option(cls, quote_option_id: int) -> list:
        """Get all snapshots for a quote option."""
        return cls.query.filter_by(quote_option_id=quote_option_id).order_by(cls.version_number.desc()).all()

    @classmethod
    def restore_snapshot(cls, snapshot_id: int) -> Dict[str, Any]:
        """Restore a snapshot to a quote option."""
        snapshot = cls.query.get(snapshot_id)
        if not snapshot:
            raise ValidationError(f"Snapshot {snapshot_id} not found.")
        
        # Return the snapshot data for restoration
        return {
            'line_items_data': snapshot.line_items_data,
            'freight_charge': float(snapshot.freight_charge),
            'lead_time_value': snapshot.lead_time_value,
            'lead_time_unit': snapshot.lead_time_unit,
            'is_ex_stock_brisbane': snapshot.is_ex_stock_brisbane.lower() == 'true'
        }

    def get_snapshot_summary(self) -> str:
        """Get a summary of the snapshot."""
        line_count = len(self.line_items_data) if self.line_items_data else 0
        total_value = self.calculate_total_value()
        
        return f"Version {self.version_number}: {line_count} items, ${total_value:,.2f}"

    def __repr__(self) -> str:
        return f"<QuoteSnapshot(id={self.id}, option_id={self.quote_option_id}, version={self.version_number})>"

