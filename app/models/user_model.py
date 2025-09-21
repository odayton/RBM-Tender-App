import secrets
import string
from typing import Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy import Column, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import enum

from app.models.base_model import BaseModel
from app.core.core_errors import ValidationError

class UserRole(enum.Enum):
    """User role types"""
    ADMIN = "Admin"
    SALES = "Sales"
    MANAGER = "Manager"
    VIEWER = "Viewer"

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
    force_password_change = Column(Boolean, default=False)
    
    # Two-Factor Authentication (2FA)
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(32), nullable=True)  # Base32 secret for TOTP
    backup_codes = Column(String(500), nullable=True)  # JSON string of backup codes
    
    # Additional fields for better user management (commented out until database is updated)
    # employee_id = Column(String(20), unique=True, nullable=True)
    # department = Column(String(100), nullable=True)
    # manager_id = Column(String(50), nullable=True)  # Reference to manager's employee_id
    # hire_date = Column(DateTime, nullable=True)
    # notes = Column(String(500), nullable=True)
    
    # Relationship to the Deal model
    deals = relationship('Deal', back_populates='owner')
    
    # CRM Relationships
    activities = relationship('Activity', back_populates='user')
    assigned_tasks = relationship('Task', foreign_keys='Task.assigned_to_id', back_populates='assigned_to')
    created_tasks = relationship('Task', foreign_keys='Task.created_by_id', back_populates='created_by')

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

    @staticmethod
    def generate_temporary_password(length: int = 12) -> str:
        """Generate a secure temporary password"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def set_temporary_password(self) -> str:
        """Set a temporary password and force change on next login"""
        temp_password = self.generate_temporary_password()
        self.password = temp_password
        self.force_password_change = True
        return temp_password

    def needs_password_change(self) -> bool:
        """Check if user needs to change their password"""
        return self.force_password_change

    def mark_password_changed(self) -> None:
        """Mark that the user has changed their password"""
        self.force_password_change = False

    def update_last_login(self) -> None:
        """Update the last login timestamp"""
        self.last_login = datetime.utcnow()

    def get_active_deals(self) -> List['Deal']:
        """Get all active deals owned by this user"""
        from .deals.deal_types import DealStage
        active_stages = [DealStage.SALES_LEAD, DealStage.TENDER, DealStage.PROPOSAL, DealStage.NEGOTIATION]
        return [deal for deal in self.deals if deal.stage in active_stages and deal.is_active]

    def get_closed_deals(self) -> List['Deal']:
        """Get all closed deals owned by this user"""
        from .deals.deal_types import DealStage
        closed_stages = [DealStage.CLOSED_WON, DealStage.CLOSED_LOST]
        return [deal for deal in self.deals if deal.stage in closed_stages]

    def get_deal_statistics(self) -> Dict[str, Any]:
        """Get comprehensive deal statistics for this user"""
        active_deals = self.get_active_deals()
        closed_deals = self.get_closed_deals()
        won_deals = [deal for deal in closed_deals if deal.stage.value == 'CLOSED_WON']
        
        total_active_value = sum(deal.total_amount for deal in active_deals)
        total_won_value = sum(deal.total_amount for deal in won_deals)
        
        return {
            'total_deals': len(self.deals),
            'active_deals': len(active_deals),
            'closed_deals': len(closed_deals),
            'won_deals': len(won_deals),
            'closed_won_deals': len(won_deals),  # Alias for compatibility
            'lost_deals': len(closed_deals) - len(won_deals),
            'total_active_value': float(total_active_value),
            'total_won_value': float(total_won_value),
            'win_rate': (len(won_deals) / len(closed_deals) * 100) if closed_deals else 0
        }

    def get_recent_activity(self, days: int = 30) -> List['Deal']:
        """Get deals that have been updated recently"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return [deal for deal in self.deals if deal.updated_at >= cutoff_date]

    def is_recently_active(self, days: int = 7) -> bool:
        """Check if user has been active recently"""
        if not self.last_login:
            return False
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return self.last_login >= cutoff_date

    def get_team_members(self) -> List['User']:
        """Get team members if user is a manager"""
        if not self.is_manager():
            return []
        
        from app.extensions import db
        return User.query.filter(
            User.manager_id == self.employee_id,
            User.is_active == True
        ).all()

    def validate(self) -> bool:
        """Custom validation for user data."""
        try:
            super().validate()
            
            # Email validation
            if not self.email or '@' not in self.email:
                return False
            
            # Username validation
            if not self.username or len(self.username) < 3:
                return False
            
            # Role validation
            if not self.role:
                return False
            
            # Employee ID validation (commented out until field is enabled)
            # if self.employee_id and len(self.employee_id.strip()) < 2:
            #     return False
            
            return True
        except Exception:
            return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert the user instance to a dictionary."""
        data = super().to_dict()
        data['full_name'] = self.full_name
        data['role_display'] = self.get_role_display_name()
        data['can_manage_users'] = self.can_manage_users()
        data['can_view_admin_panel'] = self.can_view_admin_panel()
        data['deal_statistics'] = self.get_deal_statistics()
        data['is_recently_active'] = self.is_recently_active()
        return data

    # Two-Factor Authentication Methods
    def setup_two_factor(self) -> str:
        """Setup 2FA for the user and return the secret"""
        secret = self.generate_2fa_secret()
        self.generate_backup_codes()
        return secret
    
    def generate_2fa_secret(self) -> str:
        """Generate a new 2FA secret for the user"""
        import pyotp
        secret = pyotp.random_base32()
        self.two_factor_secret = secret
        return secret
    
    def get_2fa_qr_code_url(self) -> str:
        """Get the QR code URL for 2FA setup"""
        if not self.two_factor_secret:
            return None
        
        import pyotp
        totp = pyotp.TOTP(self.two_factor_secret)
        return totp.provisioning_uri(
            name=self.email,
            issuer_name="RBM Tender App"
        )
    
    def verify_2fa_code(self, code: str) -> bool:
        """Verify a 2FA code"""
        if not self.two_factor_enabled or not self.two_factor_secret:
            return False
        
        import pyotp
        totp = pyotp.TOTP(self.two_factor_secret)
        return totp.verify(code, valid_window=1)  # Allow 1 time step tolerance
    
    def generate_backup_codes(self) -> List[str]:
        """Generate backup codes for 2FA"""
        import json
        codes = [secrets.token_hex(4).upper() for _ in range(10)]
        self.backup_codes = json.dumps(codes)
        return codes
    
    def verify_backup_code(self, code: str) -> bool:
        """Verify a backup code and remove it if valid"""
        if not self.backup_codes:
            return False
        
        import json
        try:
            codes = json.loads(self.backup_codes)
            if code.upper() in codes:
                codes.remove(code.upper())
                self.backup_codes = json.dumps(codes) if codes else None
                return True
        except (json.JSONDecodeError, ValueError):
            pass
        
        return False
    
    def enable_2fa(self) -> bool:
        """Enable 2FA for the user (requires secret to be set)"""
        if self.two_factor_secret:
            self.two_factor_enabled = True
            return True
        return False
    
    def disable_2fa(self):
        """Disable 2FA for the user"""
        self.two_factor_enabled = False
        self.two_factor_secret = None
        self.backup_codes = None
    
    def verify_two_factor(self, code: str) -> bool:
        """Verify a 2FA code and enable 2FA if not already enabled"""
        if not self.two_factor_secret:
            return False
        
        import pyotp
        totp = pyotp.TOTP(self.two_factor_secret)
        is_valid = totp.verify(code, valid_window=1)
        
        if is_valid and not self.two_factor_enabled:
            self.two_factor_enabled = True
        
        return is_valid
    
    def get_qr_code(self) -> str:
        """Get the QR code URL for 2FA setup"""
        return self.get_2fa_qr_code_url()

    def __repr__(self) -> str:
        return f"<User {self.username}>"