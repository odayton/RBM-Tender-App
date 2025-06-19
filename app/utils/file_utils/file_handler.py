import os
import shutil
from typing import Optional, Dict, List
from werkzeug.utils import secure_filename
from datetime import datetime
import logging
from pathlib import Path

from app.core.core_errors import FileOperationError
from .file_validation import (
    allowed_file,
    get_safe_filename,
    validate_file_path
)

logger = logging.getLogger(__name__)

class FileHandler:
    """Handles file operations for the application"""
    
    def __init__(self, base_upload_path: str):
        self.base_upload_path = base_upload_path
        self.ensure_upload_directories()
    
    def ensure_upload_directories(self) -> None:
        """Create necessary upload directories if they don't exist"""
        directories = [
            self.base_upload_path,
            os.path.join(self.base_upload_path, 'tech-data'),
            os.path.join(self.base_upload_path, 'others'),
            os.path.join(self.base_upload_path, 'temp')
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Ensured directory exists: {directory}")

    def save_file(self, file, subdirectory: str = None) -> Dict[str, str]:
        """
        Save uploaded file to the appropriate directory
        
        Args:
            file: FileStorage object
            subdirectory: Optional subdirectory within base upload path
            
        Returns:
            Dict containing file information
            
        Raises:
            FileOperationError: If file save fails
        """
        try:
            if not file:
                raise FileOperationError("save", "none", "No file provided")

            filename = secure_filename(file.filename)
            if not filename:
                raise FileOperationError("save", "none", "Invalid filename")

            if not allowed_file(filename):
                raise FileOperationError("save", filename, "File type not allowed")

            # Create timestamped filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            safe_filename = get_safe_filename(timestamp + filename)

            # Determine save path
            save_directory = self.base_upload_path
            if subdirectory:
                save_directory = os.path.join(save_directory, subdirectory)
                os.makedirs(save_directory, exist_ok=True)

            file_path = os.path.join(save_directory, safe_filename)
            file.save(file_path)

            return {
                'filename': safe_filename,
                'original_filename': filename,
                'path': file_path,
                'size': os.path.getsize(file_path),
                'timestamp': timestamp.rstrip('_')
            }

        except Exception as e:
            logger.error(f"Error saving file {filename if 'filename' in locals() else 'unknown'}: {str(e)}")
            raise FileOperationError("save", filename if 'filename' in locals() else 'unknown', str(e))

    def delete_file(self, filename: str, subdirectory: Optional[str] = None) -> bool:
        """
        Delete a file from the upload directory
        
        Args:
            filename: Name of file to delete
            subdirectory: Optional subdirectory within base upload path
            
        Returns:
            bool: True if file was deleted successfully
            
        Raises:
            FileOperationError: If file deletion fails
        """
        try:
            file_path = os.path.join(self.base_upload_path, subdirectory or '', filename)
            if not validate_file_path(file_path):
                raise FileOperationError("delete", filename, "File not found")

            os.remove(file_path)
            logger.info(f"Deleted file: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Error deleting file {filename}: {str(e)}")
            raise FileOperationError("delete", filename, str(e))

    def move_file(self, filename: str, source_dir: str, dest_dir: str) -> str:
        """
        Move a file between directories
        
        Args:
            filename: Name of file to move
            source_dir: Source directory
            dest_dir: Destination directory
            
        Returns:
            str: New file path
            
        Raises:
            FileOperationError: If file move fails
        """
        try:
            source_path = os.path.join(self.base_upload_path, source_dir, filename)
            dest_path = os.path.join(self.base_upload_path, dest_dir, filename)

            if not validate_file_path(source_path):
                raise FileOperationError("move", filename, "Source file not found")

            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.move(source_path, dest_path)
            logger.info(f"Moved file from {source_path} to {dest_path}")
            
            return dest_path

        except Exception as e:
            logger.error(f"Error moving file {filename}: {str(e)}")
            raise FileOperationError("move", filename, str(e))

    def list_files(self, subdirectory: Optional[str] = None, pattern: Optional[str] = None) -> List[Dict[str, str]]:
        """
        List files in upload directory
        
        Args:
            subdirectory: Optional subdirectory to list
            pattern: Optional filename pattern to match
            
        Returns:
            List of dictionaries containing file information
        """
        try:
            directory = os.path.join(self.base_upload_path, subdirectory or '')
            if not os.path.exists(directory):
                return []

            files = []
            for filename in os.listdir(directory):
                if pattern and not filename.startswith(pattern):
                    continue

                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path):
                    files.append({
                        'filename': filename,
                        'path': file_path,
                        'size': os.path.getsize(file_path),
                        'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                    })

            return sorted(files, key=lambda x: x['modified'], reverse=True)

        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            return []

    def get_file_info(self, filename: str, subdirectory: Optional[str] = None) -> Optional[Dict[str, str]]:
        """
        Get information about a specific file
        
        Args:
            filename: Name of file
            subdirectory: Optional subdirectory containing the file
            
        Returns:
            Dict containing file information or None if file not found
        """
        try:
            file_path = os.path.join(self.base_upload_path, subdirectory or '', filename)
            if not validate_file_path(file_path):
                return None

            return {
                'filename': filename,
                'path': file_path,
                'size': os.path.getsize(file_path),
                'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
                'extension': os.path.splitext(filename)[1].lower()
            }

        except Exception as e:
            logger.error(f"Error getting file info for {filename}: {str(e)}")
            return None