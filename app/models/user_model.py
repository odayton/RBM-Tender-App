from typing import Dict, Any
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum
# Import relationship from sqlalchemy.orm
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
import enum

from app.models.base_model import BaseModel
from app.core.core_errors import ValidationError

class UserRole(enum.Enum):
    """User role types"""
    ADMIN = "Admin"
    SALES = "Sales"
    MANAGER = "Manager"
    VIEWER = "Viewer"

class User(BaseModel):
    """Model for user accounts"""
    __tablename__ = 'users'
    
    # User Information
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    
    # User Details
    first_name = Column(String(50))
    last_name = Column(String(50))
    phone_number = Column(String(20))
    role = Column(Enum(UserRole), nullable=False, default=UserRole.SALES)
    
    # Account Status
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    
    # --- START OF THE FIX ---
    # Add the missing relationship to link back to the Deal model
    deals = relationship('Deal', back_populates='owner')
    # --- END OF THE FIX ---

    @property
    def full_name(self):
        """Return the user's full name."""
        return f"{self.first_name or ''} {self.last_name or ''}".strip()

    @property
    def password(self):
        """Prevent password from being accessed"""
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password) -> bool:
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role='{self.role.value}')>"