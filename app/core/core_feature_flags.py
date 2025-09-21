"""
Core Feature Flags Module - Controlled Rollouts and A/B Testing
"""

import json
import time
import hashlib
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime, timedelta
from flask import request, g, current_app
from flask_sqlalchemy import SQLAlchemy
import structlog

logger = structlog.get_logger(__name__)

class FeatureFlag:
    """Represents a single feature flag configuration."""
    
    def __init__(self, name: str, enabled: bool = False, rollout_percentage: float = 0.0, 
                 conditions: Optional[Dict[str, Any]] = None, description: str = ""):
        self.name = name
        self.enabled = enabled
        self.rollout_percentage = min(100.0, max(0.0, rollout_percentage))
        self.conditions = conditions or {}
        self.description = description
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert feature flag to dictionary."""
        return {
            'name': self.name,
            'enabled': self.enabled,
            'rollout_percentage': self.rollout_percentage,
            'conditions': self.conditions,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FeatureFlag':
        """Create feature flag from dictionary."""
        flag = cls(
            name=data['name'],
            enabled=data['enabled'],
            rollout_percentage=data.get('rollout_percentage', 0.0),
            conditions=data.get('conditions', {}),
            description=data.get('description', '')
        )
        if 'created_at' in data:
            flag.created_at = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data:
            flag.updated_at = datetime.fromisoformat(data['updated_at'])
        return flag

class FeatureFlagManager:
    """Manages feature flags with support for gradual rollouts and conditions."""
    
    def __init__(self, db: Optional[SQLAlchemy] = None):
        self.db = db
        self.flags: Dict[str, FeatureFlag] = {}
        self.conditions: Dict[str, Callable] = {}
        self._init_default_conditions()
        self._load_flags()
    
    def _init_default_conditions(self):
        """Initialize default condition functions."""
        self.conditions = {
            'user_id': self._check_user_id,
            'user_role': self._check_user_role,
            'user_email': self._check_user_email,
            'ip_address': self._check_ip_address,
            'user_agent': self._check_user_agent,
            'time_of_day': self._check_time_of_day,
            'day_of_week': self._check_day_of_week,
            'date_range': self._check_date_range,
            'custom': self._check_custom_condition
        }
    
    def _load_flags(self):
        """Load feature flags from database or configuration."""
        # In a real implementation, this would load from database
        # For now, we'll use a simple in-memory storage
        self._load_default_flags()
    
    def _load_default_flags(self):
        """Load default feature flags."""
        default_flags = [
            {
                'name': 'new_quote_ui',
                'enabled': True,
                'rollout_percentage': 50.0,
                'description': 'New quote generation UI',
                'conditions': {'user_role': 'admin'}
            },
            {
                'name': 'advanced_analytics',
                'enabled': False,
                'rollout_percentage': 25.0,
                'description': 'Advanced analytics dashboard',
                'conditions': {}
            },
            {
                'name': 'real_time_notifications',
                'enabled': True,
                'rollout_percentage': 100.0,
                'description': 'Real-time notification system',
                'conditions': {}
            },
            {
                'name': 'beta_features',
                'enabled': False,
                'rollout_percentage': 10.0,
                'description': 'Beta features for testing',
                'conditions': {'user_role': 'admin'}
            },
            {
                'name': 'enhanced_search',
                'enabled': True,
                'rollout_percentage': 75.0,
                'description': 'Enhanced search functionality',
                'conditions': {}
            },
            {
                'name': 'mobile_optimization',
                'enabled': True,
                'rollout_percentage': 100.0,
                'description': 'Mobile-optimized interface',
                'conditions': {}
            },
            {
                'name': 'api_v2',
                'enabled': False,
                'rollout_percentage': 0.0,
                'description': 'API version 2 endpoints',
                'conditions': {}
            },
            {
                'name': 'advanced_caching',
                'enabled': True,
                'rollout_percentage': 100.0,
                'description': 'Advanced caching strategies',
                'conditions': {}
            }
        ]
        
        for flag_data in default_flags:
            flag = FeatureFlag.from_dict(flag_data)
            self.flags[flag.name] = flag
    
    def is_enabled(self, flag_name: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """Check if a feature flag is enabled for the current context."""
        if flag_name not in self.flags:
            logger.warning("Feature flag not found", flag_name=flag_name)
            return False
        
        flag = self.flags[flag_name]
        
        # If flag is globally disabled, return False
        if not flag.enabled:
            return False
        
        # If rollout percentage is 0, return False
        if flag.rollout_percentage == 0:
            return False
        
        # If rollout percentage is 100, check conditions only
        if flag.rollout_percentage == 100:
            return self._check_conditions(flag, context)
        
        # For partial rollouts, check if user is in the rollout group
        if not self._is_in_rollout_group(flag_name, context):
            return False
        
        # Check conditions
        return self._check_conditions(flag, context)
    
    def _is_in_rollout_group(self, flag_name: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """Check if the current context is in the rollout group."""
        # Use a consistent hash of user identifier for stable rollout assignment
        user_id = self._get_user_identifier(context)
        hash_input = f"{flag_name}:{user_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        rollout_threshold = (hash_value % 100) + 1  # 1-100
        
        flag = self.flags[flag_name]
        return rollout_threshold <= flag.rollout_percentage
    
    def _get_user_identifier(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Get a stable identifier for the current user/context."""
        if context and 'user_id' in context:
            return str(context['user_id'])
        
        # Check if we're in an application context before accessing Flask globals
        try:
            from flask import has_app_context
            if has_app_context():
                # Try to get user ID from Flask context
                if hasattr(g, 'user') and g.user and hasattr(g.user, 'id'):
                    return str(g.user.id)
                
                # Fall back to session ID or IP address
                if hasattr(request, 'session') and request.session:
                    return request.session.get('session_id', 'anonymous')
                
                # Use IP address as last resort
                return request.remote_addr if request else 'unknown'
        except (ImportError, RuntimeError):
            # Not in Flask context or Flask not available
            pass
        
        # Fallback when not in Flask context
        return 'system'
    
    def _check_conditions(self, flag: FeatureFlag, context: Optional[Dict[str, Any]] = None) -> bool:
        """Check if all conditions for a flag are met."""
        if not flag.conditions:
            return True
        
        context = context or {}
        
        for condition_name, condition_value in flag.conditions.items():
            if condition_name not in self.conditions:
                logger.warning("Unknown condition", condition_name=condition_name)
                continue
            
            condition_func = self.conditions[condition_name]
            if not condition_func(condition_value, context):
                return False
        
        return True
    
    def _check_user_id(self, expected_ids: Union[int, List[int]], context: Dict[str, Any]) -> bool:
        """Check if user ID matches expected values."""
        user_id = context.get('user_id')
        if not user_id:
            return False
        
        if isinstance(expected_ids, list):
            return user_id in expected_ids
        return user_id == expected_ids
    
    def _check_user_role(self, expected_roles: Union[str, List[str]], context: Dict[str, Any]) -> bool:
        """Check if user role matches expected values."""
        user_role = context.get('user_role')
        if not user_role:
            return False
        
        if isinstance(expected_roles, list):
            return user_role in expected_roles
        return user_role == expected_roles
    
    def _check_user_email(self, expected_emails: Union[str, List[str]], context: Dict[str, Any]) -> bool:
        """Check if user email matches expected values."""
        user_email = context.get('user_email')
        if not user_email:
            return False
        
        if isinstance(expected_emails, list):
            return user_email in expected_emails
        return user_email == expected_emails
    
    def _check_ip_address(self, expected_ips: Union[str, List[str]], context: Dict[str, Any]) -> bool:
        """Check if IP address matches expected values."""
        ip_address = context.get('ip_address') or (request.remote_addr if request else None)
        if not ip_address:
            return False
        
        if isinstance(expected_ips, list):
            return ip_address in expected_ips
        return ip_address == expected_ips
    
    def _check_user_agent(self, expected_patterns: Union[str, List[str]], context: Dict[str, Any]) -> bool:
        """Check if user agent matches expected patterns."""
        user_agent = context.get('user_agent') or (request.headers.get('User-Agent') if request else None)
        if not user_agent:
            return False
        
        patterns = expected_patterns if isinstance(expected_patterns, list) else [expected_patterns]
        return any(pattern.lower() in user_agent.lower() for pattern in patterns)
    
    def _check_time_of_day(self, time_range: Dict[str, str], context: Dict[str, Any]) -> bool:
        """Check if current time is within specified range."""
        now = datetime.utcnow().time()
        start_time = datetime.strptime(time_range['start'], '%H:%M').time()
        end_time = datetime.strptime(time_range['end'], '%H:%M').time()
        
        if start_time <= end_time:
            return start_time <= now <= end_time
        else:  # Crosses midnight
            return now >= start_time or now <= end_time
    
    def _check_day_of_week(self, expected_days: Union[int, List[int]], context: Dict[str, Any]) -> bool:
        """Check if current day of week matches expected values (0=Monday, 6=Sunday)."""
        current_day = datetime.utcnow().weekday()
        
        if isinstance(expected_days, list):
            return current_day in expected_days
        return current_day == expected_days
    
    def _check_date_range(self, date_range: Dict[str, str], context: Dict[str, Any]) -> bool:
        """Check if current date is within specified range."""
        now = datetime.utcnow().date()
        start_date = datetime.strptime(date_range['start'], '%Y-%m-%d').date()
        end_date = datetime.strptime(date_range['end'], '%Y-%m-%d').date()
        
        return start_date <= now <= end_date
    
    def _check_custom_condition(self, condition_func: Callable, context: Dict[str, Any]) -> bool:
        """Check custom condition function."""
        try:
            return condition_func(context)
        except Exception as e:
            logger.error("Custom condition check failed", error=str(e))
            return False
    
    def add_flag(self, flag: FeatureFlag) -> bool:
        """Add a new feature flag."""
        try:
            self.flags[flag.name] = flag
            logger.info("Feature flag added", flag_name=flag.name)
            return True
        except Exception as e:
            logger.error("Failed to add feature flag", flag_name=flag.name, error=str(e))
            return False
    
    def update_flag(self, flag_name: str, **kwargs) -> bool:
        """Update an existing feature flag."""
        if flag_name not in self.flags:
            logger.warning("Feature flag not found for update", flag_name=flag_name)
            return False
        
        try:
            flag = self.flags[flag_name]
            for key, value in kwargs.items():
                if hasattr(flag, key):
                    setattr(flag, key, value)
            flag.updated_at = datetime.utcnow()
            logger.info("Feature flag updated", flag_name=flag_name, updates=kwargs)
            return True
        except Exception as e:
            logger.error("Failed to update feature flag", flag_name=flag_name, error=str(e))
            return False
    
    def remove_flag(self, flag_name: str) -> bool:
        """Remove a feature flag."""
        if flag_name not in self.flags:
            logger.warning("Feature flag not found for removal", flag_name=flag_name)
            return False
        
        try:
            del self.flags[flag_name]
            logger.info("Feature flag removed", flag_name=flag_name)
            return True
        except Exception as e:
            logger.error("Failed to remove feature flag", flag_name=flag_name, error=str(e))
            return False
    
    def get_flag(self, flag_name: str) -> Optional[FeatureFlag]:
        """Get a feature flag by name."""
        return self.flags.get(flag_name)
    
    def get_all_flags(self) -> List[FeatureFlag]:
        """Get all feature flags."""
        return list(self.flags.values())
    
    def get_enabled_flags(self, context: Optional[Dict[str, Any]] = None) -> List[str]:
        """Get all enabled feature flags for the current context."""
        enabled_flags = []
        for flag_name in self.flags:
            if self.is_enabled(flag_name, context):
                enabled_flags.append(flag_name)
        return enabled_flags
    
    def add_custom_condition(self, name: str, condition_func: Callable):
        """Add a custom condition function."""
        self.conditions[name] = condition_func
        logger.info("Custom condition added", condition_name=name)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get feature flag statistics."""
        total_flags = len(self.flags)
        enabled_flags = sum(1 for flag in self.flags.values() if flag.enabled)
        
        return {
            'total_flags': total_flags,
            'enabled_flags': enabled_flags,
            'disabled_flags': total_flags - enabled_flags,
            'flags': [flag.to_dict() for flag in self.flags.values()]
        }

# Global feature flag manager
feature_flags = FeatureFlagManager()

# Decorator for feature flag checks
def feature_flag(flag_name: str, context_func: Optional[Callable] = None):
    """Decorator to check feature flags before executing functions."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Get context for feature flag evaluation
            context = None
            if context_func:
                context = context_func()
            elif hasattr(g, 'user') and g.user:
                context = {
                    'user_id': g.user.id,
                    'user_role': g.user.roles[0].name if g.user.roles else 'user',
                    'user_email': g.user.email
                }
            
            # Check if feature flag is enabled
            if not feature_flags.is_enabled(flag_name, context):
                logger.info("Feature flag disabled", flag_name=flag_name, function=func.__name__)
                return None  # or raise an exception, depending on your needs
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Utility functions
def is_feature_enabled(flag_name: str, context: Optional[Dict[str, Any]] = None) -> bool:
    """Check if a feature flag is enabled."""
    return feature_flags.is_enabled(flag_name, context)

def get_enabled_features(context: Optional[Dict[str, Any]] = None) -> List[str]:
    """Get all enabled feature flags for the current context."""
    return feature_flags.get_enabled_flags(context)

def init_feature_flags(app):
    """Initialize feature flags with Flask app."""
    # This would typically load flags from database
    logger.info("Feature flags system initialized", 
                total_flags=len(feature_flags.flags))

# Feature flag management endpoints (for admin interface)
def get_feature_flag_stats():
    """Get feature flag statistics for admin dashboard."""
    return feature_flags.get_stats()

def update_feature_flag(flag_name: str, **kwargs):
    """Update a feature flag (admin function)."""
    return feature_flags.update_flag(flag_name, **kwargs)

def create_feature_flag(name: str, enabled: bool = False, rollout_percentage: float = 0.0, 
                       conditions: Optional[Dict[str, Any]] = None, description: str = ""):
    """Create a new feature flag (admin function)."""
    flag = FeatureFlag(name, enabled, rollout_percentage, conditions, description)
    return feature_flags.add_flag(flag)


