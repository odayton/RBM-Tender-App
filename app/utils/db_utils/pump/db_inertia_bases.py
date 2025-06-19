# app/utils/db_utils/db_inertia_bases.py

from typing import Dict, List, Optional, Union
import logging
from datetime import datetime
from decimal import Decimal
from app.core.core_database import DatabaseManager, DatabaseError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InertiaDatabaseManager:
    """Manages all inertia base-related database operations"""

    @staticmethod
    def create_inertia_base_tables() -> None:
        """Creates inertia base tables with PostgreSQL optimizations"""
        try:
            queries = [
                # Inertia Bases table
                """
                CREATE TABLE IF NOT EXISTS inertia_bases (
                    part_number TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    length DECIMAL(10, 2) NOT NULL,
                    width DECIMAL(10, 2) NOT NULL,
                    height DECIMAL(10, 2) NOT NULL,
                    spring_mount_height DECIMAL(10, 2) NOT NULL,
                    weight DECIMAL(10, 2) NOT NULL,
                    spring_amount INTEGER NOT NULL,
                    spring_load DECIMAL(10, 2),
                    cost DECIMAL(10, 2) NOT NULL,
                    material TEXT,
                    coating TEXT,
                    notes TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB DEFAULT '{}'::jsonb
                );

                CREATE INDEX IF NOT EXISTS idx_inertia_dimensions 
                ON inertia_bases(length, width, height);
                
                CREATE INDEX IF NOT EXISTS idx_inertia_weight_springs 
                ON inertia_bases(weight, spring_amount);
                
                CREATE INDEX IF NOT EXISTS idx_inertia_metadata 
                ON inertia_bases USING GIN (metadata);
                """,

                # Inertia Base Usage History
                """
                CREATE TABLE IF NOT EXISTS inertia_base_usage (
                    id SERIAL PRIMARY KEY,
                    part_number TEXT REFERENCES inertia_bases(part_number) ON DELETE CASCADE,
                    deal_id INTEGER REFERENCES deals(id) ON DELETE SET NULL,
                    pump_sku TEXT REFERENCES general_pump_details(sku) ON DELETE SET NULL,
                    installation_date DATE,
                    notes TEXT,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB DEFAULT '{}'::jsonb
                );

                CREATE INDEX IF NOT EXISTS idx_inertia_usage 
                ON inertia_base_usage(part_number, deal_id);
                """
            ]

            for query in queries:
                DatabaseManager.execute_query(query)

            logger.info("Inertia base tables created successfully")
        except Exception as e:
            logger.error(f"Error creating inertia base tables: {str(e)}")
            raise DatabaseError(f"Failed to create inertia base tables: {str(e)}")

    @staticmethod
    def validate_inertia_base_data(data: Dict) -> None:
        """Validate inertia base data before insertion/update"""
        required_fields = [
            'part_number', 'name', 'length', 'width', 'height',
            'spring_mount_height', 'weight', 'spring_amount', 'cost'
        ]
        
        for field in required_fields:
            if field not in data or data[field] is None:
                raise ValueError(f"Missing required field: {field}")

        # Validate numeric values
        numeric_fields = [
            'length', 'width', 'height', 'spring_mount_height',
            'weight', 'spring_load', 'cost'
        ]
        
        for field in numeric_fields:
            if field in data and data[field] is not None:
                try:
                    data[field] = Decimal(str(data[field]))
                    if data[field] <= 0:
                        raise ValueError(f"{field} must be positive")
                except (ValueError, TypeError):
                    raise ValueError(f"Invalid numeric value for {field}")

        # Validate spring amount
        if data['spring_amount'] <= 0:
            raise ValueError("Spring amount must be positive")

    @staticmethod
    def insert_inertia_base(data: Dict) -> str:
        """Insert a new inertia base with validation and audit logging"""
        try:
            # Validate data
            InertiaDatabaseManager.validate_inertia_base_data(data)

            # Check for existing part number
            if DatabaseManager.record_exists('inertia_bases', {'part_number': data['part_number']}):
                raise DatabaseError(f"Inertia base with part number {data['part_number']} already exists")

            # Add timestamps
            data['created_at'] = datetime.now()
            data['updated_at'] = datetime.now()

            fields = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            query = f"""
                INSERT INTO inertia_bases ({fields})
                VALUES ({placeholders})
                RETURNING part_number
            """
            
            result = DatabaseManager.execute_query(query, tuple(data.values()))
            part_number = result[0]['part_number']

            # Create audit log
            DatabaseManager.create_audit_log(
                'inertia_bases',
                'INSERT',
                part_number,
                None,
                data
            )

            return part_number

        except Exception as e:
            logger.error(f"Error inserting inertia base: {str(e)}")
            raise DatabaseError(f"Failed to insert inertia base: {str(e)}")

    @staticmethod
    def fetch_all_inertia_bases(include_inactive: bool = False) -> List[Dict]:
        """Fetch all inertia bases with usage statistics"""
        try:
            query = """
                SELECT 
                    ib.*,
                    COUNT(DISTINCT ibu.deal_id) as total_uses,
                    ARRAY_AGG(DISTINCT ibu.pump_sku) FILTER (WHERE ibu.pump_sku IS NOT NULL) as used_with_pumps,
                    MAX(ibu.installation_date) as last_used_date
                FROM inertia_bases ib
                LEFT JOIN inertia_base_usage ibu ON ib.part_number = ibu.part_number
                WHERE 1=1
            """
            
            if not include_inactive:
                query += " AND ib.status = 'active'"
                
            query += """
                GROUP BY ib.part_number
                ORDER BY ib.part_number
            """
            
            return DatabaseManager.execute_query(query)

        except Exception as e:
            logger.error(f"Error fetching inertia bases: {str(e)}")
            raise DatabaseError(f"Failed to fetch inertia bases: {str(e)}")

    @staticmethod
    def fetch_inertia_base_by_part_number(part_number: str) -> Optional[Dict]:
        """Fetch a specific inertia base with complete information"""
        try:
            query = """
                SELECT 
                    ib.*,
                    (
                        SELECT json_agg(json_build_object(
                            'deal_id', ibu.deal_id,
                            'pump_sku', ibu.pump_sku,
                            'installation_date', ibu.installation_date,
                            'notes', ibu.notes
                        ))
                        FROM inertia_base_usage ibu
                        WHERE ibu.part_number = ib.part_number
                        ORDER BY ibu.installation_date DESC
                    ) as usage_history
                FROM inertia_bases ib
                WHERE ib.part_number = %s
            """
            results = DatabaseManager.execute_query(query, (part_number,))
            return results[0] if results else None

        except Exception as e:
            logger.error(f"Error fetching inertia base: {str(e)}")
            raise DatabaseError(f"Failed to fetch inertia base: {str(e)}")

    @staticmethod
    def find_suitable_inertia_base(requirements: Dict) -> Optional[Dict]:
        """Find a suitable inertia base based on requirements"""
        try:
            # Add safety margin to requirements
            weight_with_margin = Decimal(str(requirements['weight'])) * Decimal('1.2')  # 20% safety margin
            length_with_margin = Decimal(str(requirements['length'])) * Decimal('1.1')  # 10% margin
            width_with_margin = Decimal(str(requirements['width'])) * Decimal('1.1')    # 10% margin

            query = """
                SELECT *
                FROM inertia_bases
                WHERE status = 'active'
                AND weight >= %s
                AND length >= %s
                AND width >= %s
                AND spring_amount >= %s
                ORDER BY (
                    ABS(weight - %s) +
                    ABS(length - %s) +
                    ABS(width - %s)
                ) ASC
                LIMIT 1
            """
            
            params = (
                weight_with_margin,
                length_with_margin,
                width_with_margin,
                requirements.get('min_spring_amount', 4),
                weight_with_margin,
                length_with_margin,
                width_with_margin
            )
            
            results = DatabaseManager.execute_query(query, params)
            return results[0] if results else None

        except Exception as e:
            logger.error(f"Error finding suitable inertia base: {str(e)}")
            raise DatabaseError(f"Failed to find suitable inertia base: {str(e)}")

    @staticmethod
    def record_inertia_base_usage(part_number: str, deal_id: int, pump_sku: str, 
                                 installation_date: Optional[datetime] = None,
                                 notes: Optional[str] = None) -> None:
        """Record usage of an inertia base"""
        try:
            query = """
                INSERT INTO inertia_base_usage 
                (part_number, deal_id, pump_sku, installation_date, notes)
                VALUES (%s, %s, %s, %s, %s)
            """
            DatabaseManager.execute_query(
                query, 
                (part_number, deal_id, pump_sku, installation_date, notes)
            )

        except Exception as e:
            logger.error(f"Error recording inertia base usage: {str(e)}")
            raise DatabaseError(f"Failed to record inertia base usage: {str(e)}")

# Initialize tables when module is imported
try:
    InertiaDatabaseManager.create_inertia_base_tables()
except Exception as e:
    logger.error(f"Failed to initialize inertia base tables: {str(e)}")