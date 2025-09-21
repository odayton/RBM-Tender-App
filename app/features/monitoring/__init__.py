"""
Monitoring Feature Module - Health checks, metrics, and monitoring endpoints
"""

from flask import Blueprint

monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/monitoring')

from . import routes

