"""
Product Management Routes

This module contains routes for managing products in the RBM Tender App.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import or_, and_, func
from decimal import Decimal
import decimal
import csv
import io
import os
from datetime import datetime

from app.models.products.product_model import Product
from app.features.products.forms import (
    ProductForm, ProductSearchForm, ProductBulkActionForm, 
    ProductImportForm, ProductExportForm
)
from app.extensions import db
from app.core.core_logging import logger
from app.core.core_security import roles_required

# Create blueprint
products_bp = Blueprint('products', __name__, url_prefix='/products')

@products_bp.route('/')
@login_required
def list_products():
    """List all products with search and filtering."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Get search parameters
        search_term = request.args.get('search_term', '')
        category = request.args.get('category') or request.args.get('sub_category', '')
        series = request.args.get('series', '')
        item_no = request.args.get('item_no', '')
        # brand parameter removed as it's not in the new schema
        availability = request.args.get('availability', '')
        price_range = request.args.get('price_range', '')
        
        # Handle sub_category parameter separately
        sub_category = request.args.get('sub_category', '')
        
        # Build query
        query = Product.query
        
        # Apply search filters
        if search_term:
            query = query.filter(
                or_(
                    Product.item_no.ilike(f'%{search_term}%'),
                    Product.description.ilike(f'%{search_term}%'),
                    Product.category.ilike(f'%{search_term}%'),
                    Product.sub_category.ilike(f'%{search_term}%'),
                    Product.series.ilike(f'%{search_term}%')
                )
            )
        
        if category:
            query = query.filter(Product.category.ilike(f'%{category}%'))
        
        if sub_category:
            query = query.filter(Product.sub_category.ilike(f'%{sub_category}%'))
        
        if series:
            query = query.filter(Product.series.ilike(f'%{series}%'))
        
        if item_no:
            query = query.filter(Product.item_no.ilike(f'%{item_no}%'))
        
        # Note: brand filter removed as it's not in the new schema
        
        # Apply availability filter (simplified - no stock tracking)
        if availability:
            if availability == 'active':
                query = query.filter(Product.is_active == True)
            elif availability == 'inactive':
                query = query.filter(Product.is_active == False)
        
        # Apply price range filter (using list_price)
        if price_range:
            if price_range == '0-100':
                query = query.filter(Product.list_price <= 100)
            elif price_range == '100-500':
                query = query.filter(and_(Product.list_price > 100, Product.list_price <= 500))
            elif price_range == '500-1000':
                query = query.filter(and_(Product.list_price > 500, Product.list_price <= 1000))
            elif price_range == '1000+':
                query = query.filter(Product.list_price > 1000)
        
        # Get paginated results (order by item_no first, then description, then id)
        # Use COALESCE to handle NULL values in ordering
        products = query.order_by(
            func.coalesce(Product.item_no, ''),
            func.coalesce(Product.description, ''),
            Product.id
        ).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Get statistics
        total_products = Product.query.count()
        active_products = Product.query.filter(Product.is_active == True).count()
        inactive_products = Product.query.filter(Product.is_active == False).count()
        
        # Get unique categories, sub-categories, and series for filters
        categories = db.session.query(Product.category).distinct().filter(Product.category.isnot(None)).all()
        sub_categories = db.session.query(Product.sub_category).distinct().filter(Product.sub_category.isnot(None)).all()
        series_list = db.session.query(Product.series).distinct().filter(Product.series.isnot(None)).all()
        
        # Log the results for debugging
        logger.info(f"Products page loaded: {total_products} total products, {len(products.items)} on current page")
        logger.info(f"Query filters applied - search_term: '{search_term}', category: '{category}', sub_category: '{sub_category}'")
        logger.info(f"Statistics - Total: {total_products}, Active: {active_products}, Inactive: {inactive_products}")
        
        return render_template('products/list.html',
                             products=products,
                             search_term=search_term,
                             category=category,
                             sub_category=sub_category,
                             series=series,
                             item_no=item_no,
                             availability=availability,
                             price_range=price_range,
                             categories=[c[0] for c in categories],
                             sub_categories=[s[0] for s in sub_categories],
                             series_list=[s[0] for s in series_list],
                             stats={
                                 'total': total_products,
                                 'active': active_products,
                                 'inactive': inactive_products
                             })
    
    except Exception as e:
        logger.error(f"Error loading products page: {e}", exc_info=True)
        flash('An error occurred while loading the products page. Please try again.', 'error')
        # Return a simple error template or redirect
        return render_template('products/list.html',
                             products=None,
                             search_term='',
                             category='',
                             series='',
                             item_no='',
                             availability='',
                             price_range='',
                             categories=[],
                             series_list=[],
                             stats={
                                 'total': 0,
                                 'active': 0,
                                 'inactive': 0
                             })

