"""
File validation utilities for handling various file types in the application.
"""
import os
from typing import Set

# Define allowed extensions as sets for efficient lookup
ALLOWED_EXCEL_EXTENSIONS: Set[str] = {'xlsx', 'xls'}
ALLOWED_PDF_EXTENSIONS: Set[str] = {'pdf'}
ALLOWED_ZIP_EXTENSIONS: Set[str] = {'zip'}
ALL_ALLOWED_EXTENSIONS: Set[str] = ALLOWED_EXCEL_EXTENSIONS | ALLOWED_PDF_EXTENSIONS | ALLOWED_ZIP_EXTENSIONS

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

def allowed_file(filename: str) -> bool:
    """
    Check if uploaded file has an allowed extension.
    Allowed extensions are Excel files (.xlsx, .xls) and PDF files (.pdf)
    
    Args:
        filename (str): Name of the file to check
        
    Returns:
        bool: True if file extension is allowed, False otherwise
    """
    print(f"Checking if file is allowed: {filename}")
    if not filename:
        print("No filename provided")
        return False
        
    extension = get_file_extension(filename)
    allowed = extension in (ALLOWED_EXCEL_EXTENSIONS | ALLOWED_PDF_EXTENSIONS)
    
    print(f"File extension: {extension}")
    print(f"File is allowed: {allowed}")
    return allowed

def allowed_excel_file(filename: str) -> bool:
    """
    Check if file is an Excel file (.xlsx or .xls).
    
    Args:
        filename (str): Name of the file to check
        
    Returns:
        bool: True if file is an Excel file, False otherwise
    """
    print(f"Checking if file is Excel: {filename}")
    if not filename:
        print("No filename provided")
        return False
        
    extension = get_file_extension(filename)
    allowed = extension in ALLOWED_EXCEL_EXTENSIONS
    
    print(f"File extension: {extension}")
    print(f"File is Excel: {allowed}")
    return allowed

def allowed_pdf_file(filename: str) -> bool:
    """
    Check if file is a PDF file.
    
    Args:
        filename (str): Name of the file to check
        
    Returns:
        bool: True if file is a PDF file, False otherwise
    """
    print(f"Checking if file is PDF: {filename}")
    if not filename:
        print("No filename provided")
        return False
        
    extension = get_file_extension(filename)
    allowed = extension in ALLOWED_PDF_EXTENSIONS
    
    print(f"File extension: {extension}")
    print(f"File is PDF: {allowed}")
    return allowed

def allowed_zip_file(filename: str) -> bool:
    """
    Check if file is a ZIP archive.
    
    Args:
        filename (str): Name of the file to check
        
    Returns:
        bool: True if file is a ZIP archive, False otherwise
    """
    print(f"Checking if file is ZIP: {filename}")
    if not filename:
        print("No filename provided")
        return False
        
    extension = get_file_extension(filename)
    allowed = extension in ALLOWED_ZIP_EXTENSIONS
    
    print(f"File extension: {extension}")
    print(f"File is ZIP: {allowed}")
    return allowed

def validate_file_path(file_path: str) -> bool:
    """
    Validate that a file path exists and is accessible.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        bool: True if file exists and is accessible, False otherwise
    """
    print(f"Validating file path: {file_path}")
    exists = os.path.exists(file_path)
    is_file = os.path.isfile(file_path)
    is_readable = os.access(file_path, os.R_OK) if exists else False
    
    print(f"File exists: {exists}")
    print(f"Is file: {is_file}")
    print(f"Is readable: {is_readable}")
    
    return exists and is_file and is_readable

def get_safe_filename(filename: str) -> str:
    """
    Get a safe version of the filename, removing any potentially unsafe characters.
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Safe version of the filename
    """
    # Remove any directory path components
    filename = os.path.basename(filename)
    
    # Replace potentially unsafe characters
    safe_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._")
    filename = ''.join(c if c in safe_chars else '_' for c in filename)
    
    return filename