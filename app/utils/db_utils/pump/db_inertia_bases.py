from typing import Dict, List, Optional
from decimal import Decimal
from sqlalchemy import func
from app.extensions import db
from app.models import InertiaBase, InertiaBaseUsage # Assuming these are your model names
from app.core.core_errors import DatabaseError
from app.core.core_logging import logger # Use central app logger

class InertiaDatabaseManager:
    """Manages all inertia base-related database operations using the SQLAlchemy ORM."""

    @staticmethod
    def validate_inertia_base_data(data: Dict) -> None:
        """Validate inertia base data before insertion/update."""
        required_fields = ['part_number', 'name', 'length', 'width', 'height', 'spring_mount_height', 'weight', 'spring_amount', 'cost']
        for field in required_fields:
            if field not in data or data.get(field) is None:
                raise ValueError(f"Missing required field: {field}")
        
        # Further validation for numeric types can be added here if needed

    @staticmethod
    def insert_inertia_base(data: Dict) -> InertiaBase:
        """Insert a new inertia base using the ORM."""
        try:
            InertiaDatabaseManager.validate_inertia_base_data(data)
            
            new_base = InertiaBase(**data)
            db.session.add(new_base)
            db.session.commit()
            
            logger.info(f"Successfully inserted inertia base with part number: {new_base.part_number}")
            return new_base
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error inserting inertia base: {e}", exc_info=True)
            if 'unique constraint' in str(e).lower() or 'already exists' in str(e).lower():
                raise DatabaseError(f"Inertia base with part number {data.get('part_number')} already exists.")
            raise DatabaseError(f"Failed to insert inertia base: {e}")

    @staticmethod
    def fetch_all_inertia_bases(include_inactive: bool = False) -> List[InertiaBase]:
        """Fetch all inertia bases, optionally including inactive ones."""
        try:
            query = InertiaBase.query
            if not include_inactive:
                query = query.filter(InertiaBase.status == 'active')
            return query.order_by(InertiaBase.part_number).all()
        except Exception as e:
            logger.error(f"Error fetching all inertia bases: {e}", exc_info=True)
            raise DatabaseError(f"Failed to fetch inertia bases: {e}")

    @staticmethod
    def fetch_inertia_base_by_part_number(part_number: str) -> Optional[InertiaBase]:
        """Fetch a specific inertia base by its part number."""
        try:
            # Use options to eagerly load usage history to prevent N+1 queries
            return InertiaBase.query.options(
                db.joinedload(InertiaBase.usage_history)
            ).filter_by(part_number=part_number).first()
        except Exception as e:
            logger.error(f"Error fetching inertia base '{part_number}': {e}", exc_info=True)
            raise DatabaseError(f"Failed to fetch inertia base: {e}")

    @staticmethod
    def find_suitable_inertia_base(requirements: Dict) -> Optional[InertiaBase]:
        """Find the best-fit inertia base based on requirements using the ORM."""
        try:
            weight_with_margin = Decimal(str(requirements['weight'])) * Decimal('1.2')
            length_with_margin = Decimal(str(requirements['length'])) * Decimal('1.1')
            width_with_margin = Decimal(str(requirements['width'])) * Decimal('1.1')
            min_springs = requirements.get('min_spring_amount', 4)

            # Order by the sum of differences to find the "closest" fit
            best_fit_ordering = (
                func.abs(InertiaBase.weight - weight_with_margin) +
                func.abs(InertiaBase.length - length_with_margin) +
                func.abs(InertiaBase.width - width_with_margin)
            ).asc()
            
            return InertiaBase.query.filter(
                InertiaBase.status == 'active',
                InertiaBase.weight >= weight_with_margin,
                InertiaBase.length >= length_with_margin,
                InertiaBase.width >= width_with_margin,
                InertiaBase.spring_amount >= min_springs
            ).order_by(best_fit_ordering).first()

        except Exception as e:
            logger.error(f"Error finding suitable inertia base: {e}", exc_info=True)
            raise DatabaseError(f"Failed to find suitable inertia base: {e}")

    @staticmethod
    def record_inertia_base_usage(**usage_data) -> InertiaBaseUsage:
        """Record usage of an inertia base."""
        try:
            new_usage = InertiaBaseUsage(**usage_data)
            db.session.add(new_usage)
            db.session.commit()
            logger.info(f"Recorded usage for inertia base {usage_data.get('part_number')} on deal {usage_data.get('deal_id')}")
            return new_usage
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error recording inertia base usage: {e}", exc_info=True)
            raise DatabaseError(f"Failed to record inertia base usage: {e}")