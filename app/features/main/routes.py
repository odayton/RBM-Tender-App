from flask import render_template, jsonify, send_from_directory
from flask_login import login_required, current_user
from app.models import Deal, Company, Contact, Product
from . import main_bp

# Health check endpoint for Docker
@main_bp.route('/health')
def health():
    """Ultra-simple health check endpoint with no dependencies."""
    import json
    from datetime import datetime
    
    try:
        response_data = {
            'service': 'rbm-tender-app',
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'message': 'Application is running'
        }
        return json.dumps(response_data), 200, {'Content-Type': 'application/json'}
    
    except Exception as e:
        response_data = {
            'service': 'rbm-tender-app',
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'error': str(e)
        }
        return json.dumps(response_data), 503, {'Content-Type': 'application/json'}

# Favicon route to prevent 404 errors
@main_bp.route('/favicon.ico')
def favicon():
    """Handle favicon requests to prevent 404 errors."""
    return send_from_directory('static/images', 'rbm_logo.png')

# Route for the root URL /
@main_bp.route('/')
@login_required
def home():
    """
    Renders the main home page of the application.
    """
    # Get dashboard data for admin/manager users
    dashboard_data = {}
    
    if current_user.can_view_admin_panel():
        dashboard_data = {
            'deals': Deal.query.all(),
            'companies': Company.query.all(),
            'contacts': Contact.query.all(),
            'products': Product.query.all()
        }
        
        # Log dashboard data for debugging
        from app.core.core_logging import logger
        logger.info(f"Home page dashboard data - Products: {len(dashboard_data['products'])}, Deals: {len(dashboard_data['deals'])}, Companies: {len(dashboard_data['companies'])}, Contacts: {len(dashboard_data['contacts'])}")
    
    return render_template('home.html', **dashboard_data)