from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required

# Import the correct blueprint from the __init__.py file in this directory
from . import admin_bp
from .forms import (CompanyForm, ContactForm, DealOwnerForm,
                    InertiaBaseForm, RubberMountsForm, SeismicSpringsForm,
                    AdditionalPriceAddersForm)
from .helpers import (add_new_generic, get_all_generic, get_generic_by_id,
                      update_generic, delete_generic, get_all_paginated)
from app.models import (Company, Contact, DealOwner, InertiaBase,
                        RubberMounts, SeismicSprings, AdditionalPriceAdders)
from app.utils.db_utils.import_export import ExcelDataImportManager
from app.utils.file_utils.file_validation import FileValidation
from app.core.core_logging import logger

# A dictionary to map item types to their respective classes and forms
ITEM_TYPE_MAPPING = {
    'company': {'model': Company, 'form': CompanyForm},
    'contact': {'model': Contact, 'form': ContactForm},
    'deal_owner': {'model': DealOwner, 'form': DealOwnerForm},
    'inertia_base': {'model': InertiaBase, 'form': InertiaBaseForm},
    'rubber_mounts': {'model': RubberMounts, 'form': RubberMountsForm},
    'seismic_springs': {'model': SeismicSprings, 'form': SeismicSpringsForm},
    'price_adders': {'model': AdditionalPriceAdders, 'form': AdditionalPriceAddersForm},
}


@admin_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('admin/dashboard.html')


@admin_bp.route('/<item_type>/add', methods=['GET', 'POST'])
@login_required
def add_item(item_type):
    if item_type not in ITEM_TYPE_MAPPING:
        flash(f'Invalid item type: {item_type}', 'error')
        return redirect(url_for('admin.dashboard'))
    
    form = ITEM_TYPE_MAPPING[item_type]['form']()
    model = ITEM_TYPE_MAPPING[item_type]['model']
    
    if form.validate_on_submit():
        try:
            add_new_generic(model, form)
            flash(f'{item_type.replace("_", " ").title()} added successfully!', 'success')
            return redirect(url_for('admin.manage_items', item_type=item_type))
        except Exception as e:
            logger.error(f"--- DATABASE ERROR when adding {item_type}: {e} ---")
            flash(f'Error adding {item_type.replace("_", " ").title()}.', 'error')
            
    return render_template('admin/create_generic.html', form=form, item_type=item_type)


@admin_bp.route('/<item_type>/manage')
@login_required
def manage_items(item_type):
    if item_type not in ITEM_TYPE_MAPPING:
        flash(f'Invalid item type: {item_type}', 'error')
        return redirect(url_for('admin.dashboard'))

    page = request.args.get('page', 1, type=int)
    model = ITEM_TYPE_MAPPING[item_type]['model']
    items, pagination = get_all_paginated(model, page)
    
    return render_template('admin/manage_base.html', items=items, item_type=item_type, pagination=pagination)


@admin_bp.route('/<item_type>/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_item(item_type, item_id):
    if item_type not in ITEM_TYPE_MAPPING:
        flash(f'Invalid item type: {item_type}', 'error')
        return redirect(url_for('admin.dashboard'))
    
    model = ITEM_TYPE_MAPPING[item_type]['model']
    item = get_generic_by_id(model, item_id)
    if not item:
        flash(f'{item_type.replace("_", " ").title()} not found.', 'error')
        return redirect(url_for('admin.manage_items', item_type=item_type))

    form = ITEM_TYPE_MAPPING[item_type]['form'](obj=item)
    
    if form.validate_on_submit():
        try:
            update_generic(item, form)
            flash(f'{item_type.replace("_", " ").title()} updated successfully!', 'success')
            return redirect(url_for('admin.manage_items', item_type=item_type))
        except Exception as e:
            logger.error(f"--- DATABASE ERROR when editing {item_type}: {e} ---")
            flash(f'Error updating {item_type.replace("_", " ").title()}.', 'error')
            
    return render_template('admin/create_generic.html', form=form, item_type=item_type, item_id=item_id)


@admin_bp.route('/<item_type>/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_item(item_type, item_id):
    if item_type not in ITEM_TYPE_MAPPING:
        flash(f'Invalid item type: {item_type}', 'error')
        return redirect(url_for('admin.dashboard'))

    model = ITEM_TYPE_MAPPING[item_type]['model']
    
    try:
        delete_generic(model, item_id)
        flash(f'{item_type.replace("_", " ").title()} deleted successfully!', 'success')
    except Exception as e:
        logger.error(f"--- DATABASE ERROR when deleting {item_type}: {e} ---")
        flash(f'Error deleting {item_type.replace("_", " ").title()}.', 'error')
        
    return redirect(url_for('admin.manage_items', item_type=item_type))


@admin_bp.route('/upload_excel', methods=['POST'])
@login_required
def upload_excel():
    file = request.files.get('excel_file')
    if not file:
        flash('No file selected.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    is_valid, message = FileValidation.is_allowed(file.filename)
    if not is_valid:
        flash(message, 'error')
        return redirect(url_for('admin.dashboard'))

    try:
        importer = ExcelDataImportManager()
        importer.import_data(file)
        flash('Excel file imported successfully!', 'success')
    except Exception as e:
        logger.error(f"--- EXCEL IMPORT ERROR: {e} ---")
        flash(f'An error occurred during import: {e}', 'error')
        
    return redirect(url_for('admin.dashboard'))