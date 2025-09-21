"""
Core API Documentation Module - OpenAPI/Swagger Integration
"""

import json
import yaml
from typing import Dict, Any, List, Optional
from flask import Blueprint, jsonify, render_template, request, current_app
from flask_restx import Api, Resource, fields, Namespace
from functools import wraps
import structlog

logger = structlog.get_logger(__name__)

# Create API documentation blueprint
api_docs_bp = Blueprint('api_docs', __name__, url_prefix='/api/docs')

# Initialize Flask-RESTX API
api = Api(
    api_docs_bp,
    version='1.0.0',
    title='RBM Tender App API',
    description='Comprehensive API for the RBM Tender Application',
    doc='/swagger/',  # Swagger UI endpoint
    prefix='/api/v1'
)

# Create namespaces for different API sections
deals_ns = Namespace('deals', description='Deal management operations')
quotes_ns = Namespace('quotes', description='Quote management operations')
customers_ns = Namespace('customers', description='Customer management operations')
products_ns = Namespace('products', description='Product catalog operations')
auth_ns = Namespace('auth', description='Authentication operations')
admin_ns = Namespace('admin', description='Administrative operations')
monitoring_ns = Namespace('monitoring', description='Monitoring and health check operations')

# Add namespaces to API
api.add_namespace(deals_ns)
api.add_namespace(quotes_ns)
api.add_namespace(customers_ns)
api.add_namespace(products_ns)
api.add_namespace(auth_ns)
api.add_namespace(admin_ns)
api.add_namespace(monitoring_ns)

# Define common response models
error_model = api.model('Error', {
    'error': fields.String(required=True, description='Error message'),
    'code': fields.Integer(description='Error code'),
    'details': fields.String(description='Additional error details')
})

success_model = api.model('Success', {
    'message': fields.String(required=True, description='Success message'),
    'data': fields.Raw(description='Response data')
})

# Deal models
deal_model = api.model('Deal', {
    'id': fields.Integer(required=True, description='Deal ID'),
    'project_name': fields.String(required=True, description='Project name'),
    'deal_type': fields.String(required=True, description='Deal type', enum=['HVAC', 'PLUMBING', 'HYDRONIC_HEATING', 'DATA_CENTRES', 'MERCHANT', 'WHOLESALER', 'OEM']),
    'stage': fields.String(required=True, description='Deal stage', enum=['SALES_LEAD', 'QUOTED', 'NEGOTIATION', 'CLOSED_WON', 'CLOSED_LOST']),
    'state': fields.String(required=True, description='Australian state', enum=['NSW', 'VIC', 'QLD', 'WA', 'SA', 'TAS', 'NT', 'ACT']),
    'owner_id': fields.Integer(required=True, description='Deal owner user ID'),
    'created_at': fields.DateTime(description='Creation timestamp'),
    'updated_at': fields.DateTime(description='Last update timestamp'),
    'companies': fields.List(fields.Nested(api.model('Company', {
        'id': fields.Integer(),
        'company_name': fields.String()
    }))),
    'contacts': fields.List(fields.Nested(api.model('Contact', {
        'id': fields.Integer(),
        'first_name': fields.String(),
        'last_name': fields.String(),
        'email': fields.String()
    })))
})

deal_create_model = api.model('DealCreate', {
    'project_name': fields.String(required=True, description='Project name'),
    'deal_type': fields.String(required=True, description='Deal type'),
    'state': fields.String(required=True, description='Australian state'),
    'company_id': fields.Integer(description='Associated company ID'),
    'contact_id': fields.Integer(description='Associated contact ID')
})

# Quote models
quote_model = api.model('Quote', {
    'id': fields.Integer(required=True, description='Quote ID'),
    'deal_id': fields.Integer(required=True, description='Associated deal ID'),
    'recipient_id': fields.Integer(required=True, description='Quote recipient ID'),
    'revision': fields.Integer(required=True, description='Quote revision number'),
    'notes': fields.String(description='Quote notes'),
    'created_at': fields.DateTime(description='Creation timestamp'),
    'options': fields.List(fields.Nested(api.model('QuoteOption', {
        'id': fields.Integer(),
        'name': fields.String(),
        'freight_charge': fields.Float(),
        'line_items': fields.List(fields.Nested(api.model('QuoteLineItem', {
            'id': fields.Integer(),
            'product_id': fields.Integer(),
            'quantity': fields.Integer(),
            'unit_price': fields.Float(),
            'total_price': fields.Float()
        })))
    })))
})

