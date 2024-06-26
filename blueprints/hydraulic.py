# blueprints/hydraulic.py

from flask import Blueprint, render_template

hydraulic_bp = Blueprint('hydraulic', __name__)

@hydraulic_bp.route('/')
def hydraulic():
    return render_template('hydraulic.html')
