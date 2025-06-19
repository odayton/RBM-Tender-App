from flask import render_template
import logging

# Import the blueprint from the local package __init__.py
from . import hydronics_bp

logger = logging.getLogger(__name__)

@hydronics_bp.route('/hydronics')
def hydronics():
    """Renders the main hydronics page."""
    logger.info('Rendering hydronics page')
    return render_template('hydronics/hydronics.html')

@hydronics_bp.route('/buffer-tanks')
def buffer_tanks():
    """Renders the buffer tanks page."""
    logger.info('Rendering buffer tanks page')
    return render_template('hydronics/buffer_tanks.html')

@hydronics_bp.route('/air-dirt-separators')
def air_dirt_separators():
    """Renders the air and dirt separators page."""
    logger.info('Rendering air and dirt separators page')
    return render_template('hydronics/air_dirt_separators.html')

@hydronics_bp.route('/expansion-tanks')
def expansion_tanks():
    """Renders the expansion tanks page."""
    logger.info('Rendering expansion tanks page')
    return render_template('hydronics/expansion_tanks.html')