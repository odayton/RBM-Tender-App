from typing import Dict, List, Optional
from decimal import Decimal
from app.extensions import db
from app.models import AdditionalPriceAdder # Assuming this is your model name
from app.core.core_errors import DatabaseError
from app.core.core_logging import logger # Use central app logger

class AdditionalPriceAdderManager:
    """Manages all additional price adder operations using the SQLAlchemy ORM."""

    @staticmethod
    def validate_adder_data(data: Dict) -> None:
        """Validate price adder data before insertion/update."""
        required_fields = ['ip_adder', 'drip_tray_adder']
        for field in required_fields:
            if field not in data or data.get(field) is None:
                raise ValueError(f"Missing required field: {field}")
            
            try:
                value = Decimal(str(data[field]))
                if value < 0:
                    raise ValueError(f"{field} cannot be negative.")
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid numeric value for {field}: {e}")

    @staticmethod
    def insert_adder(data: Dict) -> AdditionalPriceAdder:
        """Insert a new additional price adder record using the ORM."""
        try:
            AdditionalPriceAdderManager.validate_adder_data(data)
            
            new_adder = AdditionalPriceAdder(**data)
            db.session.add(new_adder)
            db.session.commit()
            
            logger.info(f"Successfully inserted price adder with ID: {new_adder.id}")
            return new_adder
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error inserting additional price adder: {e}", exc_info=True)
            raise DatabaseError(f"Failed to insert additional price adder: {e}")

    @staticmethod
    def fetch_all_adders() -> List[AdditionalPriceAdder]:
        """Fetch all additional price adders."""
        try:
            return AdditionalPriceAdder.query.order_by(AdditionalPriceAdder.id).all()
        except Exception as e:
            logger.error(f"Error fetching all additional price adders: {e}", exc_info=True)
            raise DatabaseError(f"Failed to fetch additional price adders: {e}")

    @staticmethod
    def fetch_adder_by_id(adder_id: int) -> Optional[AdditionalPriceAdder]:
        """Fetch a specific additional price adder by id."""
        try:
            return AdditionalPriceAdder.query.get(adder_id)
        except Exception as e:
            logger.error(f"Error fetching additional price adder ID {adder_id}: {e}", exc_info=True)
            raise DatabaseError(f"Failed to fetch additional price adder: {e}")

    @staticmethod
    def update_adder(adder_id: int, data: Dict) -> Optional[AdditionalPriceAdder]:
        """Update an existing additional price adder."""
        try:
            adder = AdditionalPriceAdder.query.get(adder_id)
            if not adder:
                logger.warning(f"Attempted to update non-existent price adder with ID {adder_id}.")
                return None
            
            # Create a merged dictionary to validate the final state
            merged_data = {
                'ip_adder': adder.ip_adder,
                'drip_tray_adder': adder.drip_tray_adder,
                **data
            }
            AdditionalPriceAdderManager.validate_adder_data(merged_data)

            for key, value in data.items():
                if hasattr(adder, key):
                    setattr(adder, key, value)
            
            db.session.commit()
            logger.info(f"Successfully updated price adder with ID: {adder_id}")
            return adder
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating additional price adder {adder_id}: {e}", exc_info=True)
            raise DatabaseError(f"Failed to update additional price adder: {e}")