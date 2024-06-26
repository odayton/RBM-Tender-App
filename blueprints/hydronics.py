# blueprints/hydronics.py

from flask import Blueprint, render_template

hydronics_bp = Blueprint('hydronics', __name__)

@hydronics_bp.route('/')
def hydronics():
    return render_template('hydronics.html')

@hydronics_bp.route('/buffer_tanks')
def buffer_tanks():
    return render_template('buffer_tanks.html')

@hydronics_bp.route('/air_dirt_separators')
def air_dirt_separators():
    return render_template('air_dirt_separators.html')

@hydronics_bp.route('/expansion_tanks')
def expansion_tanks():
    return render_template('expansion_tanks.html')
