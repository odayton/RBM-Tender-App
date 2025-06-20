from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required
import secrets
import string

from . import admin_bp
from .forms import (CompanyForm, ContactForm, DealOwnerForm,
                    ManageInertiaBasesForm, ManageSeismicSpringsForm,
                    ManageRubberMountsForm, AdditionalPriceAdderForm)
from app.models import (Company, Contact, User, InertiaBase, SeismicSpring, RubberMount, AdditionalPriceAdder, Deal, Pump)
from app.core.core_logging import logger

ITEM_TYPE_MAPPING = {
    'company': {'model': Company, 'form': CompanyForm},
    'contact': {'model': Contact, 'form': ContactForm},
    'deal_owner': {'model': User, 'form': DealOwnerForm},
    'inertia_base': {'model': InertiaBase, 'form': ManageInertiaBasesForm},
    'seismic_springs': {'model': SeismicSpring, 'form': ManageSeismicSpringsForm},
    'rubber_mounts': {'model': RubberMount, 'form': ManageRubberMountsForm},
    'price_adders': {'model': AdditionalPriceAdder, 'form': AdditionalPriceAdderForm},
}

@admin_bp.route('/dashboard')
def dashboard():
    return render_template('admin/dashboard.html')


@admin_bp.route('/<item_type>/add', methods=['GET', 'POST'])
def add_item(item_type):
    if item_type not in ITEM_TYPE_MAPPING:
        flash(f'Invalid item type: {item_type}', 'error')
        return redirect(url_for('admin.dashboard'))
    
    form_class = ITEM_TYPE_MAPPING[item_type]['form']
    model_class = ITEM_TYPE_MAPPING[item_type]['model']
    
    if not form_class:
        flash(f'No form defined for this item type: {item_type}', 'warning')
        return redirect(url_for('admin.dashboard'))
        
    form = form_class()
    
    if form.validate_on_submit():
        try:
            new_item = model_class()
            
            if item_type == 'deal_owner':
                new_item.username = form.username.data
                new_item.email = form.email.data
                new_item.phone_number = form.phone_number.data
                alphabet = string.ascii_letters + string.digits
                password = ''.join(secrets.choice(alphabet) for i in range(12))
                new_item.password = password
            else:
                form.populate_obj(new_item)

            new_item.save()
            flash(f'{item_type.replace("_", " ").title()} added successfully!', 'success')
            return redirect(url_for('admin.manage_items', item_type=item_type))
        except Exception as e:
            logger.error(f"--- DATABASE ERROR when adding {item_type}: {e} ---")
            flash(f'Error adding {item_type.replace("_", " ").title()}.', 'error')
            
    return render_template('admin/create_generic.html', form=form, item_type=item_type)


@admin_bp.route('/<item_type>/manage')
def manage_items(item_type):
    if item_type not in ITEM_TYPE_MAPPING:
        flash(f'Invalid item type: {item_type}', 'error')
        return redirect(url_for('admin.dashboard'))

    page = request.args.get('page', 1, type=int)
    model = ITEM_TYPE_MAPPING[item_type]['model']
    form_class = ITEM_TYPE_MAPPING[item_type]['form']
    
    form = form_class() if form_class else None
    
    pagination = model.query.paginate(page=page, per_page=10, error_out=False)
    items = pagination.items
    
    return render_template('admin/manage_base.html', items=items, item_type=item_type, pagination=pagination, form=form)


@admin_bp.route('/<item_type>/<int:item_id>/edit', methods=['GET', 'POST'])
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
    if not form_class:
        flash(f'No form defined for this item type: {item_type}', 'warning')
        return redirect(url_for('admin.manage_items', item_type=item_type))

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