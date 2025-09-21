"""
Secrets Management Module for RBM Tender App

This module provides secure secrets management including:
- Environment variable validation
- Secret key generation
- Sensitive data encryption/decryption
- Secrets rotation capabilities
"""

import os
import secrets
import base64
import hashlib
from typing import Optional, Dict, Any, List
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from app.core.core_logging import logger


class SecretsManager:
    """Secure secrets management for the application."""
    
    def __init__(self):
        self._encryption_key = None
        self._fernet = None
        self._initialize_encryption()
    
    def _initialize_encryption(self):
        """Initialize encryption for sensitive data."""
        try:
            # Use SECRET_KEY as base for encryption key derivation
            secret_key = os.environ.get('SECRET_KEY')
            if not secret_key:
                logger.warning("SECRET_KEY not found. Encryption disabled.")
                return
            
            # Derive encryption key from SECRET_KEY
            salt = b'rbm_tender_app_salt'  # In production, use random salt
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(secret_key.encode()))
            self._fernet = Fernet(key)
            logger.info("Secrets encryption initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            self._fernet = None
    
    def generate_secret_key(self, length: int = 32) -> str:
        """Generate a cryptographically secure secret key."""
        return secrets.token_urlsafe(length)
    
    def generate_api_key(self, prefix: str = "rbm") -> str:
        """Generate a secure API key with prefix."""
        random_part = secrets.token_urlsafe(24)
        return f"{prefix}_{random_part}"
    
    def encrypt_sensitive_data(self, data: str) -> Optional[str]:
        """Encrypt sensitive data."""
        if not self._fernet:
            logger.warning("Encryption not available. Returning plain text.")
            return data
        
        try:
            encrypted_data = self._fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Failed to encrypt data: {e}")
            return None
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> Optional[str]:
        """Decrypt sensitive data."""
        if not self._fernet:
            logger.warning("Encryption not available. Returning encrypted data.")
            return encrypted_data
        
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self._fernet.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt data: {e}")
            return None
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> Dict[str, str]:
        """Hash a password with salt."""
        if not salt:
            salt = secrets.token_hex(16)
        
        # Use PBKDF2 for password hashing
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt.encode(),
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        
        return {
            'hash': key.decode(),
            'salt': salt
        }
    
    def verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """Verify a password against stored hash."""
        try:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt.encode(),
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            return key.decode() == stored_hash
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False


class EnvironmentValidator:
    """Validates and manages environment variables."""
    
    # Critical secrets that must be set
    CRITICAL_SECRETS = [
        'SECRET_KEY',
        'DATABASE_URL',
        ]
    
    # Sensitive secrets that should be encrypted
    SENSITIVE_SECRETS = [
        'DATABASE_URL',
        'DEV_DATABASE_URL',
        'TEST_DATABASE_URL',
        'SMTP_PASSWORD',
        'REDIS_URL'
    ]
    
    # Optional secrets with defaults
    OPTIONAL_SECRETS = {
        'LOG_LEVEL': 'INFO',
        'SECURITY_MAX_LOGIN_ATTEMPTS': '10',
        'SECURITY_BLOCK_DURATION_MINUTES': '15',
        'SESSION_TIMEOUT_HOURS': '8',
        'CACHE_DEFAULT_TIMEOUT': '300'
    }
    
    @classmethod
    def validate_environment(cls) -> Dict[str, Any]:
        """Validate all environment variables."""
        validation_result = {
            'valid': True,
            'missing_critical': [],
            'missing_optional': [],
            'warnings': [],
            'recommendations': []
        }
        
        # Check critical secrets
        for secret in cls.CRITICAL_SECRETS:
            if not os.environ.get(secret):
                validation_result['missing_critical'].append(secret)
                validation_result['valid'] = False
        
        # Check optional secrets
        for secret, default_value in cls.OPTIONAL_SECRETS.items():
            if not os.environ.get(secret):
                validation_result['missing_optional'].append(secret)
                validation_result['recommendations'].append(
                    f"Set {secret}={default_value} for optimal configuration"
                )
        
        # Security recommendations
        if os.environ.get('FLASK_ENV') == 'production':
            if not os.environ.get('SECRET_KEY') or len(os.environ.get('SECRET_KEY', '')) < 32:
                validation_result['warnings'].append(
                    "SECRET_KEY should be at least 32 characters for production"
                )
            
            if os.environ.get('DEBUG', '').lower() == 'true':
                validation_result['warnings'].append(
                    "DEBUG should be False in production"
                )
        
        return validation_result
    
    @classmethod
    def get_secure_config(cls) -> Dict[str, Any]:
        """Get configuration with secrets properly handled."""
        config = {}
        
        # Handle sensitive secrets
        secrets_manager = SecretsManager()
        
        for secret in cls.SENSITIVE_SECRETS:
            value = os.environ.get(secret)
            if value:
                # In production, you might want to encrypt these
                config[secret] = value
        
        # Handle other secrets
        for secret in cls.CRITICAL_SECRETS + list(cls.OPTIONAL_SECRETS.keys()):
            if secret not in cls.SENSITIVE_SECRETS:
                config[secret] = os.environ.get(secret, cls.OPTIONAL_SECRETS.get(secret))
        
        return config
    
    @classmethod
    def generate_missing_secrets(cls) -> Dict[str, str]:
        """Generate missing secrets."""
        secrets_manager = SecretsManager()
        generated = {}
        
        # Generate SECRET_KEY if missing
        if not os.environ.get('SECRET_KEY'):
            generated['SECRET_KEY'] = secrets_manager.generate_secret_key(64)
        
        # Generate API keys if needed
        if not os.environ.get('API_KEY'):
            generated['API_KEY'] = secrets_manager.generate_api_key()
        
        return generated


# Global instances
secrets_manager = SecretsManager()
env_validator = EnvironmentValidator()


def validate_secrets() -> bool:
    """Validate all secrets and return True if valid."""
    result = env_validator.validate_environment()
    
    if not result['valid']:
        logger.error(f"Critical secrets missing: {result['missing_critical']}")
        return False
    
    if result['warnings']:
        for warning in result['warnings']:
            logger.warning(warning)
    
    if result['recommendations']:
        for rec in result['recommendations']:
            logger.info(f"Recommendation: {rec}")
    
    return True


def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get a secret value from environment."""
    return os.environ.get(key, default)


def set_secret(key: str, value: str, encrypt: bool = False) -> bool:
    """Set a secret value (for testing/development only)."""
    try:
        if encrypt and secrets_manager._fernet:
            encrypted_value = secrets_manager.encrypt_sensitive_data(value)
            if encrypted_value:
                os.environ[key] = encrypted_value
            else:
                os.environ[key] = value
        else:
            os.environ[key] = value
        return True
    except Exception as e:
        logger.error(f"Failed to set secret {key}: {e}")
        return False

