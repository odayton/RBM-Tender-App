import os
import shutil
from typing import Optional, Dict, List
from werkzeug.utils import secure_filename
from datetime import datetime
from pathlib import Path

# Import the central app logger and the refactored FileValidation class
from app.core.core_logging import logger
from app.core.core_errors import FileOperationError
from .file_validation import FileValidation

class FileHandler:
    """Handles file operations for the application"""
    
    def __init__(self, base_upload_path: str):
        self.base_upload_path = Path(base_upload_path)
        self.ensure_upload_directories()
    
    def ensure_upload_directories(self) -> None:
        """Create necessary upload directories if they don't exist"""
        directories = [
            self.base_upload_path,
            self.base_upload_path / 'tech-data',
            self.base_upload_path / 'others',
            self.base_upload_path / 'temp'
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Ensured directory exists: {directory}")

    def save_file(self, file, subdirectory: str = None) -> Dict[str, str]:
        """
        Save uploaded file to the appropriate directory
        
        Args:
            file: FileStorage object from Flask
            subdirectory: Optional subdirectory within base upload path
            
        Returns:
            Dict containing file information
            
        Raises:
            FileOperationError: If file save fails
        """
        try:
            if not file:
                raise FileOperationError("save", "none", "No file provided")

            original_filename = secure_filename(file.filename)
            if not original_filename:
                raise FileOperationError("save", "none", "Invalid filename")
            
            is_allowed, message = FileValidation.is_allowed(original_filename)
            if not is_allowed:
                raise FileOperationError("save", original_filename, message)

            # Create timestamped filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            safe_filename = FileValidation.get_safe_filename(timestamp + original_filename)

            # Determine save path using pathlib
            save_directory = self.base_upload_path / (subdirectory or '')
            save_directory.mkdir(parents=True, exist_ok=True)
            
            file_path = save_directory / safe_filename
            file.save(file_path)

            return {
                'filename': safe_filename,
                'original_filename': original_filename,
                'path': str(file_path),
                'size': file_path.stat().st_size,
                'timestamp': timestamp.rstrip('_')
            }

        except Exception as e:
            filename_for_error = original_filename if 'original_filename' in locals() else 'unknown'
            logger.error(f"Error saving file {filename_for_error}: {str(e)}", exc_info=True)
            raise FileOperationError("save", filename_for_error, str(e))

    def delete_file(self, filename: str, subdirectory: Optional[str] = None) -> bool:
        """
        Delete a file from the upload directory
        """
        try:
            file_path = self.base_upload_path / (subdirectory or '') / filename
            if not FileValidation.is_path_valid(str(file_path)):
                raise FileOperationError("delete", filename, "File not found or not accessible")

            file_path.unlink()
            logger.info(f"Deleted file: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Error deleting file {filename}: {str(e)}", exc_info=True)
            raise FileOperationError("delete", filename, str(e))

    def move_file(self, filename: str, source_dir: str, dest_dir: str) -> str:
        """
        Move a file between directories
        """
        try:
            source_path = self.base_upload_path / source_dir / filename
            dest_path = self.base_upload_path / dest_dir / filename

            if not FileValidation.is_path_valid(str(source_path)):
                raise FileOperationError("move", filename, "Source file not found")

            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source_path), str(dest_path))
            logger.info(f"Moved file from {source_path} to {dest_path}")
            
            return str(dest_path)

        except Exception as e:
            logger.error(f"Error moving file {filename}: {str(e)}", exc_info=True)
            raise FileOperationError("move", filename, str(e))

    def list_files(self, subdirectory: Optional[str] = None, pattern: Optional[str] = None) -> List[Dict[str, any]]:
        """
        List files in upload directory
        """
        try:
            directory = self.base_upload_path / (subdirectory or '')
            if not directory.exists():
                return []

            files = []
            for file_path in directory.iterdir():
                if file_path.is_file():
                    if pattern and not file_path.name.startswith(pattern):
                        continue
                    
                    files.append({
                        'filename': file_path.name,
                        'path': str(file_path),
                        'size': file_path.stat().st_size,
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    })
            
            return sorted(files, key=lambda x: x['modified'], reverse=True)

        except Exception as e:
            logger.error(f"Error listing files in {directory}: {str(e)}", exc_info=True)
            return []

    def get_file_info(self, filename: str, subdirectory: Optional[str] = None) -> Optional[Dict[str, any]]:
        """
        Get information about a specific file
        """
        try:
            file_path = self.base_upload_path / (subdirectory or '') / filename
            if not FileValidation.is_path_valid(str(file_path)):
                return None

            return {
                'filename': file_path.name,
                'path': str(file_path),
                'size': file_path.stat().st_size,
                'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                'extension': file_path.suffix.lower()
            }

        except Exception as e:
            logger.error(f"Error getting file info for {filename}: {str(e)}", exc_info=True)
            return None