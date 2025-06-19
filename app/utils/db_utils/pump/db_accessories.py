# app/utils/db_utils/pump/db_accessories.py

from typing import Dict, List, Optional
import logging
from app.core.core_database import DatabaseManager, DatabaseError
from decimal import Decimal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PumpAccessoryManager:
    """Manages pump accessory relationships and queries"""

    @staticmethod
    def fetch_accessory_options(accessory_type: str) -> List[Dict]:
        """
        Fetch available accessories by type.
        accessory_type: 'inertia_base', 'seismic_spring', or 'rubber_mount'
        """
        try:
            query = """
                SELECT part_number, name, cost
                FROM CASE %s
                    WHEN 'inertia_base' THEN inertia_bases
                    WHEN 'seismic_spring' THEN seismic_springs
                    WHEN 'rubber_mount' THEN rubber_mounts
                    ELSE NULL
                END
                WHERE status = 'active'
                ORDER BY part_number
            """
            options = DatabaseManager.execute_query(query, (accessory_type,))
            logger.info(f"Fetched {len(options)} options for {accessory_type}")
            return options

        except Exception as e:
            logger.error(f"Error fetching accessory options: {str(e)}")
            raise DatabaseError(f"Failed to fetch accessory options: {str(e)}")

    @staticmethod
    def fetch_accessory_cost(part_number: str) -> Optional[Decimal]:
        """Fetch the cost of a specific accessory"""
        try:
            query = """
                SELECT cost FROM (
                    SELECT part_number, cost FROM inertia_bases
                    UNION ALL
                    SELECT part_number, cost FROM seismic_springs
                    UNION ALL
                    SELECT part_number, cost FROM rubber_mounts
                ) accessories
                WHERE part_number = %s
            """
            result = DatabaseManager.execute_query(query, (part_number,))
            return Decimal(str(result[0]['cost'])) if result else None

        except Exception as e:
            logger.error(f"Error fetching accessory cost: {str(e)}")
            raise DatabaseError(f"Failed to fetch accessory cost: {str(e)}")

    @staticmethod
    def get_compatible_accessories(pump_sku: str) -> Dict[str, List[Dict]]:
        """Get all compatible accessories for a specific pump"""
        try:
            # First get pump details
            pump_query = """
                SELECT weight, length, width
                FROM general_pump_details
                WHERE sku = %s
            """
            pump_details = DatabaseManager.execute_query(pump_query, (pump_sku,))
            
            if not pump_details:
                raise DatabaseError(f"Pump with SKU {pump_sku} not found")

            pump = pump_details[0]
            weight_with_margin = Decimal(str(pump['weight'])) * Decimal('1.2')  # 20% safety margin

            # Get compatible inertia bases
            bases_query = """
                SELECT part_number, name, cost
                FROM inertia_bases
                WHERE length >= %s
                AND width >= %s
                AND weight >= %s
                ORDER BY cost ASC
            """
            
            # Get compatible springs
            springs_query = """
                SELECT part_number, name, cost, max_load_kg
                FROM seismic_springs
                WHERE max_load_kg >= %s
                ORDER BY max_load_kg ASC
            """

            bases = DatabaseManager.execute_query(bases_query, 
                (pump['length'], pump['width'], weight_with_margin))
            springs = DatabaseManager.execute_query(springs_query, (weight_with_margin,))

            return {
                'inertia_bases': bases,
                'seismic_springs': springs,
                'rubber_mounts': DatabaseManager.execute_query(
                    "SELECT part_number, name, cost FROM rubber_mounts ORDER BY cost ASC"
                )
            }

        except Exception as e:
            logger.error(f"Error fetching compatible accessories: {str(e)}")
            raise DatabaseError(f"Failed to fetch compatible accessories: {str(e)}")