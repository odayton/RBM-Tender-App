from typing import Dict, Any
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin  # <-- 1. IMPORT UserMixin
import enum

from app.models.base_model import BaseModel
from app.core.core_errors import ValidationError

class UserRole(enum.Enum):
    """User role types"""
    ADMIN = "Admin"
    SALES = "Sales"
    MANAGER = "Manager"
    VIEWER = "Viewer"

# 2. INHERIT from UserMixin alongside BaseModel
class User(BaseModel, UserMixin):
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
    
    # Relationship to the Deal model
    deals = relationship('Deal', back_populates='owner')

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

    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role"""
        return self.role.value == role_name

    def is_admin(self) -> bool:
        """Check if user is an admin"""
        return self.role == UserRole.ADMIN

    def is_sales(self) -> bool:
        """Check if user is a sales person"""
        return self.role == UserRole.SALES

    def is_manager(self) -> bool:
        """Check if user is a manager"""
        return self.role == UserRole.MANAGER

    def is_viewer(self) -> bool:
        """Check if user is a viewer"""
        return self.role == UserRole.VIEWER

    def can_manage_users(self) -> bool:
        """Check if user can manage other users"""
        return self.role in [UserRole.ADMIN, UserRole.MANAGER]

    def can_view_admin_panel(self) -> bool:
        """Check if user can access admin panel"""
        return self.role in [UserRole.ADMIN, UserRole.MANAGER]

    def get_role_display_name(self) -> str:
        """Get a user-friendly display name for the role"""
        role_names = {
            UserRole.ADMIN: "Administrator",
            UserRole.SALES: "Sales Representative",
            UserRole.MANAGER: "Manager",
            UserRole.VIEWER: "Viewer"
        }
        return role_names.get(self.role, self.role.value)

    def validate(self) -> None:
        """Custom validation for user data."""
        super().validate()
        
        # Email validation
        if not self.email or '@' not in self.email:
            raise ValidationError("Invalid email format.")
        
        # Username validation
        if not self.username or len(self.username) < 3:
            raise ValidationError("Username must be at least 3 characters long.")
        
        # Role validation
        if not self.role:
            raise ValidationError("User role is required.")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the user instance to a dictionary."""
        data = super().to_dict()
        data['full_name'] = self.full_name
        data['role_display'] = self.get_role_display_name()
        data['can_manage_users'] = self.can_manage_users()
        data['can_view_admin_panel'] = self.can_view_admin_panel()
        return data

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role='{self.role.value}')>"