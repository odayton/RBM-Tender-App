from flask import (
    Blueprint, 
    render_template, 
    request, 
    redirect, 
    url_for, 
    flash, 
    jsonify
)
from app.models.pumps.pump_model import Pump
from app.models.deals.deal_quote_model import Deal, DealStage
from app.app_extensions import db
from app.models.user_model import User, UserRole
from app.core.core_errors import ValidationError
from .forms import (
    PumpUploadForm,
    TechDataUploadForm,
    ManageInertiaBasesForm,
    ManageSeismicSpringsForm,
    ManageRubberMountsForm,
    ContactForm,
    DealOwnerForm,
    CompanyForm # Import the new form
)

import secrets

routes = Blueprint('admin', __name__)

@routes.route('/dashboard')
def dashboard():
    """Admin dashboard view"""
    deals = Deal.query.all()
    deal_stats = {
        'total': len(deals),
        'won': len([d for d in deals if d.stage == DealStage.WON]),
        'active': len([d for d in deals if d.stage not in [DealStage.WON, DealStage.LOST, DealStage.ABANDONED]])
    }
    
    return render_template(
        'admin/dashboard.html',
        deal_stats=deal_stats
    )

@routes.route('/create-contact', methods=['GET', 'POST'])
def create_contact():
    """Create a new contact"""
    form = ContactForm()
    if form.validate_on_submit():
        flash('Contact created successfully!', 'success')
        return redirect(url_for('admin.admin.dashboard'))
        
    return render_template(
        'admin/create_contact.html',
        form=form
    )

@routes.route('/create-deal-owner', methods=['GET', 'POST'])
def create_deal_owner():
    """Create a new deal owner"""
    form = DealOwnerForm()
    if form.validate_on_submit():
        try:
            # Create a new User object, satisfying all required fields
            new_owner = User(
                username=form.email.data,
                email=form.email.data,
                password=secrets.token_hex(16),
                # --- START OF THE FIX ---
                # Explicitly set the required 'role' field
                role=UserRole.SALES 
                # --- END OF THE FIX ---
            )

            # Safely set other attributes
            if hasattr(new_owner, 'first_name'):
                new_owner.first_name = form.name.data
            
            if hasattr(new_owner, 'phone_number'):
                new_owner.phone_number = form.phone_number.data
            
            db.session.add(new_owner)
            db.session.commit()
            
            flash('Deal Owner created successfully!', 'success')
            # Use the correct endpoint name we fixed before
            return redirect(url_for('admin.admin.dashboard')) 
            
        except Exception as e:
            db.session.rollback()
            # We are keeping this print statement just in case
            print(f"--- DATABASE ERROR: {e} ---")
            flash(f'Error creating deal owner: {e}', 'danger')

    elif request.method == 'POST':
        print(f"--- FORM VALIDATION FAILED: {form.errors} ---")
    
    return render_template(
        'admin/create_deal_owner.html',
        form=form
    )

@routes.route('/create-company', methods=['GET', 'POST'])
def create_company():
    """Create a new company"""
    form = CompanyForm()
    if form.validate_on_submit():
        flash('Company created successfully!', 'success')
        return redirect(url_for('admin.admin.dashboard'))
        
    return render_template(
        'admin/create_company.html',
        form=form
    )

@routes.route('/pumps', methods=['GET'])
def manage_pumps():
    """Pump management view"""
    pumps = Pump.query.all()
    return render_template(
        'admin/manage_pumps.html',
        pumps=pumps
    )

@routes.route('/tech-data/upload', methods=['GET', 'POST'])
def upload_tech_data():
    """Technical data upload view"""
    form = TechDataUploadForm()
    
    if form.validate_on_submit():
        try:
            file = form.file.data
            flash('Technical data uploaded successfully', 'success')
            return redirect(url_for('admin.manage_pumps'))
        except ValidationError as e:
            flash(str(e), 'error')
    
    return render_template(
        'admin/tech_data_upload.html',
        form=form
    )

@routes.route('/inertia-bases', methods=['GET', 'POST'])
def manage_inertia_bases():
    """Inertia bases management view"""
    form = ManageInertiaBasesForm()
    
    return render_template(
        'admin/manage_inertia_bases.html',
        form=form
    )

@routes.route('/seismic-springs', methods=['GET', 'POST'])
def manage_seismic_springs():
    """Seismic springs management view"""
    form = ManageSeismicSpringsForm()
    
    return render_template(
        'admin/manage_seismic_springs.html',
        form=form
    )

@routes.route('/rubber-mounts', methods=['GET', 'POST'])
def manage_rubber_mounts():
    """Rubber mounts management view"""
    form = ManageRubberMountsForm()
    
    return render_template(
        'admin/manage_rubber_mounts.html',
        form=form
    )

@routes.route('/blank-tech-data/upload', methods=['GET', 'POST'])
def blank_tech_data_upload():
    """Blank technical data upload view"""
    form = PumpUploadForm()
    
    if form.validate_on_submit():
        try:
            file = form.file.data
            flash('Blank technical data uploaded successfully', 'success')
            return redirect(url_for('admin.view_blank_tech_data'))
        except ValidationError as e:
            flash(str(e), 'error')
    
    return render_template(
        'admin/blank_tech_data_upload.html',
        form=form
    )

@routes.route('/blank-tech-data/view')
def view_blank_tech_data():
    """View blank technical data"""
    return render_template(
        'admin/view_blank_tech_data.html'
    )

@routes.route('/bom', methods=['GET'])
def manage_bom():
    """Bill of materials management view"""
    return render_template(
        'admin/manage_bom.html'
    )

@routes.route('/additional-price-adders', methods=['GET'])
def manage_additional_price_adders():
    """Additional price adders management view"""
    return render_template(
        'admin/manage_additional_price_adders.html'
    )

@routes.route('/select-sheet', methods=['GET', 'POST'])
def select_sheet():
    """Sheet selection view"""
    if request.method == 'POST':
        sheet_name = request.form.get('sheet_name')
        if sheet_name:
            return redirect(url_for('admin.dashboard'))
            
    return render_template(
        'admin/select_sheet.html'
    )