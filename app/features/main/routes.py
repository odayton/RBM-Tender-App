from flask import render_template
from . import main_bp

# Route for the root URL /
@main_bp.route('/')
def home():
    """
    Renders the main home page of the application.
    """
    return render_template('home.html')