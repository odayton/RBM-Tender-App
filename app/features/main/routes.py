from flask import redirect, url_for
# This imports the main_bp object from the __init__.py file in the same folder.
from . import main_bp

@main_bp.route('/')
def home():
    """
    Handles the root URL of the site.
    Redirects to the main deals listing page.
    """
    # The endpoint name is 'blueprint_name.function_name'
    return redirect(url_for('quotes.list_deals'))