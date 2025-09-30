from flask import render_template, jsonify, send_from_directory
from flask_login import login_required, current_user
from app.models import Deal, Company, Contact, Product
from . import main_bp

# Health check endpoint for Docker
@main_bp.route('/health')
def health():
    """Enhanced health check endpoint that validates critical functionality."""
    try:
        from app.core.core_enhanced_health_checks import (
            check_model_schema_compatibility,
            check_model_methods_functionality,
            check_critical_endpoints_functionality,
            check_database_constraints,
            check_foreign_key_integrity
        )
        
        # Run enhanced health checks
        health_results = {
            'status': 'healthy',
            'service': 'rbm-tender-app',
            'timestamp': '2025-08-08T01:00:00Z',
            'checks': {}
        }
        
        # Schema compatibility check
        schema_result = check_model_schema_compatibility()
        health_results['checks']['schema_compatibility'] = schema_result
        if schema_result['status'] == 'unhealthy':
            health_results['status'] = 'unhealthy'
        
        # Model methods functionality check
        methods_result = check_model_methods_functionality()
        health_results['checks']['model_methods'] = methods_result
        if methods_result['status'] == 'unhealthy':
            health_results['status'] = 'unhealthy'
        
        # Critical endpoints functionality check
        endpoints_result = check_critical_endpoints_functionality()
        health_results['checks']['critical_endpoints'] = endpoints_result
        if endpoints_result['status'] == 'unhealthy':
            health_results['status'] = 'unhealthy'
        
        # Database constraints check
        constraints_result = check_database_constraints()
        health_results['checks']['database_constraints'] = constraints_result
        if constraints_result['status'] == 'unhealthy':
            health_results['status'] = 'unhealthy'
        
        # Foreign key integrity check
        fk_result = check_foreign_key_integrity()
        health_results['checks']['foreign_key_integrity'] = fk_result
        if fk_result['status'] == 'unhealthy':
            health_results['status'] = 'unhealthy'
        
        # Determine HTTP status code
        status_code = 200 if health_results['status'] == 'healthy' else 503
        
        return jsonify(health_results), status_code
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'service': 'rbm-tender-app',
            'error': str(e),
            'timestamp': '2025-08-08T01:00:00Z'
        }), 503

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