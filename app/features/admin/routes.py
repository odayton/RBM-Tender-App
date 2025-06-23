from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required
import secrets
import string

from . import admin_bp
from .forms import (CompanyForm, ContactForm, DealOwnerForm,
                    ManageInertiaBasesForm, ManageSeismicSpringsForm,
                    ManageRubberMountsForm, AdditionalPriceAdderForm)
from app.models import (Company, Contact, User, InertiaBase, SeismicSpring, 
                        RubberMount, AdditionalPriceAdder, Deal, Pump)
from app.core.core_logging import logger

# We are expanding the mapping to include more metadata for the front-end.
# - display_name: A user-friendly name for the item.
# - columns: A list of model attributes to display in the management table.
ITEM_TYPE_MAPPING = {
    'company': {
        'model': Company, 
        'form': CompanyForm,
        'display_name': 'Companies',
        'columns': ['id', 'name', 'email', 'phone_number']
    },
    'contact': {
        'model': Contact, 
        'form': ContactForm,
        'display_name': 'Contacts',
        'columns': ['id', 'name', 'email', 'phone_number']
    },
    'deal_owner': {
        'model': User, 
        'form': DealOwnerForm,
        'display_name': 'Deal Owners',
        'columns': ['id', 'username', 'email']
    },
    'inertia_base': {
        'model': InertiaBase, 
        'form': ManageInertiaBasesForm,
        'display_name': 'Inertia Bases',
        'columns': ['id', 'base_size', 'weight', 'price']
    },
    'seismic_springs': {
        'model': SeismicSpring, 
        'form': ManageSeismicSpringsForm,
        'display_name': 'Seismic Springs',
        'columns': ['id', 'model', 'spring_rate', 'price']
    },
    'rubber_mounts': {
        'model': RubberMount, 
        'form': ManageRubberMountsForm,
        'display_name': 'Rubber Mounts',
        'columns': ['id', 'model', 'max_deflection', 'price']
    },
    'price_adders': {
        'model': AdditionalPriceAdder, 
        'form': AdditionalPriceAdderForm,
        'display_name': 'Price Adders',
        'columns': ['id', 'name', 'price']
    },
}

@admin_bp.route('/dashboard')
def dashboard():
    # Pass the mapping to the template to generate links dynamically.
    return render_template('admin/dashboard.html', management_items=ITEM_TYPE_MAPPING)


@admin_bp.route('/<item_type>/manage')
def manage_items(item_type):
    if item_type not in ITEM_TYPE_MAPPING:
        flash(f'Invalid item type: {item_type}', 'error')
        return redirect(url_for('admin.dashboard'))

    page = request.args.get('page', 1, type=int)
    config = ITEM_TYPE_MAPPING[item_type]
    model = config['model']
    
    pagination = model.query.paginate(page=page, per_page=15, error_out=False)
    items = pagination.items
    
    # Pass the specific config for this item_type to the template
    return render_template(
        'admin/manage_base.html', 
        items=items, 
        item_type=item_type, 
        config=config, 
        pagination=pagination
    )


@admin_bp.route('/<item_type>/add', methods=['GET', 'POST'])
def add_item(item_type):
    if item_type not in ITEM_TYPE_MAPPING:
        flash(f'Invalid item type: {item_type}', 'error')
        return redirect(url_for('admin.dashboard'))
    
    config = ITEM_TYPE_MAPPING[item_type]
    form_class = config.get('form')
    model_class = config['model']
    
    if not form_class:
        flash(f'No form defined for this item type: {item_type}', 'warning')
        return redirect(url_for('admin.dashboard'))
        
    form = form_class()
    
    if form.validate_on_submit():
        try:
            new_item = model_class()
            
            # This special handling for user password should ideally be moved 
            # into a model method (e.g., User.create_new(...)) in the future.
            if item_type == 'deal_owner':
                new_item.username = form.username.data
                new_item.email = form.email.data
                new_item.phone_number = form.phone_number.data
                alphabet = string.ascii_letters + string.digits
                password = ''.join(secrets.choice(alphabet) for i in range(12))
                new_item.set_password(password) # Using a method is better for hashing
                flash(f'Deal Owner created. Temporary Password: {password}', 'info')
            else:
                form.populate_obj(new_item)

            new_item.save()
            flash(f'{config["display_name"]} item added successfully!', 'success')
            return redirect(url_for('admin.manage_items', item_type=item_type))
        except Exception as e:
            logger.error(f"--- DATABASE ERROR when adding {item_type}: {e} ---")
            flash(f'Error adding {config["display_name"]} item.', 'error')
            
    return render_template('admin/create_generic.html', form=form, item_type=item_type, config=config)


@admin_bp.route('/<item_type>/<int:item_id>/edit', methods=['GET', 'POST'])
def edit_item(item_type, item_id):
    if item_type not in ITEM_TYPE_MAPPING:
        flash(f'Invalid item type: {item_type}', 'error')
        return redirect(url_for('admin.manage_items', item_type=item_type))
    
    config = ITEM_TYPE_MAPPING[item_type]
    model_class = config['model']
    item = model_class.get_by_id(item_id)
    if not item:
        flash(f'{config["display_name"]} item not found.', 'error')
        return redirect(url_for('admin.manage_items', item_type=item_type))

    form_class = config.get('form')
    if not form_class:
        flash(f'No form defined for this item type: {item_type}', 'warning')
        return redirect(url_for('admin.manage_items', item_type=item_type))

    form = form_class(obj=item)
    
    if form.validate_on_submit():
        try:
            # Special case for user edit to avoid changing the password unless intended
            if item_type == 'deal_owner':
                item.username = form.username.data
                item.email = form.email.data
                item.phone_number = form.phone_number.data
                # Password is not handled here, would require a separate "Change Password" form
            else:
                form.populate_obj(item)

            item.save()
            flash(f'{config["display_name"]} item updated successfully!', 'success')
            return redirect(url_for('admin.manage_items', item_type=item_type))
        except Exception as e:
            logger.error(f"--- DATABASE ERROR when editing {item_type}: {e} ---")
            flash(f'Error updating {config["display_name"]} item.', 'error')
            
    return render_template('admin/create_generic.html', form=form, item_type=item_type, item_id=item_id, config=config)


@admin_bp.route('/<item_type>/<int:item_id>/delete', methods=['POST'])
def delete_item(item_type, item_id):
    if item_type not in ITEM_TYPE_MAPPING:
        flash(f'Invalid item type: {item_type}', 'error')
        return redirect(url_for('admin.dashboard'))

    config = ITEM_TYPE_MAPPING[item_type]
    model_class = config['model']
    item = model_class.get_by_id(item_id)
    
    if item:
        try:
            item.delete()
            flash(f'{config["display_name"]} item deleted successfully!', 'success')
        except Exception as e:
            logger.error(f"--- DATABASE ERROR when deleting {item_type}: {e} ---")
            # A common error is deleting an item that is linked by a foreign key
            flash(f'Error deleting item. It may be in use by another part of the application. ({e})', 'error')
    else:
        flash(f'{config["display_name"]} item not found.', 'error')
        
    return redirect(url_for('admin.manage_items', item_type=item_type))