# Product models
product_model = api.model('Product', {
    'id': fields.Integer(required=True, description='Product ID'),
    'sku': fields.String(required=True, description='Product SKU'),
    'name': fields.String(required=True, description='Product name'),
    'description': fields.String(description='Product description'),
    'category': fields.String(description='Product category'),
    'unit_price': fields.Float(description='Unit price'),
    'unit': fields.String(description='Unit of measurement'),
    'is_active': fields.Boolean(description='Product active status')
})

# Company models
company_model = api.model('Company', {
    'id': fields.Integer(required=True, description='Company ID'),
    'company_name': fields.String(required=True, description='Company name'),
    'abn': fields.String(description='Australian Business Number'),
    'address': fields.String(description='Company address'),
    'city': fields.String(description='City'),
    'state': fields.String(description='State'),
    'postcode': fields.String(description='Postcode'),
    'phone': fields.String(description='Phone number'),
    'email': fields.String(description='Email address'),
    'website': fields.String(description='Website URL'),
    'created_at': fields.DateTime(description='Creation timestamp')
})

# Contact models
contact_model = api.model('Contact', {
    'id': fields.Integer(required=True, description='Contact ID'),
    'first_name': fields.String(required=True, description='First name'),
    'last_name': fields.String(required=True, description='Last name'),
    'email': fields.String(required=True, description='Email address'),
    'phone': fields.String(description='Phone number'),
    'position': fields.String(description='Job position'),
    'company_id': fields.Integer(description='Associated company ID'),
    'created_at': fields.DateTime(description='Creation timestamp')
})

# User models
user_model = api.model('User', {
    'id': fields.Integer(required=True, description='User ID'),
    'email': fields.String(required=True, description='Email address'),
    'first_name': fields.String(description='First name'),
    'last_name': fields.String(description='Last name'),
    'is_active': fields.Boolean(description='User active status'),
    'roles': fields.List(fields.String(description='User roles')),
    'last_login': fields.DateTime(description='Last login timestamp'),
    'created_at': fields.DateTime(description='Creation timestamp')
})

# Health check models
health_model = api.model('Health', {
    'status': fields.String(required=True, description='Overall health status'),
    'timestamp': fields.DateTime(description='Health check timestamp'),
    'checks': fields.Raw(description='Individual check results'),
    'version': fields.String(description='Application version')
})

# Metrics models
metrics_model = api.model('Metrics', {
    'http_requests_total': fields.Integer(description='Total HTTP requests'),
    'deals_created_total': fields.Integer(description='Total deals created'),
    'quotes_generated_total': fields.Integer(description='Total quotes generated'),
    'users_active': fields.Integer(description='Currently active users'),
    'database_connections': fields.Integer(description='Active database connections'),
    'cache_hit_rate': fields.Float(description='Cache hit rate percentage'),
    'memory_usage_bytes': fields.Integer(description='Memory usage in bytes'),
    'disk_usage_bytes': fields.Integer(description='Disk usage in bytes')
})

# API Documentation Routes

@api_docs_bp.route('/openapi.json')
def openapi_json():
    """Return OpenAPI specification in JSON format."""
    try:
        # Get the OpenAPI spec from Flask-RESTX
        spec = api.specs['v1']
        return jsonify(spec)
    except Exception as e:
        logger.error("Failed to generate OpenAPI JSON", error=str(e))
        return jsonify({'error': 'Failed to generate OpenAPI specification'}), 500

@api_docs_bp.route('/openapi.yaml')
def openapi_yaml():
    """Return OpenAPI specification in YAML format."""
    try:
        # Get the OpenAPI spec from Flask-RESTX
        spec = api.specs['v1']
        yaml_content = yaml.dump(spec, default_flow_style=False)
        return yaml_content, 200, {'Content-Type': 'application/x-yaml'}
    except Exception as e:
        logger.error("Failed to generate OpenAPI YAML", error=str(e))
        return jsonify({'error': 'Failed to generate OpenAPI specification'}), 500

