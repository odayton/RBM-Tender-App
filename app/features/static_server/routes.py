# app/features/static_server/routes.py

import os
from flask import Blueprint, send_from_directory, current_app, abort

# Define the blueprint. The name 'static_server' is what we use in url_for().
static_server_bp = Blueprint('static_server', __name__)

@static_server_bp.route('/generated/<path:filename>')
def serve_generated_file(filename):
    """
    Serves files from the root /generated_data/graphs/ folder.
    This route is used to make generated images viewable in the browser.
    """
    # Securely construct the absolute path to the directory where graphs are stored.
    directory = os.path.abspath(os.path.join(current_app.root_path, '..', 'generated_data', 'graphs'))
    
    # Security check: ensure the file actually exists within our directory.
    # This prevents users from trying to access files outside this folder.
    file_path = os.path.join(directory, filename)
    if not os.path.isfile(file_path):
        abort(404)  # Return a "Not Found" error if the file doesn't exist.
        
    # Use Flask's safe file sending utility.
    return send_from_directory(directory, filename)