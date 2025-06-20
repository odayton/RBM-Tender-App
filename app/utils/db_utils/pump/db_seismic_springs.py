from typing import Dict, List, Optional
from decimal import Decimal
from app.extensions import db
from app.models import SeismicSpring # Assuming this is your model name
from app.core.core_errors import DatabaseError
from app.core.core_logging import logger # Use central app logger

class SeismicSpringDatabaseManager:
    """Manages all seismic spring-related database operations using the SQLAlchemy ORM."""

    @staticmethod
    def validate_seismic_spring_data(data: Dict) -> None:
        """Validate seismic spring data before insertion/update."""
        required_fields = ['part_number', 'name', 'max_load_kg', 'static_deflection', 'spring_constant_kg_mm', 'cost']
        for field in required_fields:
            if field not in data or data.get(field) is None:
                raise ValueError(f"Missing required field: {field}")
        
        numeric_fields = ['max_load_kg', 'static_deflection', 'spring_constant_kg_mm', 'cost']
        for field in numeric_fields:
            try:
                value = Decimal(str(data[field]))
                if value <= 0:
                    raise ValueError(f"{field} must be positive.")
            except (ValueError, TypeError):
                raise ValueError(f"Invalid numeric value for {field}.")

    @staticmethod
    def insert_seismic_spring(data: Dict) -> SeismicSpring:
        """Insert a new seismic spring using the ORM."""
        try:
            SeismicSpringDatabaseManager.validate_seismic_spring_data(data)
            
            new_spring = SeismicSpring(**data)
            db.session.add(new_spring)
            db.session.commit()
            
            logger.info(f"Successfully inserted seismic spring with part number: {new_spring.part_number}")
            return new_spring
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error inserting seismic spring: {e}", exc_info=True)
            if 'unique constraint' in str(e).lower() or 'already exists' in str(e).lower():
                raise DatabaseError(f"Seismic spring with part number {data.get('part_number')} already exists.")
            raise DatabaseError(f"Failed to insert seismic spring: {e}")

    @staticmethod
    def fetch_all_seismic_springs() -> List[SeismicSpring]:
        """Fetch all seismic springs."""
        try:
            return SeismicSpring.query.order_by(SeismicSpring.part_number).all()
        except Exception as e:
            logger.error(f"Error fetching all seismic springs: {e}", exc_info=True)
            raise DatabaseError(f"Failed to fetch all seismic springs: {e}")

    @staticmethod
    def fetch_seismic_spring_by_part_number(part_number: str) -> Optional[SeismicSpring]:
        """Fetch a specific seismic spring by its part number."""
        try:
            return SeismicSpring.query.filter_by(part_number=part_number).first()
        except Exception as e:
            logger.error(f"Error fetching seismic spring '{part_number}': {e}", exc_info=True)
            raise DatabaseError(f"Failed to fetch seismic spring: {e}")

    @staticmethod
    def update_seismic_spring(part_number: str, data: Dict) -> Optional[SeismicSpring]:
        """Update an existing seismic spring."""
        try:
            spring = SeismicSpring.query.filter_by(part_number=part_number).first()
            if not spring:
                logger.warning(f"Attempted to update non-existent seismic spring with part number {part_number}.")
                return None

            # Create a merged dictionary to validate the final state
            merged_data = spring.to_dict() # Assumes a to_dict() method on the model
            merged_data.update(data)
            SeismicSpringDatabaseManager.validate_seismic_spring_data(merged_data)
            
            for key, value in data.items():
                if hasattr(spring, key):
                    setattr(spring, key, value)
            
            db.session.commit()
            logger.info(f"Successfully updated seismic spring with part number: {part_number}")
            return spring
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating seismic spring {part_number}: {e}", exc_info=True)
            raise DatabaseError(f"Failed to update seismic spring: {e}")