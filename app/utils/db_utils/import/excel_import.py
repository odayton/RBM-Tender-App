# app/utils/db_utils/import/excel_import.py

from typing import Dict, List, Any, Optional, Tuple
import logging
import pandas as pd
from datetime import datetime
from app.core.core_database import DatabaseManager, DatabaseError
from .data_validator import DataValidator

logger = logging.getLogger(__name__)

class ExcelImporter:
    """Handles Excel file imports with validation and error handling"""

    SUPPORTED_EXTENSIONS = {'.xlsx', '.xls'}

    @staticmethod
    def validate_file(file_path: str) -> bool:
        """Validate file format and basic structure"""
        if not any(file_path.lower().endswith(ext) for ext in ExcelImporter.SUPPORTED_EXTENSIONS):
            raise ValueError(f"Unsupported file format. Supported formats: {', '.join(ExcelImporter.SUPPORTED_EXTENSIONS)}")
        return True

    @staticmethod
    def get_sheet_names(file_path: str) -> List[str]:
        """Get available sheet names from Excel file"""
        try:
            xls = pd.ExcelFile(file_path)
            return xls.sheet_names
        except Exception as e:
            logger.error(f"Error reading Excel file sheets: {str(e)}")
            raise DatabaseError(f"Failed to read Excel sheets: {str(e)}")

    @staticmethod
    def import_pump_data(
        file_path: str,
        sheet_name: Optional[str] = None
    ) -> Tuple[int, List[Dict[str, Any]]]:
        """Import pump data from Excel file"""
        try:
            ExcelImporter.validate_file(file_path)
            
            # Read Excel file
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # Validate column names
            required_columns = {
                'sku', 'name', 'poles', 'kw', 'ie_class', 'mei',
                'weight', 'length', 'width', 'height'
            }
            
            if not required_columns.issubset(df.columns):
                missing = required_columns - set(df.columns)
                raise ValueError(f"Missing required columns: {', '.join(missing)}")

            # Process rows
            success_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    # Clean and validate data
                    pump_data = DataValidator.validate_pump_data({
                        'sku': str(row['sku']).strip(),
                        'name': str(row['name']).strip(),
                        'poles': row['poles'],
                        'kw': row['kw'],
                        'ie_class': row['ie_class'],
                        'mei': row['mei'],
                        'weight': row['weight'],
                        'length': row['length'],
                        'width': row['width'],
                        'height': row['height']
                    })
                    
                    # Insert or update pump data
                    query = """
                        INSERT INTO general_pump_details 
                        (sku, name, poles, kw, ie_class, mei, weight, length, width, height)
                        VALUES (%(sku)s, %(name)s, %(poles)s, %(kw)s, %(ie_class)s, 
                                %(mei)s, %(weight)s, %(length)s, %(width)s, %(height)s)
                        ON CONFLICT (sku) DO UPDATE SET
                            name = EXCLUDED.name,
                            poles = EXCLUDED.poles,
                            kw = EXCLUDED.kw,
                            ie_class = EXCLUDED.ie_class,
                            mei = EXCLUDED.mei,
                            weight = EXCLUDED.weight,
                            length = EXCLUDED.length,
                            width = EXCLUDED.width,
                            height = EXCLUDED.height
                    """
                    
                    DatabaseManager.execute_query(query, pump_data)
                    success_count += 1
                    
                except Exception as e:
                    errors.append({
                        'row': index + 2,  # Excel row number (1-based + header)
                        'error': str(e),
                        'data': row.to_dict()
                    })
            
            return success_count, errors

        except Exception as e:
            logger.error(f"Error importing pump data: {str(e)}")
            raise DatabaseError(f"Failed to import pump data: {str(e)}")

    @staticmethod
    def import_bom_data(
        file_path: str,
        sheet_name: Optional[str] = None
    ) -> Tuple[int, List[Dict[str, Any]]]:
        """Import BOM data from Excel file"""
        try:
            ExcelImporter.validate_file(file_path)
            
            # Read Excel file
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # Validate column names
            required_columns = {'pump_sku', 'inertia_base_part_number', 'seismic_spring_part_number'}
            
            if not required_columns.issubset(df.columns):
                missing = required_columns - set(df.columns)
                raise ValueError(f"Missing required columns: {', '.join(missing)}")

            # Process rows
            success_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    # Clean and validate data
                    bom_data = DataValidator.validate_bom_data({
                        'pump_sku': str(row['pump_sku']).strip(),
                        'inertia_base_part_number': str(row['inertia_base_part_number']).strip() if pd.notna(row['inertia_base_part_number']) else None,
                        'seismic_spring_part_number': str(row['seismic_spring_part_number']).strip() if pd.notna(row['seismic_spring_part_number']) else None
                    })
                    
                    # Insert or update BOM data
                    query = """
                        INSERT INTO bom 
                        (pump_sku, inertia_base_part_number, seismic_spring_part_number)
                        VALUES (%(pump_sku)s, %(inertia_base_part_number)s, %(seismic_spring_part_number)s)
                        ON CONFLICT (pump_sku) DO UPDATE SET
                            inertia_base_part_number = EXCLUDED.inertia_base_part_number,
                            seismic_spring_part_number = EXCLUDED.seismic_spring_part_number
                    """
                    
                    DatabaseManager.execute_query(query, bom_data)
                    success_count += 1
                    
                except Exception as e:
                    errors.append({
                        'row': index + 2,
                        'error': str(e),
                        'data': row.to_dict()
                    })
            
            return success_count, errors

        except Exception as e:
            logger.error(f"Error importing BOM data: {str(e)}")
            raise DatabaseError(f"Failed to import BOM data: {str(e)}")

    @staticmethod
    def create_error_report(errors: List[Dict[str, Any]], file_path: str) -> str:
        """Create detailed error report for failed imports"""
        try:
            # Create DataFrame from errors
            error_df = pd.DataFrame([{
                'Row': error['row'],
                'Error': error['error'],
                **error['data']
            } for error in errors])
            
            # Generate error report filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            error_file = f'import_errors_{timestamp}.xlsx'
            
            # Save error report
            error_df.to_excel(error_file, index=False)
            return error_file

        except Exception as e:
            logger.error(f"Error creating error report: {str(e)}")
            raise DatabaseError(f"Failed to create error report: {str(e)}")