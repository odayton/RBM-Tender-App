from flask import Blueprint, render_template, current_app
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

hydraulic_bp = Blueprint('hydraulic', __name__)

@hydraulic_bp.route('/')
def hydraulic():
    logger.info('Rendering hydraulic main page')
    return render_template('hydraulic/hydraulic.html')
