# app/utils/file_utils/storage_manager.py

import os
from flask import url_for, current_app
from typing import Optional

# In the future, this will be controlled by your config file. For now, it's hardcoded.
STORAGE_TYPE = "local" 

def get_storage_path() -> str:
    """
    Helper function to get the absolute path for the 'generated_data/graphs' folder.
    This makes the path construction robust and independent of the current working directory.
    """
    # current_app.root_path is the path to the 'app' package.
    # We go up one level ('..') to get to the project root.
    return os.path.abspath(os.path.join(current_app.root_path, '..', 'generated_data', 'graphs'))

def save_graph(file_data: bytes, filename: str) -> str:
    """
    Saves graph image data to the configured storage (currently local).

    Args:
        file_data (bytes): The raw image data to save.
        filename (str): The desired name for the file.

    Returns:
        str: The full absolute path to where the file was saved.
    """
    if STORAGE_TYPE == "local":
        storage_path = get_storage_path()
        # Ensure the target directory exists before trying to save.
        os.makedirs(storage_path, exist_ok=True)
        
        file_path = os.path.join(storage_path, filename)
        with open(file_path, 'wb') as f:
            f.write(file_data)
        return file_path
    else:
        # In the future, this is where you'd add S3 or other cloud logic.
        raise NotImplementedError("Cloud storage is not yet implemented.")

def get_graph_url(filename: str, _external: bool = True) -> str:
    """
    Returns a public-facing URL to view the stored graph.

    Args:
        filename (str): The name of the file.
        _external (bool): Whether to generate an absolute URL (e.g., with http://).

    Returns:
        str: The generated URL.
    """
    if STORAGE_TYPE == "local":
        # This endpoint name 'static_server.serve_generated_file' must match the one
        # we will create in our static file server blueprint.
        return url_for('static_server.serve_generated_file', filename=filename, _external=_external)
    else:
        # In the future, this would return an S3 URL.
        raise NotImplementedError("Cloud storage is not yet implemented.")

def delete_graph(filename: str) -> bool:
    """
    Deletes a graph from storage.

    Args:
        filename (str): The name of the file to delete.

    Returns:
        bool: True if deletion was successful, False otherwise.
    """
    if STORAGE_TYPE == "local":
        try:
            file_path = os.path.join(get_storage_path(), filename)
            os.remove(file_path)
            # You might want to add logging here in the future
            return True
        except (OSError, FileNotFoundError):
            # Log the error if the file doesn't exist or can't be deleted
            return False
    else:
        raise NotImplementedError("Cloud storage is not yet implemented.")