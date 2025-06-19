# app/utils/db_utils/import/import_processor.py

from typing import Dict, List, Any, Optional, Tuple, Union
import logging
from pathlib import Path
import pandas as pd
from datetime import datetime
import json
import tempfile
import shutil
import hashlib
from app.core.core_database import DatabaseManager, DatabaseError
from .excel_import import ExcelImporter
from .data_validator import DataValidator

logger = logging.getLogger(__name__)

class ImportProcessor:
    """Handles the import process workflow"""

    def __init__(self):
        self.import_history = []
        self.temp_dir = tempfile.mkdtemp()
        self.supported_types = {
            'pump': self._process_pump_import,
            'bom': self._process_bom_import,
            'inertia_base': self._process_inertia_base_import,
            'seismic_spring': self._process_seismic_spring_import
        }

    def __del__(self):
        """Cleanup temporary directory on object destruction"""
        try:
            shutil.rmtree(self.temp_dir)
        except Exception as e:
            logger.error(f"Error cleaning up temp directory: {str(e)}")

    def process_import_file(
        self,
        file_path: str,
        import_type: str,
        sheet_name: Optional[str] = None,
        options: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Process import file with error handling and reporting
        
        Args:
            file_path: Path to the import file
            import_type: Type of import ('pump', 'bom', etc.)
            sheet_name: Specific sheet to process
            options: Additional import options

        Returns:
            Dict containing import results and statistics
        """
        try:
            logger.info(f"Starting import process for {import_type}")
            start_time = datetime.now()

            # Validate file exists
            if not Path(file_path).exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            # Validate import type
            if import_type not in self.supported_types:
                raise ValueError(f"Unsupported import type: {import_type}")

            # Create backup of file
            backup_path = self._create_backup(file_path)
            logger.info(f"Backup created at: {backup_path}")

            # Process the import
            import_func = self.supported_types[import_type]
            success_count, errors = import_func(file_path, sheet_name, options)

            # Generate error report if needed
            error_report = None
            if errors:
                error_report = self._create_error_report(errors, import_type)

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Create import record
            import_record = {
                'success_count': success_count,
                'error_count': len(errors),
                'duration_seconds': duration,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'error_report': error_report,
                'import_type': import_type,
                'file_name': Path(file_path).name,
                'backup_path': backup_path,
                'options': options
            }

            # Save import history
            self._save_import_record(import_record)

            logger.info(f"Import completed: {success_count} successful, {len(errors)} errors")
            if error_report:
                logger.info(f"Error report generated: {error_report}")

            return import_record

        except Exception as e:
            logger.error(f"Error processing import: {str(e)}")
            raise DatabaseError(f"Import processing failed: {str(e)}")

    def _process_pump_import(
        self,
        file_path: str,
        sheet_name: Optional[str],
        options: Optional[Dict]
    ) -> Tuple[int, List[Dict[str, Any]]]:
        """Process pump data import"""
        return ExcelImporter.import_pump_data(file_path, sheet_name)

    def _process_bom_import(
        self,
        file_path: str,
        sheet_name: Optional[str],
        options: Optional[Dict]
    ) -> Tuple[int, List[Dict[str, Any]]]:
        """Process BOM data import"""
        return ExcelImporter.import_bom_data(file_path, sheet_name)

    def _process_inertia_base_import(
        self,
        file_path: str,
        sheet_name: Optional[str],
        options: Optional[Dict]
    ) -> Tuple[int, List[Dict[str, Any]]]:
        """Process inertia base data import"""
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            required_columns = {
                'part_number', 'name', 'length', 'width', 'height',
                'spring_mount_height', 'weight', 'spring_amount', 'cost'
            }

            if not required_columns.issubset(df.columns):
                missing = required_columns - set(df.columns)
                raise ValueError(f"Missing required columns: {', '.join(missing)}")

            success_count = 0
            errors = []

            for index, row in df.iterrows():
                try:
                    data = {col: row[col] for col in required_columns}
                    DataValidator.validate_inertia_base_data(data)

                    query = """
                        INSERT INTO inertia_bases 
                        (part_number, name, length, width, height, 
                         spring_mount_height, weight, spring_amount, cost)
                        VALUES (%(part_number)s, %(name)s, %(length)s, %(width)s, 
                                %(height)s, %(spring_mount_height)s, %(weight)s, 
                                %(spring_amount)s, %(cost)s)
                        ON CONFLICT (part_number) DO UPDATE SET
                            name = EXCLUDED.name,
                            length = EXCLUDED.length,
                            width = EXCLUDED.width,
                            height = EXCLUDED.height,
                            spring_mount_height = EXCLUDED.spring_mount_height,
                            weight = EXCLUDED.weight,
                            spring_amount = EXCLUDED.spring_amount,
                            cost = EXCLUDED.cost
                    """
                    
                    DatabaseManager.execute_query(query, data)
                    success_count += 1

                except Exception as e:
                    errors.append({
                        'row': index + 2,
                        'error': str(e),
                        'data': row.to_dict()
                    })

            return success_count, errors

        except Exception as e:
            logger.error(f"Error importing inertia base data: {str(e)}")
            raise DatabaseError(f"Failed to import inertia base data: {str(e)}")

    def _process_seismic_spring_import(
        self,
        file_path: str,
        sheet_name: Optional[str],
        options: Optional[Dict]
    ) -> Tuple[int, List[Dict[str, Any]]]:
        """Process seismic spring data import"""
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            required_columns = {
                'part_number', 'name', 'max_load_kg', 'static_deflection',
                'spring_constant_kg_mm', 'stripe1', 'stripe2', 'cost'
            }

            if not required_columns.issubset(df.columns):
                missing = required_columns - set(df.columns)
                raise ValueError(f"Missing required columns: {', '.join(missing)}")

            success_count = 0
            errors = []

            for index, row in df.iterrows():
                try:
                    data = {col: row[col] for col in required_columns}
                    DataValidator.validate_seismic_spring_data(data)

                    query = """
                        INSERT INTO seismic_springs 
                        (part_number, name, max_load_kg, static_deflection,
                         spring_constant_kg_mm, stripe1, stripe2, cost)
                        VALUES (%(part_number)s, %(name)s, %(max_load_kg)s, 
                                %(static_deflection)s, %(spring_constant_kg_mm)s,
                                %(stripe1)s, %(stripe2)s, %(cost)s)
                        ON CONFLICT (part_number) DO UPDATE SET
                            name = EXCLUDED.name,
                            max_load_kg = EXCLUDED.max_load_kg,
                            static_deflection = EXCLUDED.static_deflection,
                            spring_constant_kg_mm = EXCLUDED.spring_constant_kg_mm,
                            stripe1 = EXCLUDED.stripe1,
                            stripe2 = EXCLUDED.stripe2,
                            cost = EXCLUDED.cost
                    """
                    
                    DatabaseManager.execute_query(query, data)
                    success_count += 1

                except Exception as e:
                    errors.append({
                        'row': index + 2,
                        'error': str(e),
                        'data': row.to_dict()
                    })

            return success_count, errors

        except Exception as e:
            logger.error(f"Error importing seismic spring data: {str(e)}")
            raise DatabaseError(f"Failed to import seismic spring data: {str(e)}")

    def _create_backup(self, file_path: str) -> str:
        """Create backup of import file"""
        try:
            file_hash = self._calculate_file_hash(file_path)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"backup_{timestamp}_{file_hash[:8]}{Path(file_path).suffix}"
            backup_path = Path(self.temp_dir) / backup_name
            
            shutil.copy2(file_path, backup_path)
            return str(backup_path)
        except Exception as e:
            logger.error(f"Error creating backup: {str(e)}")
            raise

    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def _create_error_report(self, errors: List[Dict], import_type: str) -> str:
        """Create detailed error report"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_path = Path(self.temp_dir) / f'error_report_{import_type}_{timestamp}.xlsx'
            
            error_df = pd.DataFrame([{
                'Row': error['row'],
                'Error': error['error'],
                **error['data']
            } for error in errors])
            
            error_df.to_excel(report_path, index=False)
            return str(report_path)
        except Exception as e:
            logger.error(f"Error creating error report: {str(e)}")
            raise

    def _save_import_record(self, record: Dict[str, Any]) -> None:
        """Save import record to history"""
        try:
            self.import_history.append(record)
            
            # Save to database for persistence
            query = """
                INSERT INTO import_history 
                (import_type, file_name, success_count, error_count, 
                 duration_seconds, start_time, end_time, error_report,
                 backup_path, options)
                VALUES (%(import_type)s, %(file_name)s, %(success_count)s,
                        %(error_count)s, %(duration_seconds)s, %(start_time)s,
                        %(end_time)s, %(error_report)s, %(backup_path)s,
                        %(options)s)
            """
            
            DatabaseManager.execute_query(query, record)
        except Exception as e:
            logger.error(f"Error saving import record: {str(e)}")
            raise

    def get_import_history(
        self,
        import_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve import history with optional filters"""
        try:
            query = """
                SELECT * FROM import_history 
                WHERE 1=1
            """
            params = []
            
            if import_type:
                query += " AND import_type = %s"
                params.append(import_type)
            
            if start_date:
                query += " AND start_time >= %s"
                params.append(start_date)
            
            if end_date:
                query += " AND end_time <= %s"
                params.append(end_date)
            
            query += " ORDER BY start_time DESC"
            
            return DatabaseManager.execute_query(query, tuple(params) if params else None)
        except Exception as e:
            logger.error(f"Error retrieving import history: {str(e)}")
            raise DatabaseError(f"Failed to retrieve import history: {str(e)}")