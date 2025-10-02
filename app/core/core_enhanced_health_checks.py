"""
Enhanced Health Checks for Schema Validation and Model Compatibility

This module provides comprehensive health checks that validate database schema
compatibility and model functionality to catch issues like missing columns.
"""

import time
from typing import Dict, Any, List
from sqlalchemy import text, inspect
from app.core.core_logging import logger


def check_model_schema_compatibility():
    """
    Check that all model fields exist in the database schema.
    This catches issues like missing columns that cause 500 errors.
    """
    try:
        from app.core.core_database import db
        from app.models.products.product_model import Product
        from app.models.deals.deal_models import Deal, Quote, QuoteLineItem
        from app.models.customers.customer_models import Company, Contact
        from app.models.user_model import User
        
        # Get database inspector
        inspector = inspect(db.engine)
        
        # Define models to check and their expected columns
        models_to_check = {
            'products': {
                'model': Product,
                'required_columns': [
                    'sku', 'name', 'unit_price', 'category', 'sub_category',
                    'series', 'item_no', 'description', 'discount_code',
                    'notes', 'weight_kg', 'dimensions', 'lead_time_days',
                    'is_active', 'brand', 'model_number', 'stock_quantity',
                    'reorder_level', 'id', 'created_at', 'updated_at'
                ]
            },
            'deals': {
                'model': Deal,
                'required_columns': [
                    'id', 'name', 'stage', 'type', 'amount', 'location',
                    'close_date', 'owner', 'contact_id', 'company_id',
                    'created_at', 'updated_at'
                ]
            },
            'quotes': {
                'model': Quote,
                'required_columns': [
                    'id', 'deal_id', 'name', 'status', 'total_amount',
                    'created_at', 'updated_at'
                ]
            },
            'quote_line_items': {
                'model': QuoteLineItem,
                'required_columns': [
                    'id', 'quote_id', 'product_id', 'quantity', 'unit_price',
                    'total_price', 'created_at', 'updated_at'
                ]
            },
            'companies': {
                'model': Company,
                'required_columns': [
                    'id', 'company_name', 'contact_person', 'email',
                    'phone', 'address', 'created_at', 'updated_at'
                ]
            },
            'contacts': {
                'model': Contact,
                'required_columns': [
                    'id', 'company_id', 'representative_name', 'email',
                    'phone', 'position', 'created_at', 'updated_at'
                ]
            },
            'users': {
                'model': User,
                'required_columns': [
                    'id', 'email', 'password_hash', 'first_name', 'last_name',
                    'role', 'is_active', 'created_at', 'updated_at'
                ]
            }
        }
        
        schema_issues = []
        tables_checked = 0
        
        for table_name, config in models_to_check.items():
            try:
                # Check if table exists
                if not inspector.has_table(table_name):
                    schema_issues.append(f"Table '{table_name}' does not exist")
                    continue
                
                # Get actual columns from database
                actual_columns = [col['name'] for col in inspector.get_columns(table_name)]
                
                # Check for missing required columns
                missing_columns = set(config['required_columns']) - set(actual_columns)
                if missing_columns:
                    schema_issues.append(
                        f"Table '{table_name}' missing columns: {', '.join(missing_columns)}"
                    )
                
                tables_checked += 1
                
            except Exception as e:
                schema_issues.append(f"Error checking table '{table_name}': {str(e)}")
        
        if schema_issues:
            return {
                'status': 'unhealthy',
                'schema_issues': schema_issues,
                'tables_checked': tables_checked,
                'error': 'Schema compatibility issues detected'
            }
        
        return {
            'status': 'healthy',
            'tables_checked': tables_checked,
            'message': 'All model schemas are compatible with database'
        }
        
    except Exception as e:
        logger.error("Schema compatibility check failed", error=str(e))
        return {
            'status': 'unhealthy',
            'error': str(e),
            'note': 'Schema compatibility check failed'
        }


