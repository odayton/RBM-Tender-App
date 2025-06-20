from typing import Dict, List, Optional
from decimal import Decimal
from app.extensions import db
from app.models import RubberMount # Changed from RubberMounts (plural) to singular
from app.core.core_errors import DatabaseError
from app.core.core_logging import logger

class RubberMountDatabaseManager:
    """Manages all rubber mount-related database operations using the SQLAlchemy ORM."""

    @staticmethod
    def validate_rubber_mount_data(data: Dict) -> None:
        """Validate rubber mount data before insertion/update."""
        required_fields = ['part_number', 'name', 'weight', 'cost']
        for field in required_fields:
            if field not in data or data.get(field) is None:
                raise ValueError(f"Missing required field: {field}")
        
        for field in ['weight', 'cost']:
            try:
                value = Decimal(str(data[field]))
                if value <= 0:
                    raise ValueError(f"{field} must be positive.")
            except (ValueError, TypeError):
                raise ValueError(f"Invalid numeric value for {field}.")

    @staticmethod
    def insert_rubber_mount(data: Dict) -> RubberMount:
        """Insert a new rubber mount using the ORM."""
        try:
            RubberMountDatabaseManager.validate_rubber_mount_data(data)
            
            new_mount = RubberMount(**data) # Use singular name
            db.session.add(new_mount)
            db.session.commit()
            
            logger.info(f"Successfully inserted rubber mount with part number: {new_mount.part_number}")
            return new_mount
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error inserting rubber mount: {e}", exc_info=True)
            if 'unique constraint' in str(e).lower() or 'already exists' in str(e).lower():
                raise DatabaseError(f"Rubber mount with part number {data.get('part_number')} already exists.")
            raise DatabaseError(f"Failed to insert rubber mount: {e}")

    @staticmethod
    def fetch_all_rubber_mounts() -> List[RubberMount]:
        """Fetch all rubber mounts."""
        try:
            return RubberMount.query.order_by(RubberMount.part_number).all() # Use singular name
        except Exception as e:
            logger.error(f"Error fetching all rubber mounts: {e}", exc_info=True)
            raise DatabaseError(f"Failed to fetch all rubber mounts: {e}")

    @staticmethod
    def fetch_rubber_mount_by_part_number(part_number: str) -> Optional[RubberMount]:
        """Fetch a specific rubber mount by its part number."""
        try:
            return RubberMount.query.filter_by(part_number=part_number).first() # Use singular name
        except Exception as e:
            logger.error(f"Error fetching rubber mount '{part_number}': {e}", exc_info=True)
            raise DatabaseError(f"Failed to fetch rubber mount: {e}")

    @staticmethod
    def update_rubber_mount(part_number: str, data: Dict) -> Optional[RubberMount]:
        """Update an existing rubber mount."""
        try:
            mount = RubberMount.query.filter_by(part_number=part_number).first() # Use singular name
            if not mount:
                logger.warning(f"Attempted to update non-existent rubber mount with part number {part_number}.")
                return None

            merged_data = mount.to_dict()
            merged_data.update(data)
            RubberMountDatabaseManager.validate_rubber_mount_data(merged_data)
            
            for key, value in data.items():
                if hasattr(mount, key):
                    setattr(mount, key, value)
            
            db.session.commit()
            logger.info(f"Successfully updated rubber mount with part number: {part_number}")
            return mount
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating rubber mount {part_number}: {e}", exc_info=True)
            raise DatabaseError(f"Failed to update rubber mount: {e}")