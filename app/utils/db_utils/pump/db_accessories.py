from typing import Dict, List, Optional, Type
from decimal import Decimal
from app.extensions import db
from app.models import (
    Pump, InertiaBase, SeismicSpring, RubberMounts, Base,
    pump_inertia_base_association, pump_seismic_spring_association, pump_rubber_mount_association
)
from app.core.core_errors import DatabaseError
from app.core.core_logging import logger

class PumpAccessoryManager:
    """Manages pump accessory relationships and queries using the SQLAlchemy ORM."""

    # A mapping from string identifiers to the actual Model classes
    ACCESSORY_MODELS: Dict[str, Type[Base]] = {
        'inertia_base': InertiaBase,
        'seismic_spring': SeismicSpring,
        'rubber_mount': RubberMounts
    }

    @staticmethod
    def fetch_accessory_options(accessory_type: str) -> List[Dict]:
        """
        Fetch available accessories by type using the ORM.
        accessory_type: 'inertia_base', 'seismic_spring', or 'rubber_mount'
        """
        logger.debug(f"Fetching accessory options for type: {accessory_type}")
        try:
            model = PumpAccessoryManager.ACCESSORY_MODELS.get(accessory_type)
            if not model:
                raise ValueError(f"Invalid accessory type specified: {accessory_type}")
            
            # Assuming models have a 'part_number' and 'name' attribute
            results = model.query.order_by(model.part_number).all()
            # Convert to list of dicts for consistent return type
            return [
                {'part_number': r.part_number, 'name': r.name, 'cost': r.cost} 
                for r in results
            ]
        except Exception as e:
            logger.error(f"Error fetching accessory options for '{accessory_type}': {e}", exc_info=True)
            raise DatabaseError(f"Failed to fetch accessory options: {e}")

    @staticmethod
    def fetch_accessory_cost(part_number: str) -> Optional[Decimal]:
        """Fetch the cost of a specific accessory by querying all accessory tables."""
        logger.debug(f"Fetching cost for accessory part number: {part_number}")
        try:
            for model in PumpAccessoryManager.ACCESSORY_MODELS.values():
                accessory = model.query.filter_by(part_number=part_number).first()
                if accessory and hasattr(accessory, 'cost'):
                    return accessory.cost
            return None # Not found in any accessory table
        except Exception as e:
            logger.error(f"Error fetching accessory cost for '{part_number}': {e}", exc_info=True)
            raise DatabaseError(f"Failed to fetch accessory cost: {e}")

    @staticmethod
    def get_compatible_accessories(pump_sku: str) -> Dict[str, List[Dict]]:
        """Get all compatible accessories for a specific pump using the ORM."""
        logger.info(f"Fetching compatible accessories for pump SKU: {pump_sku}")
        try:
            pump = Pump.query.filter_by(sku=pump_sku).first()
            if not pump:
                raise DatabaseError(f"Pump with SKU {pump_sku} not found")

            # 20% safety margin for weight calculations
            required_weight_capacity = pump.weight * Decimal('1.2')

            # Get compatible inertia bases
            bases = InertiaBase.query.filter(
                InertiaBase.length >= pump.length,
                InertiaBase.width >= pump.width,
                InertiaBase.weight >= required_weight_capacity
            ).order_by(InertiaBase.cost.asc()).all()

            # Get compatible seismic springs
            springs = SeismicSpring.query.filter(
                SeismicSpring.max_load_kg >= required_weight_capacity
            ).order_by(SeismicSpring.max_load_kg.asc()).all()

            # Get all rubber mounts (assuming all are compatible for now)
            mounts = RubberMounts.query.order_by(RubberMounts.cost.asc()).all()
            
            # Convert results to list of dicts for a consistent API
            return {
                'inertia_bases': [{'part_number': r.part_number, 'name': r.name, 'cost': r.cost} for r in bases],
                'seismic_springs': [{'part_number': r.part_number, 'name': r.name, 'cost': r.cost} for r in springs],
                'rubber_mounts': [{'part_number': r.part_number, 'name': r.name, 'cost': r.cost} for r in mounts]
            }

        except Exception as e:
            logger.error(f"Error fetching compatible accessories for pump '{pump_sku}': {e}", exc_info=True)
            raise DatabaseError(f"Failed to fetch compatible accessories: {e}")