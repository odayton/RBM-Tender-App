"""
Core Forms Module - Custom form base classes to handle application context issues
"""

from flask_wtf import FlaskForm as BaseFlaskForm
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class FlaskForm(BaseFlaskForm):
    """
    Custom FlaskForm that handles application context issues gracefully.
    
    This form class overrides the problematic methods to prevent RuntimeError
    when no application context is available.
    """
    
    class Meta(BaseFlaskForm.Meta):
        """Custom Meta class to handle Flask-WTF configuration safely."""
        
        @property
        def csrf(self):
            """
            Override csrf property to handle missing application context.
            
            This prevents the RuntimeError that occurs when Flask-WTF tries
            to access current_app.config during form initialization outside
            of an application context.
            """
            try:
                # Try to access current_app normally
                return current_app.config.get("WTF_CSRF_ENABLED", True)
            except RuntimeError as e:
                if "Working outside of application context" in str(e):
                    # Log the issue but don't fail - default to False for safety
                    logger.debug("Form initialized outside application context, disabling CSRF")
                    return False
                else:
                    # Re-raise other RuntimeErrors
                    raise
            except Exception as e:
                # Log other exceptions but don't fail - default to False for safety
                logger.warning(f"Error checking CSRF setting: {e}")
                return False
        
        def get_translations(self, form):
            """
            Override get_translations to handle missing application context.
            
            This prevents the RuntimeError that occurs when Flask-WTF tries
            to access current_app.config during form initialization outside
            of an application context.
            """
            try:
                # Try to access current_app normally
                if not current_app.config.get("WTF_I18N_ENABLED", True):
                    return None
                return super().get_translations(form)
            except RuntimeError as e:
                if "Working outside of application context" in str(e):
                    # Log the issue but don't fail
                    logger.debug("Form initialized outside application context, skipping translations")
                    return None
                else:
                    # Re-raise other RuntimeErrors
                    raise
            except Exception as e:
                # Log other exceptions but don't fail
                logger.warning(f"Error getting form translations: {e}")
                return None
