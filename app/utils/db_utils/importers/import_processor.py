from typing import Dict, Any, List, Optional
from werkzeug.utils import secure_filename
import os
from pathlib import Path
from celery import Celery

from .excel_import import ExcelImporter
# Correct the import paths
from app.core.core_database import DatabaseManager
from app.core.core_errors import DatabaseError
from app.core.core_logging import logger

# This would be configured in your Flask app config
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

celery = Celery(__name__, broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

class ImportProcessor:
    """Handles the processing of file uploads for data import."""

    def __init__(self, upload_folder: str):
        self.upload_folder = Path(upload_folder)
        if not self.upload_folder.exists():
            self.upload_folder.mkdir(parents=True, exist_ok=True)

    def save_file(self, file) -> Path:
        """Saves an uploaded file securely to the upload folder."""
        if not file or not file.filename:
            raise ValueError("Invalid file provided.")
            
        filename = secure_filename(file.filename)
        filepath = self.upload_folder / filename
        file.save(filepath)
        logger.info(f"File '{filename}' saved to '{filepath}'.")
        return filepath

    @staticmethod
    @celery.task(bind=True)
    def process_import_task(self, file_path: str, import_type: str, sheet_name: Optional[str] = None):
        """
        Celery task to handle long-running import processes asynchronously.
        """
        logger.info(f"Celery task started for importing '{import_type}' from '{file_path}'.")
        try:
            if import_type == 'pump_data':
                success_count, errors = ExcelImporter.import_pump_data(file_path, sheet_name)
            elif import_type == 'bom_data':
                success_count, errors = ExcelImporter.import_bom_data(file_path, sheet_name)
            else:
                raise ValueError(f"Unknown import type: {import_type}")

            result = {
                'status': 'Complete',
                'success_count': success_count,
                'error_count': len(errors)
            }
            if errors:
                error_report_path = ExcelImporter.create_error_report(errors, os.path.dirname(file_path))
                result['error_report'] = error_report_path
                logger.warning(f"Import for '{file_path}' completed with {len(errors)} errors.")
            else:
                logger.info(f"Import for '{file_path}' completed successfully.")
            
            return result

        except Exception as e:
            logger.error(f"Celery import task failed for file '{file_path}': {e}", exc_info=True)
            # You might want to update the task state to 'FAILURE'
            self.update_state(state='FAILURE', meta={'exc_type': type(e).__name__, 'exc_message': str(e)})
            raise

    def start_import(self, file_path: str, import_type: str, sheet_name: Optional[str] = None) -> str:
        """Kicks off the asynchronous import task."""
        task = self.process_import_task.delay(str(file_path), import_type, sheet_name)
        logger.info(f"Dispatched import task {task.id} for file '{file_path}'.")
        return task.id