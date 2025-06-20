"""
File validation utilities for handling various file types in the application.
"""
import os
from typing import Set, Tuple
from app.core.core_logging import logger

class FileValidation:
    """A collection of static methods for validating files."""

    ALLOWED_EXCEL_EXTENSIONS: Set[str] = {'xlsx', 'xls'}
    ALLOWED_PDF_EXTENSIONS: Set[str] = {'pdf'}
    ALLOWED_ZIP_EXTENSIONS: Set[str] = {'zip'}
    ALL_ALLOWED_EXTENSIONS: Set[str] = ALLOWED_EXCEL_EXTENSIONS | ALLOWED_PDF_EXTENSIONS | ALLOWED_ZIP_EXTENSIONS

    @staticmethod
    def get_file_extension(filename: str) -> str:
        """
        Extract the file extension from a filename.
        
        Args:
            filename (str): Name of the file
            
        Returns:
            str: Lowercase extension without the dot, or empty string if no extension
        """
        if '.' not in filename:
            return ''
        return filename.rsplit('.', 1)[1].lower()

    @classmethod
    def is_allowed(cls, filename: str, allowed_extensions: Set[str] = None) -> Tuple[bool, str]:
        """
        Check if an uploaded file has an allowed extension.

        Args:
            filename (str): Name of the file to check.
            allowed_extensions (Set[str], optional): A set of allowed extensions. 
                                                     Defaults to all allowed extensions.

        Returns:
            Tuple[bool, str]: (True/False, message)
        """
        logger.debug(f"Validating file: {filename}")
        if not filename:
            logger.warning("Validation failed: No filename provided.")
            return False, "No file selected."

        if allowed_extensions is None:
            allowed_extensions = cls.ALL_ALLOWED_EXTENSIONS
            
        extension = cls.get_file_extension(filename)
        if extension in allowed_extensions:
            logger.debug(f"File validation successful for {filename} with extension '{extension}'.")
            return True, "File type is allowed."
        else:
            logger.warning(f"Validation failed: Disallowed file type '{extension}' for file {filename}.")
            return False, f"Invalid file type: '{extension}'. Allowed types are: {', '.join(allowed_extensions)}"

    @staticmethod
    def is_path_valid(file_path: str) -> bool:
        """
        Validate that a file path exists, is a file, and is readable.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            bool: True if file exists and is accessible, False otherwise
        """
        logger.debug(f"Validating file path: {file_path}")
        exists = os.path.exists(file_path)
        is_file = os.path.isfile(file_path)
        is_readable = os.access(file_path, os.R_OK) if exists else False
        
        if exists and is_file and is_readable:
            logger.debug("File path validation successful.")
            return True
        else:
            logger.error(f"File path validation failed for {file_path}. Exists: {exists}, IsFile: {is_file}, IsReadable: {is_readable}")
            return False

    @staticmethod
    def get_safe_filename(filename: str) -> str:
        """
        Get a safe version of the filename, removing any potentially unsafe characters.
        
        Args:
            filename (str): Original filename
            
        Returns:
            str: Safe version of the filename
        """
        # Remove any directory path components
        safe_filename = os.path.basename(filename)
        
        # Replace potentially unsafe characters
        safe_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._")
        safe_filename = ''.join(c if c in safe_chars else '_' for c in safe_filename)
        
        return safe_filename