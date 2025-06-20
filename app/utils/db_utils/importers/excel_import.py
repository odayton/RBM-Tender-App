from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import pandas as pd
from pathlib import Path

# Corrected imports
from app.core.core_database import DatabaseManager
from app.core.core_errors import DatabaseError
from .data_validator import DataValidator
from app.core.core_logging import logger

class ExcelImporter:
    """Handles Excel file imports with validation and error handling."""

    SUPPORTED_EXTENSIONS = {'.xlsx', '.xls'}

    @staticmethod
    def validate_file(file_path: str) -> None:
        """Validate file format."""
        if not Path(file_path).suffix.lower() in ExcelImporter.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file format. Supported: {', '.join(ExcelImporter.SUPPORTED_EXTENSIONS)}")

    @staticmethod
    def get_sheet_names(file_path: str) -> List[str]:
        """Get available sheet names from an Excel file."""
        try:
            ExcelImporter.validate_file(file_path)
            xls = pd.ExcelFile(file_path)
            return xls.sheet_names
        except Exception as e:
            logger.error(f"Error reading Excel file sheets from '{file_path}': {e}", exc_info=True)
            raise DatabaseError(f"Failed to read Excel sheets: {e}")

    @staticmethod
    def import_pump_data(
        file_path: str, sheet_name: Optional[str] = None
    ) -> Tuple[int, List[Dict[str, Any]]]:
        """Import pump data from an Excel file, returning success count and errors."""
        logger.info(f"Starting pump data import from '{file_path}', sheet: '{sheet_name or 'default'}'.")
        try:
            ExcelImporter.validate_file(file_path)
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            required_columns = {'sku', 'name', 'poles', 'kw', 'ie_class', 'mei', 'weight', 'length', 'width', 'height'}
            if not required_columns.issubset(df.columns):
                missing = required_columns - set(df.columns)
                raise ValueError(f"Missing required columns in Excel file: {', '.join(missing)}")

            success_count = 0
            errors = []
            for index, row in df.iterrows():
                try:
                    pump_data = DataValidator.validate_pump_data(row.to_dict())
                    
                    query = """
                        INSERT INTO general_pump_details 
                            (sku, name, poles, kw, ie_class, mei, weight, length, width, height)
                        VALUES 
                            (%(sku)s, %(name)s, %(poles)s, %(kw)s, %(ie_class)s, %(mei)s, 
                             %(weight)s, %(length)s, %(width)s, %(height)s)
                        ON CONFLICT (sku) DO UPDATE SET
                            name = EXCLUDED.name, poles = EXCLUDED.poles, kw = EXCLUDED.kw,
                            ie_class = EXCLUDED.ie_class, mei = EXCLUDED.mei, weight = EXCLUDED.weight,
                            length = EXCLUDED.length, width = EXCLUDED.width, height = EXCLUDED.height
                    """
                    DatabaseManager.execute_query(query, pump_data)
                    success_count += 1
                except Exception as e:
                    logger.warning(f"Failed to process row {index + 2} from pump import: {e}")
                    errors.append({'row': index + 2, 'error': str(e), 'data': row.to_dict()})
            
            logger.info(f"Pump data import complete. Success: {success_count}, Failures: {len(errors)}.")
            return success_count, errors

        except Exception as e:
            logger.error(f"Error importing pump data from '{file_path}': {e}", exc_info=True)
            raise DatabaseError(f"Failed to import pump data: {e}")

    @staticmethod
    def import_bom_data(
        file_path: str, sheet_name: Optional[str] = None
    ) -> Tuple[int, List[Dict[str, Any]]]:
        """Import BOM data from an Excel file, returning success count and errors."""
        logger.info(f"Starting BOM data import from '{file_path}', sheet: '{sheet_name or 'default'}'.")
        try:
            ExcelImporter.validate_file(file_path)
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            required_columns = {'pump_sku', 'inertia_base_part_number', 'seismic_spring_part_number'}
            if not required_columns.issubset(df.columns):
                missing = required_columns - set(df.columns)
                raise ValueError(f"Missing required columns in Excel file: {', '.join(missing)}")

            success_count = 0
            errors = []
            for index, row in df.iterrows():
                try:
                    bom_data = DataValidator.validate_bom_data(row.to_dict())
                    
                    query = """
                        INSERT INTO bom (pump_sku, inertia_base_part_number, seismic_spring_part_number)
                        VALUES (%(pump_sku)s, %(inertia_base_part_number)s, %(seismic_spring_part_number)s)
                        ON CONFLICT (pump_sku) DO UPDATE SET
                            inertia_base_part_number = EXCLUDED.inertia_base_part_number,
                            seismic_spring_part_number = EXCLUDED.seismic_spring_part_number
                    """
                    DatabaseManager.execute_query(query, bom_data)
                    success_count += 1
                except Exception as e:
                    logger.warning(f"Failed to process row {index + 2} from BOM import: {e}")
                    errors.append({'row': index + 2, 'error': str(e), 'data': row.to_dict()})
            
            logger.info(f"BOM data import complete. Success: {success_count}, Failures: {len(errors)}.")
            return success_count, errors

        except Exception as e:
            logger.error(f"Error importing BOM data from '{file_path}': {e}", exc_info=True)
            raise DatabaseError(f"Failed to import BOM data: {e}")

    @staticmethod
    def create_error_report(errors: List[Dict[str, Any]], destination_dir: str) -> str:
        """Create a detailed Excel report for failed import rows."""
        if not errors:
            return ""
        try:
            error_data = [{'Row': e['row'], 'Error': e['error'], **e['data']} for e in errors]
            error_df = pd.DataFrame(error_data)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            error_filepath = Path(destination_dir) / f'import_errors_{timestamp}.xlsx'
            
            error_df.to_excel(error_filepath, index=False)
            logger.info(f"Successfully created error report at: {error_filepath}")
            return str(error_filepath)

        except Exception as e:
            logger.error(f"Error creating import error report: {e}", exc_info=True)
            raise DatabaseError(f"Failed to create error report: {e}")