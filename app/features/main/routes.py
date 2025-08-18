from flask import render_template, jsonify
from flask_login import login_required, current_user
from app.models import Deal, Company, Contact, Product
from . import main_bp

# Health check endpoint for Docker
@main_bp.route('/health')
def health():
    """Health check endpoint for Docker and load balancers."""
    return jsonify({
        'status': 'healthy',
        'service': 'rbm-tender-app',
        'timestamp': '2025-08-08T01:00:00Z'
    }), 200

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
    
    return render_template('home.html', **dashboard_data)