from flask import render_template
import logging

# Import the blueprint object that was created in the __init__.py file
from . import hydronic_heating_bp

logger = logging.getLogger(__name__)

@hydronic_heating_bp.route('/')
def index():
    """Renders the main hydronic heating page."""
    logger.info('Rendering hydronic heating page')
    return render_template('hydronic_heating/hydronic_heating.html')

@hydronic_heating_bp.route('/buffer-tanks')
def buffer_tanks():
    """Renders the buffer tanks page."""
    logger.info('Rendering buffer tanks page')
    return render_template('hydronic_heating/buffer_tanks.html')

@hydronic_heating_bp.route('/air-dirt-separators')
def air_dirt_separators():
    """Renders the air and dirt separators page."""
    logger.info('Rendering air and dirt separators page')
    return render_template('hydronic_heating/air_dirt_separators.html')

@hydronic_heating_bp.route('/expansion-tanks')
def expansion_tanks():
    """Renders the expansion tanks page."""
    logger.info('Rendering expansion tanks page')
    return render_template('hydronic_heating/expansion_tanks.html')