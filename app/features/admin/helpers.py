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
    PumpUploadForm, TechDataUploadForm, ManageInertiaBasesForm,
    ManageSeismicSpringsForm, ManageRubberMountsForm, ContactForm,
    DealOwnerForm, CompanyForm, BOMUploadForm, AdditionalPriceAdderForm
)
from .helpers import AdminDashboard, DataExporter, DataImporter

# Import the ORM models and db session for creation logic
from app.models import (
    db, Pump, User, UserRole, Company, Customer, Deal, DealStage
)
from app.core.core_errors import ValidationError
import secrets

@admin_bp.route('/dashboard')
def dashboard():
    """Renders the main admin dashboard with statistics."""
    # Use the helper class to get statistics, keeping the route clean
    deal_stats = AdminDashboard.get_deal_statistics()
    pump_stats = AdminDashboard.get_pump_statistics()
    
    return render_template(
        'admin/dashboard.html',
        deal_stats=deal_stats,
        pump_stats=pump_stats
    )

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
            new_contact = Customer(
                name=form.name.data,
                email=form.email.data,
                phone_number=form.phone.data,
                position=form.position.data,
                company_id=form.company.data.id
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

@admin_bp.route('/pumps', methods=['GET'])
def manage_pumps():
    """Displays the pump management page."""
    # This should use a PumpManager in the future
    pumps = Pump.query.all()
    return render_template('admin/manage_pumps.html', pumps=pumps)

@admin_bp.route('/tech-data/upload', methods=['GET', 'POST'])
def upload_tech_data():
    """Handles uploading technical data from a file."""
    form = TechDataUploadForm()
    if form.validate_on_submit():
        # You would use the DataImporter helper here
        flash('File processed (logic to be implemented).', 'info')
        return redirect(url_for('admin.manage_pumps'))
    
    return render_template('admin/tech_data_upload.html', form=form)

@admin_bp.route('/inertia-bases', methods=['GET', 'POST'])
def manage_inertia_bases():
    """Renders the page to manage inertia bases."""
    form = ManageInertiaBasesForm()
    if form.validate_on_submit():
        flash('Inertia Base saved (logic to be implemented).', 'info')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/manage_inertia_bases.html', form=form)

@admin_bp.route('/seismic-springs', methods=['GET', 'POST'])
def manage_seismic_springs():
    """Renders the page to manage seismic springs."""
    form = ManageSeismicSpringsForm()
    if form.validate_on_submit():
        flash('Seismic Spring saved (logic to be implemented).', 'info')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/manage_seismic_springs.html', form=form)

@admin_bp.route('/rubber-mounts', methods=['GET', 'POST'])
def manage_rubber_mounts():
    """Renders the page to manage rubber mounts."""
    form = ManageRubberMountsForm()
    if form.validate_on_submit():
        flash('Rubber Mount saved (logic to be implemented).', 'info')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/manage_rubber_mounts.html', form=form)

@admin_bp.route('/blank-tech-data/upload', methods=['GET', 'POST'])
def blank_tech_data_upload():
    """Handles uploading a blank technical data sheet."""
    form = PumpUploadForm()
    if form.validate_on_submit():
        flash('File processed (logic to be implemented).', 'info')
        return redirect(url_for('admin.view_blank_tech_data'))
    
    return render_template('admin/blank_tech_data_upload.html', form=form)

@admin_bp.route('/blank-tech-data/view')
def view_blank_tech_data():
    """Displays a page for viewing blank technical data."""
    return render_template('admin/view_blank_tech_data.html')

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