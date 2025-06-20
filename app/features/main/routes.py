from flask import redirect, url_for
from . import main_bp

# Route for the root URL '/'
@main_bp.route('/')
def home():
    """
    Redirects the root URL directly to the main deals page for development.
    """
    return redirect(url_for('deals.list_deals'))