@api_docs_bp.route('/redoc')
def redoc():
    """Serve ReDoc documentation interface."""
    return render_template('api/redoc.html')

# Deal API Endpoints

@deals_ns.route('/')
class DealList(Resource):
    @deals_ns.doc('list_deals')
    @deals_ns.marshal_list_with(deal_model)
    @deals_ns.param('search', 'Search query for deals')
    @deals_ns.param('stage', 'Filter by deal stage')
    @deals_ns.param('deal_type', 'Filter by deal type')
    @deals_ns.param('page', 'Page number for pagination')
    @deals_ns.param('per_page', 'Number of items per page')
    def get(self):
        """Get a list of all deals with optional filtering and pagination."""
        # This would integrate with your actual deal listing logic
        return {'message': 'Deal list endpoint - implementation needed'}

    @deals_ns.doc('create_deal')
    @deals_ns.expect(deal_create_model)
    @deals_ns.marshal_with(deal_model, code=201)
    @deals_ns.marshal_with(error_model, code=400)
    def post(self):
        """Create a new deal."""
        # This would integrate with your actual deal creation logic
        return {'message': 'Deal creation endpoint - implementation needed'}, 201

@deals_ns.route('/<int:deal_id>')
class DealDetail(Resource):
    @deals_ns.doc('get_deal')
    @deals_ns.marshal_with(deal_model)
    @deals_ns.marshal_with(error_model, code=404)
    def get(self, deal_id):
        """Get a specific deal by ID."""
        return {'message': f'Deal {deal_id} detail endpoint - implementation needed'}

    @deals_ns.doc('update_deal')
    @deals_ns.expect(deal_create_model)
    @deals_ns.marshal_with(deal_model)
    @deals_ns.marshal_with(error_model, code=400)
    def put(self, deal_id):
        """Update a specific deal."""
        return {'message': f'Deal {deal_id} update endpoint - implementation needed'}

    @deals_ns.doc('delete_deal')
    @deals_ns.marshal_with(success_model)
    @deals_ns.marshal_with(error_model, code=404)
    def delete(self, deal_id):
        """Delete a specific deal."""
        return {'message': f'Deal {deal_id} deleted'}

# Quote API Endpoints

@quotes_ns.route('/deal/<int:deal_id>')
class DealQuotes(Resource):
    @quotes_ns.doc('list_deal_quotes')
    @quotes_ns.marshal_list_with(quote_model)
    def get(self, deal_id):
        """Get all quotes for a specific deal."""
        return {'message': f'Quotes for deal {deal_id} - implementation needed'}

@quotes_ns.route('/<int:quote_id>/pdf')
class QuotePDF(Resource):
    @quotes_ns.doc('generate_quote_pdf')
    def get(self, quote_id):
        """Generate and return a quote PDF."""
        return {'message': f'PDF generation for quote {quote_id} - implementation needed'}

# Product API Endpoints

@products_ns.route('/')
class ProductList(Resource):
    @products_ns.doc('list_products')
    @products_ns.marshal_list_with(product_model)
    @products_ns.param('search', 'Search query for products')
    @products_ns.param('category', 'Filter by product category')
    @products_ns.param('active_only', 'Show only active products')
    def get(self):
        """Get a list of all products with optional filtering."""
        return {'message': 'Product list endpoint - implementation needed'}

@products_ns.route('/<int:product_id>')
class ProductDetail(Resource):
    @products_ns.doc('get_product')
    @products_ns.marshal_with(product_model)
    def get(self, product_id):
        """Get a specific product by ID."""
        return {'message': f'Product {product_id} detail - implementation needed'}

# Customer API Endpoints

@customers_ns.route('/companies')
class CompanyList(Resource):
    @customers_ns.doc('list_companies')
    @customers_ns.marshal_list_with(company_model)
    @customers_ns.param('search', 'Search query for companies')
    def get(self):
        """Get a list of all companies."""
        return {'message': 'Company list endpoint - implementation needed'}

