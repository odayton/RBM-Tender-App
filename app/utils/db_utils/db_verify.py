from typing import Dict, List, Any, Tuple
from sqlalchemy import inspect
from sqlalchemy.engine import Engine
from flask_sqlalchemy.extension import SQLAlchemy

from app.core.core_database import DatabaseManager
from app.core.core_logging import logger

class DatabaseVerifier:
    """
    Handles dynamic database schema verification and data integrity checks
    by inspecting live SQLAlchemy models.
    """

    @staticmethod
    def _get_schema_from_models(db: SQLAlchemy) -> Dict[str, Any]:
        """Dynamically builds an expected schema from the SQLAlchemy metadata."""
        expected_schema = {}
        inspector = inspect(db.engine)
        for table_name, table in db.metadata.tables.items():
            expected_schema[table_name] = {
                'columns': {c.name: str(c.type) for c in table.columns},
                'primary_key': [c.name for c in table.primary_key.columns],
                'foreign_keys': [
                    {
                        "constrained_columns": fk.constrained_columns,
                        "referred_table": fk.referred_table.name,
                        "referred_columns": fk.referred_columns,
                    }
                    for fk in table.foreign_keys
                ],
                # 'indexes': [idx.name for idx in table.indexes],
            }
        return expected_schema

    @classmethod
    def run_full_verification(cls, db: SQLAlchemy) -> Tuple[bool, List[str]]:
        """
        Runs all database verification checks against the live SQLAlchemy models.

        Args:
            db (SQLAlchemy): The Flask-SQLAlchemy instance to get model metadata from.
        
        Returns:
            A tuple containing a success boolean and a list of all identified issues.
        """
        logger.info("Starting full dynamic database verification...")
        all_issues = []
        
        try:
            expected_schema = cls._get_schema_from_models(db)
            
            # Verify schema
            schema_issues = cls._verify_database_schema(expected_schema)
            if schema_issues:
                all_issues.extend(['Schema Issues:'] + schema_issues)
            
            # Check data integrity (foreign keys)
            integrity_issues = cls._check_data_integrity(expected_schema)
            if integrity_issues:
                all_issues.extend(['Data Integrity Issues:'] + integrity_issues)

        except Exception as e:
            logger.error(f"A critical error occurred during verification: {e}", exc_info=True)
            all_issues.append(f"CRITICAL VERIFICATION ERROR: {e}")

        success = not all_issues
        if success:
            logger.info("Full database verification completed successfully.")
        else:
            logger.warning(f"Database verification found {len(all_issues)} issues.")

        return success, all_issues

    @staticmethod
    def _verify_database_schema(expected_schema: Dict[str, Any]) -> List[str]:
        """Verify the database schema against the dynamically generated structure."""
        issues = []
        try:
            query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
            # Note: DatabaseManager provides raw query execution if needed,
            # but for this, we can also use SQLAlchemy's inspector.
            with DatabaseManager.get_engine().connect() as connection:
                result = connection.execute(query)
                existing_tables = {row[0] for row in result}

            # Check for missing or extra tables
            expected_table_set = set(expected_schema.keys())
            missing_tables = expected_table_set - existing_tables
            extra_tables = existing_tables - expected_table_set

            for table in missing_tables:
                issues.append(f"Missing Table: SQLAlchemy model '{table}' exists but table is not in the database.")
            for table in extra_tables:
                # This could also indicate tables left over from old migrations.
                issues.append(f"Extra Table: Table '{table}' exists in the database but has no corresponding SQLAlchemy model.")

            # Check columns for tables that do exist
            for table_name in expected_table_set.intersection(existing_tables):
                column_issues = DatabaseVerifier._verify_table_columns(table_name, expected_schema[table_name])
                issues.extend(column_issues)

        except Exception as e:
            logger.error(f"Error verifying database schema: {e}", exc_info=True)
            issues.append(f"Schema verification error: {e}")

        return issues

    @staticmethod
    def _verify_table_columns(table_name: str, expected_table_info: Dict[str, Any]) -> List[str]:
        """Verify columns in a specific table against the SQLAlchemy model info."""
        issues = []
        try:
            query = "SELECT column_name, udt_name FROM information_schema.columns WHERE table_name = %s"
            with DatabaseManager.get_engine().connect() as connection:
                 result = connection.execute(query, (table_name,))
                 existing_columns = {row[0]: row[1] for row in result}
            
            expected_columns = expected_table_info['columns']
            
            # Check for missing or extra columns
            expected_col_set = set(expected_columns.keys())
            existing_col_set = set(existing_columns.keys())
            missing_cols = expected_col_set - existing_col_set
            extra_cols = existing_col_set - expected_col_set

            for col in missing_cols:
                issues.append(f"Missing Column in table '{table_name}': Model expects '{col}'.")
            for col in extra_cols:
                issues.append(f"Extra Column in table '{table_name}': Column '{col}' exists in DB but not in the model.")

        except Exception as e:
            logger.error(f"Error verifying columns for table {table_name}: {e}", exc_info=True)
            issues.append(f"Column verification error in {table_name}: {e}")

        return issues

    @staticmethod
    def _check_data_integrity(expected_schema: Dict[str, Any]) -> List[str]:
        """Check data integrity using the dynamically discovered foreign keys."""
        issues = []
        try:
            for table_name, config in expected_schema.items():
                if 'foreign_keys' in config:
                    for fk in config['foreign_keys']:
                        # Example for single-column foreign keys
                        fk_column = fk['constrained_columns'][0]
                        ref_table = fk['referred_table']
                        ref_column = fk['referred_columns'][0]
                        
                        query = f"""
                            SELECT t1."{fk_column}"
                            FROM "{table_name}" t1
                            LEFT JOIN "{ref_table}" t2 ON t1."{fk_column}" = t2."{ref_column}"
                            WHERE t1."{fk_column}" IS NOT NULL AND t2."{ref_column}" IS NULL
                            LIMIT 10
                        """
                        orphaned_records = DatabaseManager.execute_query(query)
                        if orphaned_records:
                            issues.append(f"Orphaned records found in '{table_name}' on column '{fk_column}' referencing '{ref_table}'.")
        except Exception as e:
            logger.error(f"Error checking data integrity: {e}", exc_info=True)
            issues.append(f"Data integrity check error: {e}")

        return issues