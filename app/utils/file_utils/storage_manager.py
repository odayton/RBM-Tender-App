import os
from pathlib import Path
from flask import url_for, current_app
from typing import Optional

from app.core.core_logging import logger
from app.core.core_errors import FileOperationError

class StorageManager:
    """
    Manages storage operations for generated files like graphs.
    Designed to be extensible for different storage backends (e.g., local, S3).
    """

    def __init__(self, storage_type: str, local_path: str = 'generated_data'):
        """
        Initializes the StorageManager.

        Args:
            storage_type (str): The type of storage to use ('local', 's3', etc.).
            local_path (str): The base directory for local storage, relative to the instance path.
        """
        self.storage_type = storage_type
        if self.storage_type == 'local':
            # Use the app's instance path for robust, self-contained storage
            self.base_path = Path(current_app.instance_path) / local_path
        else:
            # Placeholder for future cloud storage paths
            self.base_path = Path('.')
        
        logger.info(f"StorageManager initialized with type '{self.storage_type}' and base path '{self.base_path}'")

    def _get_storage_path(self, subdirectory: str) -> Path:
        """
        Constructs and ensures the existence of a subdirectory within the base storage path.
        
        Args:
            subdirectory (str): The target subdirectory (e.g., 'graphs').

        Returns:
            Path: The absolute path to the subdirectory.
        """
        path = self.base_path / subdirectory
        try:
            path.mkdir(parents=True, exist_ok=True)
            return path
        except OSError as e:
            logger.error(f"Could not create storage directory {path}: {e}", exc_info=True)
            raise FileOperationError("init_storage", str(path), f"Could not create directory: {e}")


    def save_file(self, file_data: bytes, filename: str, subdirectory: str) -> str:
        """
        Saves file data to the configured storage.

        Args:
            file_data (bytes): The raw data to save.
            filename (str): The desired name for the file.
            subdirectory (str): The subdirectory to save the file in (e.g., 'graphs').

        Returns:
            str: The full absolute path to where the file was saved.
        """
        if self.storage_type == "local":
            try:
                storage_path = self._get_storage_path(subdirectory)
                file_path = storage_path / filename
                
                with open(file_path, 'wb') as f:
                    f.write(file_data)
                
                logger.info(f"Successfully saved file to {file_path}")
                return str(file_path)
            except Exception as e:
                logger.error(f"Failed to save file '{filename}' to {storage_path}: {e}", exc_info=True)
                raise FileOperationError("save", filename, str(e))
        else:
            raise NotImplementedError("Cloud storage is not yet implemented.")


    def get_file_url(self, filename: str, subdirectory: str, _external: bool = True) -> str:
        """
        Returns a public-facing URL to view a stored file.

        Args:
            filename (str): The name of the file.
            subdirectory (str): The subdirectory where the file is stored.
            _external (bool): Whether to generate an absolute URL.

        Returns:
            str: The generated URL.
        """
        if self.storage_type == "local":
            # The endpoint 'static_server.serve_generated_file' must match the blueprint endpoint.
            # The route itself will need to know how to map `subdirectory` and `filename` to a path.
            return url_for('static_server.serve_generated_file', subdirectory=subdirectory, filename=filename, _external=_external)
        else:
            raise NotImplementedError("Cloud storage is not yet implemented.")


    def delete_file(self, filename: str, subdirectory: str) -> bool:
        """
        Deletes a file from storage.

        Args:
            filename (str): The name of the file to delete.
            subdirectory (str): The subdirectory where the file is stored.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        if self.storage_type == "local":
            try:
                # We don't create the directory on delete, just resolve the path
                storage_path = self.base_path / subdirectory
                file_path = storage_path / filename
                
                if not file_path.is_file():
                    logger.warning(f"Attempted to delete non-existent file: {file_path}")
                    return False
                
                file_path.unlink()
                logger.info(f"Successfully deleted file: {file_path}")
                return True
            except OSError as e:
                logger.error(f"Error deleting file {file_path}: {e}", exc_info=True)
                return False
        else:
            raise NotImplementedError("Cloud storage is not yet implemented.")