@customers_ns.route('/contacts')
class ContactList(Resource):
    @customers_ns.doc('list_contacts')
    @customers_ns.marshal_list_with(contact_model)
    @customers_ns.param('company_id', 'Filter by company ID')
    @customers_ns.param('search', 'Search query for contacts')
    def get(self):
        """Get a list of all contacts."""
        return {'message': 'Contact list endpoint - implementation needed'}

# Authentication API Endpoints

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.doc('user_login')
    @auth_ns.expect(api.model('LoginRequest', {
        'email': fields.String(required=True, description='User email'),
        'password': fields.String(required=True, description='User password'),
        'remember_me': fields.Boolean(description='Remember login session')
    }))
    @auth_ns.marshal_with(api.model('LoginResponse', {
        'access_token': fields.String(description='JWT access token'),
        'refresh_token': fields.String(description='JWT refresh token'),
        'user': fields.Nested(user_model)
    }))
    @auth_ns.marshal_with(error_model, code=401)
    def post(self):
        """Authenticate user and return access token."""
        return {'message': 'Login endpoint - implementation needed'}

@auth_ns.route('/logout')
class Logout(Resource):
    @auth_ns.doc('user_logout')
    @auth_ns.marshal_with(success_model)
    def post(self):
        """Logout user and invalidate session."""
        return {'message': 'Logout successful'}

# Monitoring API Endpoints

@monitoring_ns.route('/health')
class HealthCheck(Resource):
    @monitoring_ns.doc('health_check')
    @monitoring_ns.marshal_with(health_model)
    def get(self):
        """Get application health status."""
        # This would integrate with your health check system
        return {
            'status': 'healthy',
            'timestamp': '2025-01-15T10:30:00Z',
            'version': '1.0.0',
            'checks': {
                'database': {'status': 'healthy'},
                'redis': {'status': 'healthy'},
                'disk_space': {'status': 'healthy'}
            }
        }

@monitoring_ns.route('/metrics')
class Metrics(Resource):
    @monitoring_ns.doc('get_metrics')
    @monitoring_ns.marshal_with(metrics_model)
    def get(self):
        """Get application metrics."""
        # This would integrate with your metrics system
        return {
            'http_requests_total': 1250,
            'deals_created_total': 45,
            'quotes_generated_total': 120,
            'users_active': 8,
            'database_connections': 3,
            'cache_hit_rate': 85.5,
            'memory_usage_bytes': 256000000,
            'disk_usage_bytes': 1024000000
        }

# Admin API Endpoints

@admin_ns.route('/users')
class UserList(Resource):
    @admin_ns.doc('list_users')
    @admin_ns.marshal_list_with(user_model)
    def get(self):
        """Get a list of all users (admin only)."""
        return {'message': 'User list endpoint - implementation needed'}

@admin_ns.route('/users/<int:user_id>')
class UserDetail(Resource):
    @admin_ns.doc('get_user')
    @admin_ns.marshal_with(user_model)
    def get(self, user_id):
        """Get a specific user by ID (admin only)."""
        return {'message': f'User {user_id} detail - implementation needed'}

# Utility functions for API documentation

def init_api_docs(app):
    """Initialize API documentation with Flask app."""
    app.register_blueprint(api_docs_bp)
    logger.info("API documentation initialized", 
                swagger_ui='/api/docs/swagger/',
                redoc='/api/docs/redoc/',
                openapi_json='/api/docs/openapi.json',
                openapi_yaml='/api/docs/openapi.yaml')

def generate_api_spec():
    """Generate complete API specification."""
    try:
        spec = api.specs['v1']
        return spec
    except Exception as e:
        logger.error("Failed to generate API spec", error=str(e))
        return None

def validate_api_spec():
    """Validate the API specification."""
    try:
        spec = generate_api_spec()
        if spec:
            # Basic validation - check for required fields
            required_fields = ['info', 'paths', 'openapi']
            for field in required_fields:
                if field not in spec:
                    logger.error(f"Missing required field in API spec: {field}")
                    return False
            logger.info("API specification validation passed")
            return True
        return False
    except Exception as e:
        logger.error("API specification validation failed", error=str(e))
        return False

