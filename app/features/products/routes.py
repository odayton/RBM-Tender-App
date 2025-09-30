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
        brand = request.args.get('brand', '')
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
                    Product.series.ilike(f'%{search_term}%'),
                    Product.sku.ilike(f'%{search_term}%'),  # Legacy
                    Product.name.ilike(f'%{search_term}%'),  # Legacy
                    Product.brand.ilike(f'%{search_term}%')  # Legacy
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
        
        if brand:
            query = query.filter(Product.brand.ilike(f'%{brand}%'))
        
        # Apply availability filter
        if availability:
            if availability == 'in_stock':
                query = query.filter(and_(Product.is_active == True, Product.stock_quantity > Product.reorder_level))
            elif availability == 'low_stock':
                query = query.filter(and_(Product.is_active == True, Product.stock_quantity <= Product.reorder_level, Product.stock_quantity > 0))
            elif availability == 'out_of_stock':
                query = query.filter(and_(Product.is_active == True, Product.stock_quantity == 0))
            elif availability == 'inactive':
                query = query.filter(Product.is_active == False)
        
        # Apply price range filter (using list_price as primary, fallback to unit_price)
        if price_range:
            if price_range == '0-100':
                query = query.filter(
                    or_(
                        Product.list_price <= 100,
                        Product.unit_price <= 100
                    )
                )
            elif price_range == '100-500':
                query = query.filter(
                    or_(
                        and_(Product.list_price > 100, Product.list_price <= 500),
                        and_(Product.unit_price > 100, Product.unit_price <= 500)
                    )
                )
            elif price_range == '500-1000':
                query = query.filter(
                    or_(
                        and_(Product.list_price > 500, Product.list_price <= 1000),
                        and_(Product.unit_price > 500, Product.unit_price <= 1000)
                    )
                )
            elif price_range == '1000+':
                query = query.filter(
                    or_(
                        Product.list_price > 1000,
                        Product.unit_price > 1000
                    )
                )
        
        # Get paginated results (order by item_no first, then description)
        products = query.order_by(Product.item_no, Product.description).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Get statistics
        total_products = query.count()
        active_products = query.filter(Product.is_active == True).count()
        low_stock_products = query.filter(
            and_(Product.is_active == True, Product.stock_quantity <= Product.reorder_level)
        ).count()
        out_of_stock_products = query.filter(
            and_(Product.is_active == True, Product.stock_quantity == 0)
        ).count()
        
        # Get unique categories, sub-categories, series, and brands for filters
        categories = db.session.query(Product.category).distinct().filter(Product.category.isnot(None)).all()
        sub_categories = db.session.query(Product.sub_category).distinct().filter(Product.sub_category.isnot(None)).all()
        series_list = db.session.query(Product.series).distinct().filter(Product.series.isnot(None)).all()
        brands = db.session.query(Product.brand).distinct().filter(Product.brand.isnot(None)).all()
        
        # Log the results for debugging
        logger.info(f"Products page loaded: {total_products} total products, {len(products.items)} on current page")
        
        return render_template('products/list.html',
                             products=products,
                             search_term=search_term,
                             category=category,
                             sub_category=sub_category,
                             series=series,
                             item_no=item_no,
                             brand=brand,
                             availability=availability,
                             price_range=price_range,
                             categories=[c[0] for c in categories],
                             sub_categories=[s[0] for s in sub_categories],
                             series_list=[s[0] for s in series_list],
                             brands=[b[0] for b in brands],
                             stats={
                                 'total': total_products,
                                 'active': active_products,
                                 'low_stock': low_stock_products,
                                 'out_of_stock': out_of_stock_products
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
                             brand='',
                             availability='',
                             price_range='',
                             categories=[],
                             series_list=[],
                             brands=[],
                             stats={
                                 'total': 0,
                                 'active': 0,
                                 'low_stock': 0,
                                 'out_of_stock': 0
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
                pack=form.pack.data or 1,
                carton_qty=form.carton_qty.data or 1,
                list_price=form.list_price.data,
                nett=form.nett.data,
                discount_code=form.discount_code.data.strip() if form.discount_code.data else None,
                notes=form.notes.data.strip() if form.notes.data else None,
                weight_kg=form.weight_kg.data,
                dimensions=form.dimensions.data.strip() if form.dimensions.data else None,
                lead_time_days=form.lead_time_days.data or 0,
                is_active=form.is_active.data,
                
                # Legacy fields (for backward compatibility)
                sku=form.sku.data.strip() if form.sku.data else None,
                name=form.name.data.strip() if form.name.data else None,
                unit_price=form.unit_price.data,
                brand=form.brand.data.strip() if form.brand.data else None,
                model_number=form.model_number.data.strip() if form.model_number.data else None,
                stock_quantity=form.stock_quantity.data or 0,
                reorder_level=form.reorder_level.data or 0
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
    
    # Get similar products
    similar_products = product.get_similar_products(limit=5)
    
    # Get usage statistics
    usage_stats = product.get_usage_statistics()
    
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
    
    # Set product ID for SKU validation
    form.set_product_id(product_id)
    
    if form.validate_on_submit():
        try:
            # Update new primary fields
            product.category = form.category.data.strip()
            product.sub_category = form.sub_category.data.strip() if form.sub_category.data else None
            product.series = form.series.data.strip() if form.series.data else None
            product.item_no = form.item_no.data.strip()
            product.description = form.description.data.strip()
            product.pack = form.pack.data or 1
            product.carton_qty = form.carton_qty.data or 1
            product.list_price = form.list_price.data
            product.nett = form.nett.data
            product.discount_code = form.discount_code.data.strip() if form.discount_code.data else None
            product.notes = form.notes.data.strip() if form.notes.data else None
            product.weight_kg = form.weight_kg.data
            product.dimensions = form.dimensions.data.strip() if form.dimensions.data else None
            product.lead_time_days = form.lead_time_days.data or 0
            product.is_active = form.is_active.data
            
            # Update legacy fields (for backward compatibility)
            product.sku = form.sku.data.strip() if form.sku.data else None
            product.name = form.name.data.strip() if form.name.data else None
            product.unit_price = form.unit_price.data
            product.brand = form.brand.data.strip() if form.brand.data else None
            product.model_number = form.model_number.data.strip() if form.model_number.data else None
            product.stock_quantity = form.stock_quantity.data or 0
            product.reorder_level = form.reorder_level.data or 0
            
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

@products_bp.route('/<int:product_id>/update-stock', methods=['POST'])
@login_required
@roles_required('Admin', 'Manager')
def update_stock(product_id):
    """Update product stock quantity."""
    product = Product.query.get_or_404(product_id)
    
    try:
        quantity_change = int(request.form.get('quantity_change', 0))
        product.update_stock(quantity_change)
        product.save()
        
        logger.info(f"Stock updated for {product.sku}: {quantity_change} by {current_user.email}")
        flash(f'Stock updated for "{product.name}"!', 'success')
        
    except ValueError:
        flash('Invalid quantity value.', 'error')
    except Exception as e:
        logger.error(f"Error updating stock: {e}")
        flash('An error occurred while updating stock.', 'error')
    
    return redirect(url_for('products.view_product', product_id=product.id))

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
                    
                    # Map CSV columns to database fields using new schema
                    product.item_no = item_no
                    product.description = row['Description'].strip()
                    product.category = row['Category'].strip()
                    
                    # Optional fields with validation
                    if row.get('SubCategory'):
                        product.sub_category = row['SubCategory'].strip()
                    
                    if row.get('Series'):
                        product.series = row['Series'].strip()
                    
                    # Pack and Carton Qty with defaults
                    try:
                        product.pack = int(row.get('Pack', 1)) if row.get('Pack') else 1
                    except (ValueError, TypeError):
                        errors.append(f"Row {row_num}: Invalid Pack value '{row.get('Pack')}', using default 1")
                        product.pack = 1
                    
                    try:
                        product.carton_qty = int(row.get('Carton Qty', 1)) if row.get('Carton Qty') else 1
                    except (ValueError, TypeError):
                        errors.append(f"Row {row_num}: Invalid Carton Qty value '{row.get('Carton Qty')}', using default 1")
                        product.carton_qty = 1
                    
                    # Pricing fields with better error handling
                    if row.get('List price'):
                        try:
                            list_price_str = str(row['List price']).replace('$', '').replace(',', '').replace(' ', '').strip()
                            if list_price_str and list_price_str.lower() not in ['', 'null', 'none', 'n/a']:
                                product.list_price = Decimal(list_price_str)
                            else:
                                product.list_price = None
                        except (ValueError, TypeError, decimal.InvalidOperation) as e:
                            errors.append(f"Row {row_num}: Invalid List price format '{row['List price']}' - must be a number")
                            product.list_price = None
                    
                    # Physical properties
                    if row.get('weight_kg'):
                        try:
                            product.weight_kg = Decimal(row['weight_kg']) if row['weight_kg'] else None
                        except (ValueError, TypeError):
                            errors.append(f"Row {row_num}: Invalid weight format '{row['weight_kg']}'")
                    
                    if row.get('dimensions'):
                        product.dimensions = row['dimensions'].strip()
                    
                    if row.get('lead_time_days'):
                        try:
                            product.lead_time_days = int(row['lead_time_days']) if row['lead_time_days'] else None
                        except (ValueError, TypeError):
                            errors.append(f"Row {row_num}: Invalid lead time format '{row['lead_time_days']}'")
                    
                    # Notes and discount code
                    if row.get('Note'):
                        product.notes = row['Note'].strip()
                    
                    # Handle discount code with validation
                    disc_code = row.get('Disc Code', '').strip()
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
                        product.discount_code = None
                    
                    # Active status
                    is_active_str = row.get('is_active', 'true').strip().lower()
                    product.is_active = is_active_str in ['true', '1', 'yes', 'y']
                    
                    # Legacy fields for backward compatibility
                    product.sku = item_no  # Use Item No as SKU
                    product.name = product.description  # Use Description as name
                    if product.list_price:
                        product.unit_price = product.list_price  # Use List Price as unit price
                    
                    # Set default values for legacy fields
                    product.brand = None
                    product.model_number = None
                    product.stock_quantity = 0
                    product.reorder_level = 0
                    
                    product.save()
                    
                except Exception as e:
                    # Provide more specific error messages for common issues
                    if "ConversionSyntax" in str(e):
                        error_msg = f"Row {row_num}: Invalid number format in CSV data. Check price fields (List price, Nett) for non-numeric values like '$', commas, or text."
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
                # Create a default sample if file doesn't exist
                csv_content = "Category,SubCategory,Series,Item No,Description,Pack,Carton Qty,List price,Nett,Disc Code,Note,weight_kg,dimensions,lead_time_days,is_active\n"
        
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
        
        # Write header
        writer.writerow([
            'SKU', 'Name', 'Description', 'Unit Price', 'Category', 'Brand',
            'Model Number', 'Weight (kg)', 'Dimensions', 'Stock Quantity',
            'Reorder Level', 'Lead Time (days)', 'Active', 'Notes'
        ])
        
        # Write data
        for product in products:
            writer.writerow([
                product.sku,
                product.name,
                product.description or '',
                float(product.unit_price),
                product.category,
                product.brand or '',
                product.model_number or '',
                float(product.weight_kg) if product.weight_kg else '',
                product.dimensions or '',
                product.stock_quantity,
                product.reorder_level,
                product.lead_time_days,
                'Yes' if product.is_active else 'No',
                product.notes or ''
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
                Product.name.ilike(f'%{search_term}%'),
                Product.sku.ilike(f'%{search_term}%'),
                Product.brand.ilike(f'%{search_term}%')
            )
        )
    ).limit(limit).all()
    
    results = []
    for product in products:
        results.append({
            'id': product.id,
            'sku': product.sku,
            'name': product.name,
            'brand': product.brand,
            'unit_price': float(product.unit_price),
            'stock_quantity': product.stock_quantity,
            'availability': product.get_availability_status()
        })
    
    return jsonify(results)

@products_bp.route('/dashboard')
@login_required
def dashboard():
    """Product management dashboard."""
    # Get statistics
    total_products = Product.query.count()
    active_products = Product.query.filter(Product.is_active == True).count()
    low_stock_products = Product.query.filter(
        and_(Product.is_active == True, Product.stock_quantity <= Product.reorder_level)
    ).count()
    out_of_stock_products = Product.query.filter(
        and_(Product.is_active == True, Product.stock_quantity == 0)
    ).count()
    
    # Get products by category
    category_stats = db.session.query(
        Product.category,
        func.count(Product.id).label('count')
    ).filter(Product.is_active == True).group_by(Product.category).all()
    
    # Get recent products
    recent_products = Product.query.order_by(Product.created_at.desc()).limit(10).all()
    
    # Get low stock products
    low_stock_list = Product.query.filter(
        and_(Product.is_active == True, Product.stock_quantity <= Product.reorder_level)
    ).order_by(Product.stock_quantity.asc()).limit(10).all()
    
    return render_template('products/dashboard.html',
                         stats={
                             'total': total_products,
                             'active': active_products,
                             'low_stock': low_stock_products,
                             'out_of_stock': out_of_stock_products
                         },
                         category_stats=category_stats,
                         recent_products=recent_products,
                         low_stock_list=low_stock_list) 

@products_bp.route('/debug')
@login_required
def debug_products():
    """Debug route to check products database status."""
    try:
        # Basic product count
        total_products = Product.query.count()
        
        # Check if any products exist
        first_product = Product.query.first()
        
        # Get table info
        from sqlalchemy import text
        result = db.session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'products'"))
        table_exists = result.fetchone() is not None
        
        debug_info = {
            'table_exists': table_exists,
            'total_products': total_products,
            'first_product': str(first_product) if first_product else None,
            'dev_database_url': str(db.engine.url),
        }
        
        return jsonify(debug_info)
        
    except Exception as e:
        logger.error(f"Error in debug route: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500 