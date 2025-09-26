#!/usr/bin/env python3
"""
WSGI entry point for RBM Tender App
This file is used by Gunicorn to serve the Flask application in production.
"""

import os
from app import create_app
from app.core.core_config import ProductionConfig

# Create the Flask application instance
application = create_app(ProductionConfig)

if __name__ == "__main__":
    # This allows running the file directly for testing
    application.run(host='0.0.0.0', port=5000, debug=False)