@products_bp.route('/create', methods=['GET', 'POST'])
@login_required
@roles_required('Admin', 'Manager')
def create_product():
    """Create a new product."""
    form = ProductForm()
    
    if form.validate_on_submit():
        try:
            product = Product(
                # New primary fields
                category=form.category.data.strip(),
                sub_category=form.sub_category.data.strip() if form.sub_category.data else None,
                series=form.series.data.strip() if form.series.data else None,
                item_no=form.item_no.data.strip(),
                description=form.description.data.strip(),
                pack=form.pack.data.strip() if form.pack.data else None,
                carton_qty=form.carton_qty.data or 1,
                list_price=form.list_price.data,
                discount_code=form.discount_code.data.strip() if form.discount_code.data else None,
                notes=form.notes.data.strip() if form.notes.data else None,
                weight_kg=form.weight_kg.data,
                dimensions=form.dimensions.data.strip() if form.dimensions.data else None,
                lead_time_days=form.lead_time_days.data or 0,
                is_active=form.is_active.data,
                
            )
            
            product.save()
            
            logger.info(f"Product created: {product.item_no} - {product.description} by {current_user.email}")
            flash(f'Product "{product.item_no}" created successfully!', 'success')
            
            return redirect(url_for('products.view_product', product_id=product.id))
            
        except Exception as e:
            logger.error(f"Error creating product: {e}")
            flash('An error occurred while creating the product.', 'error')
    
    return render_template('products/create.html', form=form)

@products_bp.route('/<int:product_id>')
@login_required
def view_product(product_id):
    """View product details."""
    product = Product.query.get_or_404(product_id)
    
    try:
        # Get similar products
        similar_products = product.get_similar_products(limit=5)
        
        # Get usage statistics
        usage_stats = product.get_usage_statistics()
        
    except Exception as e:
        logger.error(f"Error loading product details for product {product_id}: {e}")
        # Provide fallback values to prevent 500 error
        similar_products = []
        usage_stats = {
            'total_quantity_sold': 0,
            'total_value_sold': 0.0,
            'usage_count': 0,
            'average_quantity_per_use': 0
        }
    
    return render_template('products/view.html',
                         product=product,
                         similar_products=similar_products,
                         usage_stats=usage_stats)