def check_model_methods_functionality():
    """
    Check that critical model methods work correctly.
    This catches issues with model methods that reference non-existent columns.
    """
    try:
        from app.core.core_database import db
        from app.models.products.product_model import Product
        from app.models.deals.deal_models import Deal
        from app.models.customers.customer_models import Company
        
        method_issues = []
        models_tested = 0
        
        # Test Product model methods
        try:
            # Test basic query
            products = Product.query.limit(1).all()
            
            if products:
                product = products[0]
                
                # Test methods that were failing before
                try:
                    product.get_discounted_price()
                except Exception as e:
                    method_issues.append(f"Product.get_discounted_price() failed: {str(e)}")
                
                try:
                    product.get_list_price()
                except Exception as e:
                    method_issues.append(f"Product.get_list_price() failed: {str(e)}")
                
                try:
                    product.get_effective_price()
                except Exception as e:
                    method_issues.append(f"Product.get_effective_price() failed: {str(e)}")
                
                try:
                    product.is_low_stock()
                except Exception as e:
                    method_issues.append(f"Product.is_low_stock() failed: {str(e)}")
                
                try:
                    product.is_out_of_stock()
                except Exception as e:
                    method_issues.append(f"Product.is_out_of_stock() failed: {str(e)}")
                
                try:
                    product.get_availability_status()
                except Exception as e:
                    method_issues.append(f"Product.get_availability_status() failed: {str(e)}")
            
            models_tested += 1
            
        except Exception as e:
            method_issues.append(f"Product model test failed: {str(e)}")
        
        # Test Deal model methods
        try:
            deals = Deal.query.limit(1).all()
            if deals:
                deal = deals[0]
                # Test deal methods if they exist
                try:
                    deal.to_dict()
                except Exception as e:
                    method_issues.append(f"Deal.to_dict() failed: {str(e)}")
            
            models_tested += 1
            
        except Exception as e:
            method_issues.append(f"Deal model test failed: {str(e)}")
        
        # Test Company model methods
        try:
            companies = Company.query.limit(1).all()
            if companies:
                company = companies[0]
                # Test company methods if they exist
                try:
                    company.to_dict()
                except Exception as e:
                    method_issues.append(f"Company.to_dict() failed: {str(e)}")
            
            models_tested += 1
            
        except Exception as e:
            method_issues.append(f"Company model test failed: {str(e)}")
        
        if method_issues:
            return {
                'status': 'unhealthy',
                'method_issues': method_issues,
                'models_tested': models_tested,
                'error': 'Model method functionality issues detected'
            }
        
        return {
            'status': 'healthy',
            'models_tested': models_tested,
            'message': 'All model methods are functioning correctly'
        }
        
    except Exception as e:
        logger.error("Model methods functionality check failed", error=str(e))
        return {
            'status': 'unhealthy',
            'error': str(e),
            'note': 'Model methods functionality check failed'
        }


def check_critical_endpoints_functionality():
    """
    Check that critical application endpoints work correctly.
    This catches issues with routes that fail due to schema problems.
    """
    try:
        from app.core.core_database import db
        from app.models.products.product_model import Product
        from app.models.deals.deal_models import Deal
        from app.models.customers.customer_models import Company, Contact
        
        endpoint_issues = []
        endpoints_tested = 0
        
        # Test Product queries that are used in routes
        try:
            # Test product list query (used in /products/)
            products = Product.query.filter(Product.is_active == True).limit(10).all()
            endpoints_tested += 1
            
        except Exception as e:
            endpoint_issues.append(f"Product list query failed: {str(e)}")
        
        try:
            # Test product search query (used in product search)
            products = Product.query.filter(
                Product.description.ilike('%test%')
            ).limit(5).all()
            endpoints_tested += 1
            
        except Exception as e:
            endpoint_issues.append(f"Product search query failed: {str(e)}")
        
        try:
            # Test product price filtering (used in product filtering)
            products = Product.query.filter(
                Product.unit_price <= 1000
            ).limit(5).all()
            endpoints_tested += 1
            
        except Exception as e:
            endpoint_issues.append(f"Product price filtering failed: {str(e)}")
        
        # Test Deal queries
        try:
            deals = Deal.query.limit(5).all()
            endpoints_tested += 1
            
        except Exception as e:
            endpoint_issues.append(f"Deal query failed: {str(e)}")
        
        # Test Company queries
        try:
            companies = Company.query.limit(5).all()
            endpoints_tested += 1
            
        except Exception as e:
            endpoint_issues.append(f"Company query failed: {str(e)}")
        
        # Test Contact queries
        try:
            contacts = Contact.query.limit(5).all()
            endpoints_tested += 1
            
        except Exception as e:
            endpoint_issues.append(f"Contact query failed: {str(e)}")
        
        if endpoint_issues:
            return {
                'status': 'unhealthy',
                'endpoint_issues': endpoint_issues,
                'endpoints_tested': endpoints_tested,
                'error': 'Critical endpoint functionality issues detected'
            }
        
        return {
            'status': 'healthy',
            'endpoints_tested': endpoints_tested,
            'message': 'All critical endpoints are functioning correctly'
        }
        
    except Exception as e:
        logger.error("Critical endpoints functionality check failed", error=str(e))
        return {
            'status': 'unhealthy',
            'error': str(e),
            'note': 'Critical endpoints functionality check failed'
        }


