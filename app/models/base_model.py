from typing import Any, Dict, Optional
from datetime import datetime, date
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declared_attr
from decimal import Decimal

from app.extensions import db # Corrected import
from app.core.core_errors import ValidationError, DatabaseError

class BaseModel(db.Model):
    """
    Base model class providing common attributes and methods for all models.
    Inherits from Flask-SQLAlchemy's db.Model.
    """
    __abstract__ = True

    # Primary key
    id = Column(Integer, primary_key=True)
    
    # Tracking fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    @declared_attr
    def __tablename__(cls) -> str:
        """Generate a default table name from the class name."""
        # Converts "UserModel" to "user_model"
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def save(self) -> None:
        """
        Save the current instance to the database.
        Raises:
            DatabaseError: If the save operation fails.
        """
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to save {self.__class__.__name__}: {e}")

    def update(self, **kwargs) -> None:
        """
        Update the instance with provided data from keyword arguments.
        Args:
            **kwargs: Keyword arguments corresponding to model attributes.
        Raises:
            ValidationError: If validation fails.
            DatabaseError: If the update operation fails.
        """
        try:
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            
            self.validate()
            db.session.commit()
        except ValidationError:
            db.session.rollback()
            raise
        except Exception as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to update {self.__class__.__name__}: {e}")

    def delete(self) -> None:
        """
        Delete the instance from the database.
        Raises:
            DatabaseError: If the delete operation fails.
        """
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to delete {self.__class__.__name__}: {e}")

    @classmethod
    def get_by_id(cls, record_id: int) -> Optional['BaseModel']:
        """Get a model instance by its primary key."""
        return cls.query.get(record_id)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the model instance to a dictionary."""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            
            if isinstance(value, (datetime, date)):
                value = value.isoformat()
            elif isinstance(value, Decimal):
                value = str(value)
                
            result[column.name] = value
        return result

    def validate(self) -> None:
        """
        Basic validation. Override in subclasses for model-specific validation.
        Raises:
            ValidationError: If validation fails.
        """
        for column in self.__table__.columns:
            if not column.nullable and getattr(self, column.name) is None:
                if not column.primary_key: # Primary keys are often generated on commit
                    raise ValidationError(f"Field '{column.name}' cannot be null.")

    def __repr__(self) -> str:
        """String representation of the model instance."""
        return f"<{self.__class__.__name__}(id={self.id})>"