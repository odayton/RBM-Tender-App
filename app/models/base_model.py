from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Session
from app.core.core_errors import ValidationError, DatabaseError
from app.app_extensions import db

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
        """Generate default tablename from class name"""
        return cls.__name__.lower()

    def save(self) -> None:
        """
        Save instance to database.
        Raises:
            DatabaseError: If save operation fails
        """
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise DatabaseError("save", str(e))

    def update(self, data: Dict[str, Any]) -> None:
        """
        Update instance with provided data
        Args:
            data: Dictionary of attributes to update
        Raises:
            ValidationError: If validation fails
            DatabaseError: If update operation fails
        """
        try:
            for key, value in data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            
            self.validate()
            db.session.commit()
        except ValidationError:
            db.session.rollback()
            raise
        except Exception as e:
            db.session.rollback()
            raise DatabaseError("update", str(e))

    def delete(self) -> None:
        """
        Delete instance from database
        Raises:
            DatabaseError: If delete operation fails
        """
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise DatabaseError("delete", str(e))

    @classmethod
    def get_by_id(cls, id: int) -> Optional['BaseModel']:
        """Get model instance by ID"""
        return cls.query.get(id)

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            
            # Format datetime objects
            if isinstance(value, datetime):
                value = value.isoformat()
                
            result[column.name] = value
            
        return result

    def validate(self) -> None:
        """
        Basic validation of required fields.
        Override in subclasses for model-specific validation.
        Raises:
            ValidationError: If validation fails
        """
        for column in self.__table__.columns:
            if not column.nullable and getattr(self, column.name) is None:
                raise ValidationError(f"Field '{column.name}' cannot be null")

    def __repr__(self) -> str:
        """String representation of model instance"""
        return f"<{self.__class__.__name__}(id={self.id})>"