@products_bp.route('/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
@roles_required('Admin', 'Manager')
def edit_product(product_id):
    """Edit an existing product."""
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    
    # Set product ID for validation
    form.set_product_id(product_id)
    
    if form.validate_on_submit():
        try:
            # Update new primary fields
            product.category = form.category.data.strip()
            product.sub_category = form.sub_category.data.strip() if form.sub_category.data else None
            product.series = form.series.data.strip() if form.series.data else None
            product.item_no = form.item_no.data.strip()
            product.description = form.description.data.strip()
            product.pack = form.pack.data.strip() if form.pack.data else None
            product.carton_qty = form.carton_qty.data or 1
            product.list_price = form.list_price.data
            product.discount_code = form.discount_code.data.strip() if form.discount_code.data else None
            product.notes = form.notes.data.strip() if form.notes.data else None
            product.weight_kg = form.weight_kg.data
            product.dimensions = form.dimensions.data.strip() if form.dimensions.data else None
            product.lead_time_days = form.lead_time_days.data or 0
            product.is_active = form.is_active.data
            
            
            product.save()
            
            logger.info(f"Product updated: {product.item_no} - {product.description} by {current_user.email}")
            flash(f'Product "{product.item_no}" updated successfully!', 'success')
            
            return redirect(url_for('products.view_product', product_id=product.id))
            
        except Exception as e:
            logger.error(f"Error updating product: {e}")
            flash('An error occurred while updating the product.', 'error')
    
    return render_template('products/edit.html', form=form, product=product)

@products_bp.route('/<int:product_id>/delete', methods=['POST'])
@login_required
@roles_required('Admin')
def delete_product(product_id):
    """Delete a product."""
    product = Product.query.get_or_404(product_id)
    
    try:
        product_identifier = product.item_no or product.description or f"ID {product.id}"
        product.delete()
        
        logger.info(f"Product deleted: {product.item_no} - {product.description} by {current_user.email}")
        flash(f'Product "{product_identifier}" deleted successfully!', 'success')
        
    except Exception as e:
        logger.error(f"Error deleting product: {e}")
        flash('An error occurred while deleting the product.', 'error')
    
    return redirect(url_for('products.list_products'))

@products_bp.route('/<int:product_id>/toggle-status', methods=['POST'])
@login_required
@roles_required('Admin', 'Manager')
def toggle_product_status(product_id):
    """Toggle product active status."""
    product = Product.query.get_or_404(product_id)
    
    try:
        product.is_active = not product.is_active
        product.save()
        
        status = "activated" if product.is_active else "deactivated"
        logger.info(f"Product {status}: {product.item_no} - {product.description} by {current_user.email}")
        flash(f'Product "{product.item_no}" {status}!', 'success')
        
    except Exception as e:
        logger.error(f"Error toggling product status: {e}")
        flash('An error occurred while updating the product status.', 'error')
    
    return redirect(url_for('products.view_product', product_id=product.id))

# Stock update route removed - not connected to warehouse system

@products_bp.route('/bulk-action', methods=['POST'])
@login_required
@roles_required('Admin', 'Manager')
def bulk_action():
    """Perform bulk actions on products."""
    form = ProductBulkActionForm()
    
    if form.validate_on_submit():
        action = form.action.data
        product_ids = [int(id) for id in form.product_ids.data.split(',') if id.strip()]
        
        if not product_ids:
            flash('No products selected.', 'error')
            return redirect(url_for('products.list_products'))
        
        products = Product.query.filter(Product.id.in_(product_ids)).all()
        
        try:
            if action == 'activate':
                for product in products:
                    product.is_active = True
                db.session.commit()
                flash(f'{len(products)} products activated!', 'success')
                
            elif action == 'deactivate':
                for product in products:
                    product.is_active = False
                db.session.commit()
                flash(f'{len(products)} products deactivated!', 'success')
                
            elif action == 'delete':
                for product in products:
                    product.delete()
                flash(f'{len(products)} products deleted!', 'success')
                
            elif action == 'export':
                # Handle export in a separate function
                return export_products(product_ids)
            
            logger.info(f"Bulk action '{action}' performed on {len(products)} products by {current_user.email}")
            
        except Exception as e:
            logger.error(f"Error in bulk action: {e}")
            flash('An error occurred while performing the bulk action.', 'error')
    
    return redirect(url_for('products.list_products'))

@products_bp.route('/import', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def import_products():
    """Import products from CSV file."""
    form = ProductImportForm()
    
    if form.validate_on_submit():
        try:
            csv_file = form.csv_file.data
            update_existing = form.update_existing.data
            skip_errors = form.skip_errors.data
            
            # Read CSV file with encoding detection
            csv_file.seek(0)  # Reset file pointer
            raw_data = csv_file.read()
            
            # Try different encodings
            encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
            csv_data = None
            
            for encoding in encodings_to_try:
                try:
                    csv_data = raw_data.decode(encoding)
                    logger.info(f"Successfully decoded CSV with {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    continue
            
            if csv_data is None:
                raise ValueError("Could not decode CSV file. Please save your file as UTF-8 encoding.")
            # Clean up trailing commas that might cause empty columns
            csv_lines = csv_data.strip().split('\n')
            cleaned_lines = []
            for line in csv_lines:
                # Remove trailing commas and whitespace
                cleaned_line = line.rstrip(', \t')
                cleaned_lines.append(cleaned_line)
            csv_data = '\n'.join(cleaned_lines)
            
            csv_reader = csv.DictReader(io.StringIO(csv_data))
            
            imported_count = 0
            updated_count = 0
            errors = []
            
            for row_num, row in enumerate(csv_reader, 2):  # Start from 2 to account for header
                try:
                    # Validate required fields
                    required_fields = ['Item No', 'Description', 'Category']
                    missing_fields = []
                    for field in required_fields:
                        if not row.get(field) or not row[field].strip():
                            missing_fields.append(field)
                    
                    if missing_fields:
                        errors.append(f"Row {row_num}: Missing required fields: {', '.join(missing_fields)}")
                        if not skip_errors:
                            continue
                    
                    # Check if product exists by Item No
                    item_no = row['Item No'].strip()
                    existing_product = Product.query.filter_by(item_no=item_no).first()
                    
                    if existing_product and not update_existing:
                        errors.append(f"Row {row_num}: Item No '{item_no}' already exists")
                        if not skip_errors:
                            continue
                    
                    # Create or update product
                    if existing_product and update_existing:
                        product = existing_product
                        updated_count += 1
                    else:
                        product = Product()
                        imported_count += 1
                    
                    # Helper function to safely get and strip values
                    def safe_get_value(field_name, default=None):
                        """Safely get and strip a value from CSV row, handling None values."""
                        value = row.get(field_name)
                        if value is None or value == '':
                            return default
                        return value.strip() if value else default
                    
                    # Helper function to update field only if CSV has value or it's a new product
                    def update_field_if_provided(field_name, csv_field, transform_func=None, default_value=None):
                        """Update field only if CSV has value or it's a new product."""
                        csv_value = safe_get_value(csv_field)
                        if csv_value is not None:
                            if transform_func:
                                try:
                                    return transform_func(csv_value)
                                except (ValueError, TypeError) as e:
                                    errors.append(f"Row {row_num}: Invalid {csv_field} format '{csv_value}' - {str(e)}")
                                    return None
                            return csv_value
                        elif not existing_product:
                            # For new products, use default values
                            return default_value
                        else:
                            # For existing products, keep current value if CSV is empty
                            return getattr(existing_product, field_name, default_value)
                    
                    # Map CSV columns to database fields using new schema
                    product.item_no = item_no
                    product.description = row['Description'].strip()
                    product.category = row['Category'].strip()
                    
                    # Optional fields with smart updating
                    product.sub_category = update_field_if_provided('sub_category', 'SubCategory')
                    product.series = update_field_if_provided('series', 'Series')
                    product.pack = update_field_if_provided('pack', 'Pack')
                    
                    # Numeric fields with validation
                    product.carton_qty = update_field_if_provided('carton_qty', 'Carton Qty', 
                                                               lambda x: int(x) if x else 1) or 1
                    
                    product.list_price = update_field_if_provided('list_price', 'List price',
                                                                lambda x: Decimal(x) if x else None)
                    
                    # Physical properties
                    product.weight_kg = update_field_if_provided('weight_kg', 'weight_kg',
                                                               lambda x: Decimal(x) if x else None)
                    
                    product.dimensions = update_field_if_provided('dimensions', 'dimensions')
                    
                    product.lead_time_days = update_field_if_provided('lead_time_days', 'lead_time_days',
                                                                    lambda x: int(x) if x else 0) or 0
                    
                    # Notes
                    product.notes = update_field_if_provided('notes', 'Note')
                    
                    # Handle discount code with validation
                    disc_code = safe_get_value('Disc Code')
                    if disc_code:
                        # Check if discount code exists in database
                        from app.models.deals.deal_models import Discount
                        existing_discount = Discount.query.filter_by(code=disc_code).first()
                        if existing_discount:
                            product.discount_code = disc_code
                        else:
                            # Log warning and skip discount code instead of failing
                            errors.append(f"Row {row_num}: Discount code '{disc_code}' not found in database, skipping discount")
                            product.discount_code = None
                    else:
                        # For existing products, keep current discount code if CSV is empty
                        if existing_product:
                            product.discount_code = existing_product.discount_code
                        else:
                            product.discount_code = None
                    
                    # Active status - only update if CSV has value
                    is_active_str = safe_get_value('is_active', 'true')
                    if is_active_str is not None:
                        product.is_active = is_active_str.lower() in ['true', '1', 'yes', 'y']
                    elif not existing_product:
                        # For new products, default to active
                        product.is_active = True
                    else:
                        # For existing products, keep current status if CSV is empty
                        product.is_active = existing_product.is_active
                    
                    
                    product.save()
                    
                except Exception as e:
                    # Provide more specific error messages for common issues
                    if "ConversionSyntax" in str(e):
                        error_msg = f"Row {row_num}: Invalid number format in CSV data. Check price fields (List price) for non-numeric values like '$', commas, or text."
                    elif "ValueError" in str(e):
                        error_msg = f"Row {row_num}: Invalid data format - {str(e)}"
                    elif "TypeError" in str(e):
                        error_msg = f"Row {row_num}: Data type error - {str(e)}"
                    elif "ForeignKeyViolation" in str(e):
                        error_msg = f"Row {row_num}: Database constraint error - {str(e)}"
                    else:
                        error_msg = f"Row {row_num}: {str(e)}"
                    
                    errors.append(error_msg)
                    if not skip_errors:
                        raise e
            
            # Show results with detailed error messages
            if imported_count > 0:
                flash(f'✅ {imported_count} products imported successfully!', 'success')
            if updated_count > 0:
                flash(f'✅ {updated_count} products updated successfully!', 'success')
            
            if errors:
                # Show detailed error messages instead of generic count
                error_count = len(errors)
                if error_count <= 5:
                    # Show all errors if 5 or fewer
                    for error in errors:
                        flash(f'❌ {error}', 'error')
                else:
                    # Show first 3 errors and count if more
                    for error in errors[:3]:
                        flash(f'❌ {error}', 'error')
                    flash(f'❌ ... and {error_count - 3} more errors. Check logs for details.', 'error')
            
            logger.info(f"Products imported: {imported_count} new, {updated_count} updated by {current_user.email}")
            
        except Exception as e:
            logger.error(f"Error importing products: {e}")
            # Provide more specific error messages
            if "Could not decode CSV file" in str(e):
                flash('❌ CSV file encoding issue. Please save your file as UTF-8 encoding in Excel/Google Sheets.', 'error')
            elif "No such file or directory" in str(e):
                flash('❌ CSV file not found or could not be read.', 'error')
            elif "Permission denied" in str(e):
                flash('❌ Permission denied accessing the CSV file.', 'error')
            elif "Invalid CSV format" in str(e):
                flash('❌ Invalid CSV format. Please check your file structure.', 'error')
            else:
                flash(f'❌ Import failed: {str(e)}', 'error')
    
    return render_template('products/import.html', form=form)

@products_bp.route('/download-sample-csv')
@login_required
def download_sample_csv():
    """Download sample CSV template."""
    try:
        # Try to read the sample CSV from the new location first
        sample_path = os.path.join(current_app.root_path, 'static', 'samples', 'products.csv')
        
        if os.path.exists(sample_path):
            with open(sample_path, 'r', encoding='utf-8') as f:
                csv_content = f.read()
        else:
            # Fallback to old location
            sample_path = os.path.join(current_app.root_path, '..', 'data', 'products.csv')
            if os.path.exists(sample_path):
                with open(sample_path, 'r', encoding='utf-8') as f:
                    csv_content = f.read()
            else:
                # Create a default sample if file doesn't exist (new schema - 14 columns)
                csv_content = "Category,SubCategory,Series,Item No,Description,Pack,Carton Qty,List price,Disc Code,Note,weight_kg,dimensions,lead_time_days,is_active\n"
        
        from flask import Response
        return Response(
            csv_content,
            mimetype='text/csv',
            headers={
                'Content-Disposition': 'attachment; filename=products_sample.csv'
            }
        )
        
    except Exception as e:
        logger.error(f"Error downloading sample CSV: {e}")
        flash('Error downloading sample CSV.', 'error')
        return redirect(url_for('products.import_products'))

@products_bp.route('/export')
@login_required
def export_products():
    """Export products to CSV."""
    try:
        # Get all products or filtered products
        products = Product.query.filter(Product.is_active == True).all()
        
        # Create CSV data
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header (new schema - 14 columns)
        writer.writerow([
            'Category', 'SubCategory', 'Series', 'Item No', 'Description', 'Pack', 'Carton Qty',
            'List price', 'Disc Code', 'Note', 'weight_kg', 'dimensions', 'lead_time_days', 'is_active'
        ])
        
        # Write data (new schema - 14 columns)
        for product in products:
            writer.writerow([
                product.category or '',
                product.sub_category or '',
                product.series or '',
                product.item_no or '',
                product.description or '',
                product.pack or '',
                product.carton_qty or 1,
                float(product.list_price) if product.list_price else '',
                product.discount_code or '',
                product.notes or '',
                float(product.weight_kg) if product.weight_kg else '',
                product.dimensions or '',
                product.lead_time_days or 0,
                'Yes' if product.is_active else 'No'
            ])
        
        # Create response
        output.seek(0)
        
        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=products_{datetime.now().strftime("%Y%m%d")}.csv'}
        )
        
    except Exception as e:
        logger.error(f"Error exporting products: {e}")
        flash('An error occurred while exporting products.', 'error')
        return redirect(url_for('products.list_products'))

@products_bp.route('/api/search')
@login_required
def api_search():
    """API endpoint for product search (for AJAX requests)."""
    search_term = request.args.get('q', '')
    limit = request.args.get('limit', 10, type=int)
    
    if not search_term:
        return jsonify([])
    
    products = Product.query.filter(
        and_(
            Product.is_active == True,
            or_(
                Product.item_no.ilike(f'%{search_term}%'),
                Product.description.ilike(f'%{search_term}%'),
                Product.category.ilike(f'%{search_term}%'),
                Product.sub_category.ilike(f'%{search_term}%'),
                Product.series.ilike(f'%{search_term}%')
            )
        )
    ).limit(limit).all()
    
    results = []
    for product in products:
        results.append({
            'id': product.id,
            'item_no': product.item_no,
            'description': product.description,
            'category': product.category,
            'list_price': float(product.list_price) if product.list_price else 0.0,
            'is_active': product.is_active
        })
    
    return jsonify(results)

@products_bp.route('/dashboard')
@login_required
def dashboard():
    """Product management dashboard."""
    # Get statistics (simplified without stock tracking)
    total_products = Product.query.count()
    active_products = Product.query.filter(Product.is_active == True).count()
    inactive_products = Product.query.filter(Product.is_active == False).count()
    
    # Get products by category
    category_stats = db.session.query(
        Product.category,
        func.count(Product.id).label('count')
    ).filter(Product.is_active == True).group_by(Product.category).all()
    
    # Get recent products
    recent_products = Product.query.order_by(Product.created_at.desc()).limit(10).all()
    
    # Get inactive products
    inactive_list = Product.query.filter(
        Product.is_active == False
    ).order_by(Product.item_no.asc()).limit(10).all()
    
    return render_template('products/dashboard.html',
                         stats={
                             'total': total_products,
                             'active': active_products,
                             'inactive': inactive_products,
                             'low_stock': 0,  # No stock tracking in current system
                             'out_of_stock': 0  # No stock tracking in current system
                         },
                         category_stats=category_stats,
                         recent_products=recent_products,
                         inactive_list=inactive_list) 

@products_bp.route('/debug')
@login_required
def debug_products():
    """Debug route to check products database status."""
    try:
        # Basic product count
        total_products = Product.query.count()
        
        # Check if any products exist
        first_product = Product.query.first()
        
        # Test the same query as list_products
        test_query = Product.query
        test_paginated = test_query.order_by(
            func.coalesce(Product.item_no, ''),
            func.coalesce(Product.description, ''),
            Product.id
        ).paginate(page=1, per_page=20, error_out=False)
        
        # Get table info
        from sqlalchemy import text
        result = db.session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'products'"))
        table_exists = result.fetchone() is not None
        
        # Check for NULL values in required fields
        null_item_no_count = db.session.execute(text("SELECT COUNT(*) FROM products WHERE item_no IS NULL")).scalar()
        null_description_count = db.session.execute(text("SELECT COUNT(*) FROM products WHERE description IS NULL")).scalar()
        
        debug_info = {
            'table_exists': table_exists,
            'total_products': total_products,
            'first_product': str(first_product) if first_product else None,
            'paginated_items_count': len(test_paginated.items),
            'null_item_no_count': null_item_no_count,
            'null_description_count': null_description_count,
            'database_url': str(db.engine.url),
        }
        
        return jsonify(debug_info)
        
    except Exception as e:
        logger.error(f"Error in debug route: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500 