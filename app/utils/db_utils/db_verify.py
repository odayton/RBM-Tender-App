# app/utils/db_utils/db_verify.py

from typing import Dict, List, Set, Tuple
import logging
from app.core.core_database import DatabaseManager, DatabaseError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseVerifier:
    """Handles database schema verification and data integrity checks"""

    EXPECTED_TABLES = {
        'general_pump_details': {
            'columns': {
                'sku': 'TEXT',
                'name': 'TEXT',
                'poles': 'INTEGER',
                'kw': 'NUMERIC',
                'ie_class': 'TEXT',
                'mei': 'NUMERIC',
                'weight': 'NUMERIC',
                'length': 'NUMERIC',
                'width': 'NUMERIC',
                'height': 'NUMERIC',
                'image_path': 'TEXT',
                'list_price': 'NUMERIC'
            },
            'primary_key': 'sku'
        },
        'historic_pump_data': {
            'columns': {
                'sku': 'TEXT',
                'name': 'TEXT',
                'flow': 'NUMERIC',
                'flow_unit': 'TEXT',
                'head': 'NUMERIC',
                'head_unit': 'TEXT',
                'efficiency': 'TEXT',
                'absorbed_power': 'TEXT',
                'npsh': 'TEXT',
                'image_path': 'TEXT'
            }
        },
        'deals': {
            'columns': {
                'id': 'INTEGER',
                'name': 'TEXT',
                'stage': 'TEXT',
                'type': 'TEXT',
                'location': 'TEXT',
                'close_date': 'DATE',
                'owner': 'TEXT',
                'contact_id': 'INTEGER',
                'company_id': 'INTEGER',
                'amount': 'NUMERIC',
                'created_at': 'TIMESTAMP',
                'updated_at': 'TIMESTAMP'
            },
            'primary_key': 'id'
        },
        'contacts': {
            'columns': {
                'id': 'INTEGER',
                'representative_name': 'TEXT',
                'representative_email': 'TEXT',
                'phone_number': 'TEXT',
                'company_id': 'INTEGER'
            },
            'primary_key': 'id'
        },
        'companies': {
            'columns': {
                'id': 'INTEGER',
                'company_name': 'TEXT',
                'address': 'TEXT',
                'created_at': 'TIMESTAMP',
                'updated_at': 'TIMESTAMP'
            },
            'primary_key': 'id'
        },
        'inertia_bases': {
            'columns': {
                'part_number': 'TEXT',
                'name': 'TEXT',
                'length': 'NUMERIC',
                'width': 'NUMERIC',
                'height': 'NUMERIC',
                'spring_mount_height': 'NUMERIC',
                'weight': 'NUMERIC',
                'spring_amount': 'INTEGER',
                'cost': 'NUMERIC'
            },
            'primary_key': 'part_number'
        },
        'seismic_springs': {
            'columns': {
                'part_number': 'TEXT',
                'name': 'TEXT',
                'max_load_kg': 'NUMERIC',
                'static_deflection': 'NUMERIC',
                'spring_constant_kg_mm': 'NUMERIC',
                'stripe1': 'TEXT',
                'stripe2': 'TEXT',
                'cost': 'NUMERIC'
            },
            'primary_key': 'part_number'
        },
        'rubber_mounts': {
            'columns': {
                'part_number': 'TEXT',
                'name': 'TEXT',
                'weight': 'NUMERIC',
                'cost': 'NUMERIC'
            },
            'primary_key': 'part_number'
        },
        'additional_price_adders': {
            'columns': {
                'id': 'INTEGER',
                'ip_adder': 'NUMERIC',
                'drip_tray_adder': 'NUMERIC'
            },
            'primary_key': 'id'
        },
        'bom': {
            'columns': {
                'id': 'INTEGER',
                'pump_sku': 'TEXT',
                'inertia_base_part_number': 'TEXT',
                'seismic_spring_part_number': 'TEXT',
                'created_at': 'TIMESTAMP'
            },
            'primary_key': 'id',
            'foreign_keys': {
                'pump_sku': ('general_pump_details', 'sku'),
                'inertia_base_part_number': ('inertia_bases', 'part_number'),
                'seismic_spring_part_number': ('seismic_springs', 'part_number')
            }
        }
    }

    @staticmethod
    def verify_database_schema() -> List[str]:
        """Verify the database schema against expected structure"""
        issues = []
        try:
            # Get list of existing tables
            query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """
            existing_tables = {row['table_name'] for row in DatabaseManager.execute_query(query)}
            
            # Check for missing tables
            for table_name in DatabaseVerifier.EXPECTED_TABLES:
                if table_name not in existing_tables:
                    issues.append(f"Missing table: {table_name}")
                else:
                    # Verify columns for existing tables
                    column_issues = DatabaseVerifier._verify_table_columns(table_name)
                    issues.extend(column_issues)

            if not issues:
                logger.info("Database schema verification completed successfully")
            else:
                logger.warning(f"Found {len(issues)} schema issues")

        except Exception as e:
            logger.error(f"Error verifying database schema: {str(e)}")
            issues.append(f"Schema verification error: {str(e)}")

        return issues

    @staticmethod
    def _verify_table_columns(table_name: str) -> List[str]:
        """Verify columns in a specific table"""
        issues = []
        try:
            query = """
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = %s
            """
            existing_columns = {
                row['column_name']: row['data_type']
                for row in DatabaseManager.execute_query(query, (table_name,))
            }

            expected_columns = DatabaseVerifier.EXPECTED_TABLES[table_name]['columns']

            # Check for missing columns
            for col_name, expected_type in expected_columns.items():
                if col_name not in existing_columns:
                    issues.append(f"Missing column in {table_name}: {col_name}")
                elif not DatabaseVerifier._check_type_compatibility(
                    existing_columns[col_name], expected_type):
                    issues.append(
                        f"Type mismatch in {table_name}.{col_name}: "
                        f"expected {expected_type}, got {existing_columns[col_name]}"
                    )

        except Exception as e:
            logger.error(f"Error verifying columns for table {table_name}: {str(e)}")
            issues.append(f"Column verification error in {table_name}: {str(e)}")

        return issues

    @staticmethod
    def _check_type_compatibility(actual_type: str, expected_type: str) -> bool:
        """Check if column types are compatible"""
        # PostgreSQL type mappings
        type_mappings = {
            'INTEGER': {'integer', 'bigint', 'smallint'},
            'NUMERIC': {'numeric', 'decimal', 'real', 'double precision'},
            'TEXT': {'text', 'character varying', 'varchar', 'char'},
            'TIMESTAMP': {'timestamp', 'timestamp without time zone', 'timestamp with time zone'},
            'DATE': {'date'}
        }

        actual_type = actual_type.lower()
        expected_type = expected_type.upper()

        if expected_type in type_mappings:
            return actual_type in type_mappings[expected_type]
        return actual_type == expected_type.lower()

    @staticmethod
    def check_data_integrity() -> List[str]:
        """Check data integrity across tables"""
        issues = []
        try:
            # Check foreign key constraints
            for table_name, config in DatabaseVerifier.EXPECTED_TABLES.items():
                if 'foreign_keys' in config:
                    for fk_column, (ref_table, ref_column) in config['foreign_keys'].items():
                        query = f"""
                            SELECT t1.{fk_column}
                            FROM {table_name} t1
                            LEFT JOIN {ref_table} t2 ON t1.{fk_column} = t2.{ref_column}
                            WHERE t1.{fk_column} IS NOT NULL
                            AND t2.{ref_column} IS NULL
                        """
                        orphaned_records = DatabaseManager.execute_query(query)
                        if orphaned_records:
                            orphaned_values = [str(record[fk_column]) for record in orphaned_records]
                            issues.append(
                                f"Orphaned records in {table_name}.{fk_column}: {', '.join(orphaned_values)}"
                            )

        except Exception as e:
            logger.error(f"Error checking data integrity: {str(e)}")
            issues.append(f"Data integrity check error: {str(e)}")

        return issues

    @staticmethod
    def run_full_verification() -> Tuple[bool, List[str]]:
        """Run all database verification checks"""
        all_issues = []
        
        # Verify schema
        schema_issues = DatabaseVerifier.verify_database_schema()
        if schema_issues:
            all_issues.extend(['Schema Issues:'] + schema_issues)
        
        # Check data integrity
        integrity_issues = DatabaseVerifier.check_data_integrity()
        if integrity_issues:
            all_issues.extend(['Data Integrity Issues:'] + integrity_issues)

        success = len(all_issues) == 0
        if success:
            logger.info("Full database verification completed successfully")
        else:
            logger.warning(f"Database verification found {len(all_issues)} issues")

        return success, all_issues

