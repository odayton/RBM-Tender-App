from flask import Blueprint, render_template
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

hydronics_bp = Blueprint('hydronics', __name__)

@hydronics_bp.route('/')
def hydronics():
    logger.info('Rendering hydronics page')
    return render_template('hydronics/hydronics.html')

@hydronics_bp.route('/buffer_tanks')
def buffer_tanks():
    logger.info('Rendering buffer tanks page')
    return render_template('hydronics/buffer_tanks.html')

@hydronics_bp.route('/air_dirt_separators')
def air_dirt_separators():
    logger.info('Rendering air and dirt separators page')
    return render_template('hydronics/air_dirt_separators.html')

@hydronics_bp.route('/expansion_tanks')
def expansion_tanks():
    logger.info('Rendering expansion tanks page')
    return render_template('hydronics/expansion_tanks.html')
