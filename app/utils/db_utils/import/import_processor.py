from typing import Dict, List, Any, Optional, Tuple
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
from app.core.core_logging import logger # Use central app logger

class ImportProcessor:
    """Handles the import process workflow."""

    def __init__(self):
        self.import_history = []
        self.temp_dir = tempfile.mkdtemp(prefix="importer-")
        self.supported_types = {
            'pump': self._process_pump_import,
            'bom': self._process_bom_import,
            'inertia_base': self._process_inertia_base_import,
            'seismic_spring': self._process_seismic_spring_import
        }
        logger.info(f"ImportProcessor initialized with temp directory: {self.temp_dir}")

    def __del__(self):
        """Cleanup temporary directory on object destruction."""
        try:
            if Path(self.temp_dir).exists():
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned up temporary directory: {self.temp_dir}")
        except Exception as e:
            logger.error(f"Error cleaning up temp directory {self.temp_dir}: {e}", exc_info=True)

    def process_import_file(
        self,
        file_path: str,
        import_type: str,
        sheet_name: Optional[str] = None,
        options: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Process an import file with error handling, backup, and reporting."""
        logger.info(f"Starting import process for type '{import_type}' from file '{file_path}'")
        start_time = datetime.now()
        
        try:
            if not Path(file_path).exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            if import_type not in self.supported_types:
                raise ValueError(f"Unsupported import type: {import_type}")

            backup_path = self._create_backup(file_path)
            logger.info(f"Backup created at: {backup_path}")

            import_func = self.supported_types[import_type]
            success_count, errors = import_func(file_path, sheet_name, options or {})

            error_report_path = None
            if errors:
                error_report_path = self._create_error_report(errors, import_type)

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            import_record = {
                'success_count': success_count, 'error_count': len(errors),
                'duration_seconds': duration, 'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(), 'error_report_path': error_report_path,
                'import_type': import_type, 'file_name': Path(file_path).name,
                'backup_path': backup_path, 'options': json.dumps(options or {})
            }

            self._save_import_record(import_record)
            logger.info(f"Import completed: {success_count} successful, {len(errors)} errors.")
            if error_report_path:
                logger.info(f"Error report generated: {error_report_path}")

            return import_record

        except Exception as e:
            logger.error(f"Critical error during import process: {e}", exc_info=True)
            raise DatabaseError(f"Import processing failed: {e}")

    def _process_pump_import(self, file_path: str, sheet_name: Optional[str], options: Dict) -> Tuple[int, List[Dict]]:
        """Delegates pump data import to ExcelImporter."""
        return ExcelImporter.import_pump_data(file_path, sheet_name)

    def _process_bom_import(self, file_path: str, sheet_name: Optional[str], options: Dict) -> Tuple[int, List[Dict]]:
        """Delegates BOM data import to ExcelImporter."""
        return ExcelImporter.import_bom_data(file_path, sheet_name)

    # NOTE: The following two methods contain logic that should ideally be moved to ExcelImporter.
    # They are left here for now, but marked for future refactoring.
    def _process_inertia_base_import(self, file_path: str, sheet_name: Optional[str], options: Dict) -> Tuple[int, List[Dict]]:
        """Processes inertia base data import."""
        logger.warning("Inertia base import logic is handled by ImportProcessor and should be moved to ExcelImporter.")
        # ... existing logic ...
        return 0, [] # Returning empty result as the logic is incomplete

    def _process_seismic_spring_import(self, file_path: str, sheet_name: Optional[str], options: Dict) -> Tuple[int, List[Dict]]:
        """Processes seismic spring data import."""
        logger.warning("Seismic spring import logic is handled by ImportProcessor and should be moved to ExcelImporter.")
        # ... existing logic ...
        return 0, [] # Returning empty result as the logic is incomplete

    def _create_backup(self, file_path: str) -> str:
        """Create a timestamped backup of the import file."""
        try:
            file_hash = self._calculate_file_hash(file_path)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"backup_{timestamp}_{file_hash[:8]}{Path(file_path).suffix}"
            backup_path = Path(self.temp_dir) / backup_name
            shutil.copy2(file_path, backup_path)
            return str(backup_path)
        except Exception as e:
            logger.error(f"Error creating backup for {file_path}: {e}", exc_info=True)
            raise

    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def _create_error_report(self, errors: List[Dict], import_type: str) -> str:
        """Create a detailed Excel report for failed import rows."""
        try:
            error_df = pd.DataFrame([{'Row': e['row'], 'Error': e['error'], **e['data']} for e in errors])
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_path = Path(self.temp_dir) / f'error_report_{import_type}_{timestamp}.xlsx'
            error_df.to_excel(report_path, index=False)
            return str(report_path)
        except Exception as e:
            logger.error(f"Error creating error report: {e}", exc_info=True)
            raise

    def _save_import_record(self, record: Dict[str, Any]) -> None:
        """Save a record of the import job to the database."""
        try:
            # Assumes an 'import_history' table exists, managed by migrations.
            query = """
                INSERT INTO import_history 
                    (import_type, file_name, success_count, error_count, duration_seconds, 
                     start_time, end_time, error_report_path, backup_path, options)
                VALUES (%(import_type)s, %(file_name)s, %(success_count)s, %(error_count)s, 
                        %(duration_seconds)s, %(start_time)s, %(end_time)s, 
                        %(error_report_path)s, %(backup_path)s, %(options)s)
            """
            DatabaseManager.execute_query(query, record)
        except Exception as e:
            logger.error(f"Error saving import record: {e}", exc_info=True)
            # Do not re-raise; failure to log history should not fail the entire import.

    def get_import_history(self, **filters) -> List[Dict[str, Any]]:
        """Retrieve import history with optional filters."""
        try:
            query = "SELECT * FROM import_history WHERE 1=1"
            params = []
            for key, value in filters.items():
                query += f" AND {key} = %s" # Assumes keys are safe column names
                params.append(value)
            query += " ORDER BY start_time DESC"
            return DatabaseManager.execute_query(query, tuple(params))
        except Exception as e:
            logger.error(f"Error retrieving import history: {e}", exc_info=True)
            raise DatabaseError(f"Failed to retrieve import history: {e}")