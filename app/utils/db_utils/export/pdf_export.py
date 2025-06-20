from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required

from . import admin_bp
from .forms import (CompanyForm, ContactForm, DealOwnerForm,
                    ManageInertiaBasesForm, ManageRubberMountsForm, ManageSeismicSpringsForm,
                    AdditionalPriceAdderForm)
from app.utils.db_utils.import.excel_import import ExcelImporter
from app.models import (Company, Contact, User, InertiaBase,
                        SeismicSpring)
from app.utils.file_utils.file_validation import FileValidation
from app.core.core_logging import logger

ITEM_TYPE_MAPPING = {
    'company': {'model': Company, 'form': CompanyForm},
    'contact': {'model': Contact, 'form': ContactForm},
    'deal_owner': {'model': User, 'form': DealOwnerForm},
    'inertia_base': {'model': InertiaBase, 'form': ManageInertiaBasesForm},
    'seismic_springs': {'model': SeismicSpring, 'form': ManageSeismicSpringsForm},
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
    
    form_class = ITEM_TYPE_MAPPING[item_type]['form']
    model_class = ITEM_TYPE_MAPPING[item_type]['model']
    form = form_class()
    
    if form.validate_on_submit():
        try:
            new_item = model_class()
            form.populate_obj(new_item)
            new_item.save()
            
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
    
    pagination = model.query.paginate(page=page, per_page=10, error_out=False)
    items = pagination.items
    
    return render_template('admin/manage_base.html', items=items, item_type=item_type, pagination=pagination)


@admin_bp.route('/<item_type>/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_item(item_type, item_id):
    if item_type not in ITEM_TYPE_MAPPING:
        flash(f'Invalid item type: {item_type}', 'error')
        return redirect(url_for('admin.manage_items', item_type=item_type))
    
    model_class = ITEM_TYPE_MAPPING[item_type]['model']
    item = model_class.get_by_id(item_id)
    if not item:
        flash(f'{item_type.replace("_", " ").title()} not found.', 'error')
        return redirect(url_for('admin.manage_items', item_type=item_type))

    form_class = ITEM_TYPE_MAPPING[item_type]['form']
    form = form_class(obj=item)
    
    if form.validate_on_submit():
        try:
            form.populate_obj(item)
            item.save()
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

    model_class = ITEM_TYPE_MAPPING[item_type]['model']
    item = model_class.get_by_id(item_id)
    
    if item:
        try:
            item.delete()
            flash(f'{item_type.replace("_", " ").title()} deleted successfully!', 'success')
        except Exception as e:
            logger.error(f"--- DATABASE ERROR when deleting {item_type}: {e} ---")
            flash(f'Error deleting {item_type.replace("_", " ").title()}.', 'error')
    else:
        flash(f'{item_type.replace("_", " ").title()} not found.', 'error')
        
    return redirect(url_for('admin.manage_items', item_type=item_type))