def check_database_constraints():
    """
    Check that database constraints are properly defined.
    This catches issues with missing constraints that could cause data integrity problems.
    """
    try:
        from app.core.core_database import db
        from sqlalchemy import text
        
        constraint_issues = []
        
        # Check for important constraints
        constraints_to_check = [
            {
                'table': 'products',
                'constraint': 'check_product_unit_price',
                'description': 'Unit price must be >= 0'
            },
            {
                'table': 'products',
                'constraint': 'check_product_stock_quantity',
                'description': 'Stock quantity must be >= 0'
            },
            {
                'table': 'products',
                'constraint': 'check_product_reorder_level',
                'description': 'Reorder level must be >= 0'
            },
            {
                'table': 'products',
                'constraint': 'check_product_lead_time',
                'description': 'Lead time must be >= 0'
            }
        ]
        
        for constraint_info in constraints_to_check:
            try:
                # Check if constraint exists
                result = db.session.execute(text(f"""
                    SELECT constraint_name 
                    FROM information_schema.table_constraints 
                    WHERE table_name = '{constraint_info['table']}' 
                    AND constraint_name = '{constraint_info['constraint']}'
                """)).fetchone()
                
                if not result:
                    constraint_issues.append(
                        f"Missing constraint '{constraint_info['constraint']}' "
                        f"on table '{constraint_info['table']}': {constraint_info['description']}"
                    )
                
            except Exception as e:
                constraint_issues.append(
                    f"Error checking constraint '{constraint_info['constraint']}': {str(e)}"
                )
        
        if constraint_issues:
            return {
                'status': 'unhealthy',
                'constraint_issues': constraint_issues,
                'error': 'Database constraint issues detected'
            }
        
        return {
            'status': 'healthy',
            'constraints_checked': len(constraints_to_check),
            'message': 'All database constraints are properly defined'
        }
        
    except Exception as e:
        logger.error("Database constraints check failed", error=str(e))
        return {
            'status': 'unhealthy',
            'error': str(e),
            'note': 'Database constraints check failed'
        }


def check_foreign_key_integrity():
    """
    Check that foreign key relationships are intact.
    This catches issues with broken relationships between tables.
    """
    try:
        from app.core.core_database import db
        from sqlalchemy import text
        
        fk_issues = []
        
        # Check foreign key relationships
        fk_checks = [
            {
                'table': 'quote_line_items',
                'column': 'product_id',
                'referenced_table': 'products',
                'referenced_column': 'id'
            },
            {
                'table': 'quote_line_items',
                'column': 'quote_id',
                'referenced_table': 'quotes',
                'referenced_column': 'id'
            },
            {
                'table': 'quotes',
                'column': 'deal_id',
                'referenced_table': 'deals',
                'referenced_column': 'id'
            },
            {
                'table': 'deals',
                'column': 'contact_id',
                'referenced_table': 'contacts',
                'referenced_column': 'id'
            },
            {
                'table': 'deals',
                'column': 'company_id',
                'referenced_table': 'companies',
                'referenced_column': 'id'
            },
            {
                'table': 'contacts',
                'column': 'company_id',
                'referenced_table': 'companies',
                'referenced_column': 'id'
            }
        ]
        
        for fk_check in fk_checks:
            try:
                # Check for orphaned records
                result = db.session.execute(text(f"""
                    SELECT COUNT(*) 
                    FROM {fk_check['table']} t1
                    LEFT JOIN {fk_check['referenced_table']} t2 
                    ON t1.{fk_check['column']} = t2.{fk_check['referenced_column']}
                    WHERE t1.{fk_check['column']} IS NOT NULL 
                    AND t2.{fk_check['referenced_column']} IS NULL
                """)).fetchone()
                
                orphaned_count = result[0] if result else 0
                
                if orphaned_count > 0:
                    fk_issues.append(
                        f"Found {orphaned_count} orphaned records in "
                        f"{fk_check['table']}.{fk_check['column']} "
                        f"referencing {fk_check['referenced_table']}"
                    )
                
            except Exception as e:
                fk_issues.append(
                    f"Error checking FK {fk_check['table']}.{fk_check['column']}: {str(e)}"
                )
        
        if fk_issues:
            return {
                'status': 'unhealthy',
                'fk_issues': fk_issues,
                'error': 'Foreign key integrity issues detected'
            }
        
        return {
            'status': 'healthy',
            'fk_checks_performed': len(fk_checks),
            'message': 'All foreign key relationships are intact'
        }
        
    except Exception as e:
        logger.error("Foreign key integrity check failed", error=str(e))
        return {
            'status': 'unhealthy',
            'error': str(e),
            'note': 'Foreign key integrity check failed'
        }
