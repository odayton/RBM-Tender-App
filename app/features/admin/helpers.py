from flask import (
    render_template, 
    request, 
    redirect, 
    url_for, 
    flash
)

# Import the blueprint object, forms, and helpers from the local package
from . import admin_bp
from .forms import (
    ContactForm, DealOwnerForm, CompanyForm, BOMUploadForm, AdditionalPriceAdderForm
)

# Import the ORM models and db session for creation logic
from app.extensions import db
from app.models import (
    User, UserRole, Company, Contact, Deal, DealStage
)
from app.core.core_errors import ValidationError
import secrets

# Removed duplicate dashboard route - it's already defined in routes.py

@admin_bp.route('/create-company', methods=['GET', 'POST'])
def create_company():
    """Handles the creation of a new company."""
    form = CompanyForm()
    if form.validate_on_submit():
        # This logic should eventually be moved to a CompanyManager
        try:
            new_company = Company(
                company_name=form.company_name.data,
                address=form.address.data
            )
            db.session.add(new_company)
            db.session.commit()
            flash('Company created successfully!', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating company: {e}', 'danger')
        
    return render_template('admin/create_company.html', form=form)

@admin_bp.route('/create-contact', methods=['GET', 'POST'])
def create_contact():
    """Handles creating a new contact."""
    form = ContactForm()
    if form.validate_on_submit():
        # This logic should eventually be moved to a ContactManager
        try:
            # Note: A real implementation would need a Customer model
            new_contact = Contact(
                name=form.name.data,
                email=form.email.data,
                phone_number=form.phone_number.data,
                mobile_number=form.mobile_number.data,
                position=form.position.data,
                company_id=form.company_id.data
            )
            db.session.add(new_contact)
            db.session.commit()
            flash('Contact created successfully!', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating contact: {e}', 'danger')

    return render_template('admin/create_contact.html', form=form)

@admin_bp.route('/create-deal-owner', methods=['GET', 'POST'])
def create_deal_owner():
    """Handles creating a new deal owner (user)."""
    form = DealOwnerForm()
    if form.validate_on_submit():
        # This logic should eventually be moved to a UserManager
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('A user with that email already exists.', 'danger')
        else:
            try:
                new_owner = User(
                    username=form.email.data,
                    email=form.email.data,
                    password=secrets.token_hex(16),
                    first_name=form.name.data,
                    phone_number=form.phone_number.data,
                    role=UserRole.SALES
                )
                db.session.add(new_owner)
                db.session.commit()
                flash('Deal Owner created successfully!', 'success')
                return redirect(url_for('admin.dashboard'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error creating deal owner: {e}', 'danger')
    
    return render_template('admin/create_deal_owner.html', form=form)













@admin_bp.route('/bom', methods=['GET'])
def manage_bom():
    """Renders the Bill of Materials management page."""
    return render_template('admin/manage_bom.html')

@admin_bp.route('/additional-price-adders', methods=['GET'])
def manage_additional_price_adders():
    """Renders the page to manage additional price adders."""
    return render_template('admin/manage_additional_price_adders.html')

@admin_bp.route('/select-sheet', methods=['GET', 'POST'])
def select_sheet():
    """Handles sheet selection from an uploaded file."""
    if request.method == 'POST':
        sheet_name = request.form.get('sheet_name')
        if sheet_name:
            flash(f'Sheet "{sheet_name}" selected (logic to be implemented).', 'info')
            return redirect(url_for('admin.dashboard'))
            
    return render_template('admin/select_sheet.html')