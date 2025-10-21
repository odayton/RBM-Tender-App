from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.features.admin import admin_bp
from app.core.core_security import admin_required, rate_limit, security_manager
from app.core.core_rate_limiting import admin_rate_limit, security_rate_limit
from app.core.core_logging import logger
from app.models import User, UserRole, Company, Contact
from app.models.deals.deal_models import Discount
from app.models.pumps import (
    PumpSeries, Pump, InertiaBase, SeismicSpring, RubberMount,
    Crossbar, MotorProtection, DripTripTray, PumpDutyPoint,
    PumpBOM, PumpComponent
)
from app.features.admin.forms import (
    CreateUserForm, EditUserForm, CompanyForm, ContactForm, DiscountForm,
    PumpSeriesForm, PumpForm, InertiaBaseForm, SeismicSpringForm, RubberMountForm,
    CrossbarForm, MotorProtectionForm, DripTripTrayForm, PumpDutyPointForm,
    PumpBOMForm, PumpComponentForm, BOMImportForm, SeismicSpringImportForm,
    BulkComponentImportForm
)
from app.utils.db_utils.organization.db_companies import CompanyManager
from app.utils.db_utils.organization.db_contacts import ContactManager
from app.utils.db_utils.organization.db_deal_owners import DealOwnerManager
from app.utils.bom_import_export import export_bom_to_csv, import_bom_from_csv, generate_sample_csv
from app.utils.seismic_spring_import_export import (
    export_seismic_springs_to_csv, 
    import_seismic_springs_from_csv, 
    generate_seismic_spring_sample_csv
)
from app.utils.bulk_component_import_export import (
    export_pump_series_to_csv, import_pump_series_from_csv,
    export_pumps_to_csv, import_pumps_from_csv,
    export_inertia_bases_to_csv, import_inertia_bases_from_csv,
    export_rubber_mounts_to_csv, import_rubber_mounts_from_csv,
    export_crossbars_to_csv, import_crossbars_from_csv,
    export_motor_protection_to_csv, import_motor_protection_from_csv,
    export_drip_trays_to_csv, import_drip_trays_from_csv,
    export_duty_points_to_csv, import_duty_points_from_csv,
    export_generic_components_to_csv, import_generic_components_from_csv
)

# Import helpers to register additional routes
from . import helpers

# Management items configuration
MANAGEMENT_ITEMS = {
    'company': {
        'display_name': 'Companies',
        'model': Company,
        'form': CompanyForm,
        'columns': ['company_name', 'phone_number', 'domain'],
        'category': 'general'
    },
    'contact': {
        'display_name': 'Contacts',
        'model': Contact,
        'form': ContactForm,
        'columns': ['name', 'email', 'phone_number', 'position'],
        'category': 'general'
    },
    'discount': {
        'display_name': 'Discounts',
        'model': Discount,
        'form': DiscountForm,
        'columns': ['code', 'percentage', 'is_active'],
        'category': 'general'
    },
    # HVAC Management Items
    'pump-series': {
        'display_name': 'Pump Series',
        'model': PumpSeries,
        'form': PumpSeriesForm,
        'columns': ['series_code', 'series_name', 'is_active'],
        'category': 'hvac'
    },
    'pump': {
        'display_name': 'Pumps',
        'model': Pump,
        'form': PumpForm,
        'columns': ['part_number', 'name', 'series.series_code', 'list_price', 'is_active'],
        'category': 'hvac'
    },
    'inertia-base': {
        'display_name': 'Inertia Bases',
        'model': InertiaBase,
        'form': InertiaBaseForm,
        'columns': ['part_number', 'description', 'list_price', 'is_active'],
        'category': 'hvac'
    },
    'seismic-spring': {
        'display_name': 'Seismic Springs',
        'model': SeismicSpring,
        'form': SeismicSpringForm,
        'columns': ['part_number', 'description', 'max_load_kg', 'is_active'],
        'category': 'hvac'
    },
    'rubber-mount': {
        'display_name': 'Rubber Mounts',
        'model': RubberMount,
        'form': RubberMountForm,
        'columns': ['sku', 'item_description', 'list_price', 'is_active'],
        'category': 'hvac'
    },
    'crossbar': {
        'display_name': 'Crossbars',
        'model': Crossbar,
        'form': CrossbarForm,
        'columns': ['sku', 'description', 'list_price', 'is_active'],
        'category': 'hvac'
    },
    'motor-protection': {
        'display_name': 'Motor Protection',
        'model': MotorProtection,
        'form': MotorProtectionForm,
        'columns': ['description', 'nett_cost', 'is_active'],
        'category': 'hvac'
    },
    'drip-trip-tray': {
        'display_name': 'Drip Trip Trays',
        'model': DripTripTray,
        'form': DripTripTrayForm,
        'columns': ['series.series_code', 'description', 'nett_cost', 'is_standard', 'is_active'],
        'category': 'hvac'
    },
    'duty-point': {
        'display_name': 'Duty Points',
        'model': PumpDutyPoint,
        'form': PumpDutyPointForm,
        'columns': ['flow_rate_lps', 'head_pressure_kpa', 'series.series_code', 'tolerance_percentage'],
        'category': 'hvac'
    },
    'pump-bom': {
        'display_name': 'Pump BOM (Bill of Materials)',
        'model': PumpBOM,
        'form': PumpBOMForm,
        'columns': ['pump.part_number', 'pump.name', 'component_type', 'component_id', 'quantity', 'is_optional'],
        'category': 'hvac'
    },
    'pump-component': {
        'display_name': 'Generic Components',
        'model': PumpComponent,
        'form': PumpComponentForm,
        'columns': ['component_type', 'part_number', 'description', 'list_price', 'is_active'],
        'category': 'hvac'
    }
}

# Import additional models and forms for specific routes
from app.features.admin.forms import DealOwnerForm
from app.core.core_security import security_manager
from app.core.core_errors import ValidationError
import secrets

def safe_getattr(obj, attr_name, default=''):
    """Safely get attribute from object, handling nested attributes."""
    try:
        if '.' in attr_name:
            # Handle nested attributes like 'company.company_name'
            parts = attr_name.split('.')
            value = obj
            for part in parts:
                value = getattr(value, part, None)
                if value is None:
                    break
            return value if value is not None else default
        else:
            # Handle direct attributes
            value = getattr(obj, attr_name, default)
            return value if value is not None else default
    except (AttributeError, TypeError):
        return default

# Register the function with the admin blueprint
admin_bp.add_app_template_filter(safe_getattr, 'safe_getattr')

@admin_bp.route('/create-company', methods=['GET', 'POST'])
@login_required
@admin_required
def create_company():
    """Handles the creation of a new company."""
    form = CompanyForm()
    if form.validate_on_submit():
        try:
            # Sanitize input to prevent XSS attacks
            company_name = security_manager.sanitize_input(form.company_name.data)
            phone_number = security_manager.sanitize_input(form.phone_number.data) if form.phone_number.data else None
            domain = security_manager.sanitize_input(form.domain.data) if form.domain.data else None
            
            new_company = Company(
                company_name=company_name,
                phone_number=phone_number,
                domain=domain
            )
            
            # Add validation call before saving
            new_company.validate()
            
            # Use transaction safety with savepoint
            from app.extensions import db
            with db.session.begin_nested():
                db.session.add(new_company)
                db.session.commit()
            
            logger.info(f"Admin created new company: {company_name}")
            flash('Company created successfully!', 'success')
            return redirect(url_for('admin.dashboard'))
            
        except ValidationError as e:
            from app.extensions import db
            db.session.rollback()
            logger.warning(f"Validation error creating company: {e}")
            flash(f'Validation error: {e}', 'error')
        except Exception as e:
            from app.extensions import db
            db.session.rollback()
            logger.error(f"Unexpected error creating company: {e}", exc_info=True)
            flash('An unexpected error occurred while creating the company. Please try again.', 'error')
        
    return render_template('admin/create_company.html', form=form)

@admin_bp.route('/create-contact', methods=['GET', 'POST'])
@login_required
@admin_required
def create_contact():
    """Handles creating a new contact."""
    form = ContactForm()
    if form.validate_on_submit():
        try:
            # Sanitize input to prevent XSS attacks
            name = security_manager.sanitize_input(form.name.data)
            email = security_manager.sanitize_input(form.email.data)
            phone_number = security_manager.sanitize_input(form.phone_number.data) if form.phone_number.data else None
            mobile_number = security_manager.sanitize_input(form.mobile_number.data) if form.mobile_number.data else None
            position = security_manager.sanitize_input(form.position.data) if form.position.data else None
            
            new_contact = Contact(
                name=name,
                email=email,
                phone_number=phone_number,
                mobile_number=mobile_number,
                position=position,
                company_id=form.company_id.data
            )
            
            # Add validation call before saving
            new_contact.validate()
            
            # Use transaction safety with savepoint
            from app.extensions import db
            with db.session.begin_nested():
                db.session.add(new_contact)
                db.session.commit()
            
            logger.info(f"Admin created new contact: {name} ({email})")
            flash('Contact created successfully!', 'success')
            return redirect(url_for('admin.dashboard'))
            
        except ValidationError as e:
            from app.extensions import db
            db.session.rollback()
            logger.warning(f"Validation error creating contact: {e}")
            flash(f'Validation error: {e}', 'error')
        except Exception as e:
            from app.extensions import db
            db.session.rollback()
            logger.error(f"Unexpected error creating contact: {e}", exc_info=True)
            flash('An unexpected error occurred while creating the contact. Please try again.', 'error')

    return render_template('admin/create_contact.html', form=form)

@admin_bp.route('/create-deal-owner', methods=['GET', 'POST'])
@login_required
@admin_required
def create_deal_owner():
    """Handles creating a new deal owner (user)."""
    form = DealOwnerForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('A user with that email already exists.', 'danger')
        else:
            try:
                # Sanitize input to prevent XSS attacks
                username = security_manager.sanitize_input(form.username.data)
                email = security_manager.sanitize_input(form.email.data)
                first_name = security_manager.sanitize_input(form.first_name.data)
                last_name = security_manager.sanitize_input(form.last_name.data)
                phone_number = security_manager.sanitize_input(form.phone_number.data) if form.phone_number.data else None
                
                # Generate a secure temporary password
                temp_password = secrets.token_hex(16)
                
                new_owner = User(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=phone_number,
                    role=UserRole.SALES
                )
                
                # Set password properly (this will hash it via the property setter)
                new_owner.password = temp_password
                
                # Use transaction safety with savepoint
                from app.extensions import db
                with db.session.begin_nested():
                    db.session.add(new_owner)
                    db.session.commit()
                
                logger.info(f"Admin created new deal owner: {username} ({email})")
                flash(f'Deal Owner created successfully! Temporary password: {temp_password}', 'success')
                flash('The user will be required to change their password on first login.', 'info')
                return redirect(url_for('admin.dashboard'))
                
            except ValidationError as e:
                from app.extensions import db
                db.session.rollback()
                logger.warning(f"Validation error creating deal owner: {e}")
                flash(f'Validation error: {e}', 'error')
            except Exception as e:
                from app.extensions import db
                db.session.rollback()
                logger.error(f"Unexpected error creating deal owner: {e}", exc_info=True)
                flash('An unexpected error occurred while creating the deal owner. Please try again.', 'error')
    
    return render_template('admin/create_deal_owner.html', form=form)

@admin_bp.route('/dashboard')
@login_required
@admin_required
@admin_rate_limit()
def dashboard():
    """Admin dashboard with enhanced security."""
    try:
        # Get system statistics
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        
        # Get recent activity (last 7 days)
        from datetime import datetime, timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_logins = User.query.filter(User.last_login >= week_ago).count()
        
        stats = {
            'total_users': total_users,
            'active_users': active_users,
            'recent_logins': recent_logins,
        }
        
        return render_template('admin/dashboard.html', stats=stats, management_items=MANAGEMENT_ITEMS)
        
    except Exception as e:
        logger.error(f"Error loading admin dashboard: {e}")
        flash('An error occurred while loading the dashboard.', 'error')
        return redirect(url_for('main.home'))

@admin_bp.route('/users')
@login_required
@admin_required
@rate_limit(max_requests=20, window_seconds=60)
def manage_users():
    """Manage users with enhanced security."""
    try:
        users = User.query.all()
        return render_template('admin/manage_users.html', users=users)
        
    except Exception as e:
        logger.error(f"Error loading users: {e}")
        flash('An error occurred while loading users.', 'error')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
@rate_limit(max_requests=10, window_seconds=300)
def create_user():
    """Create new user with enhanced validation."""
    form = CreateUserForm()
    
    if form.validate_on_submit():
        try:
            # Sanitize input
            username = security_manager.sanitize_input(form.username.data)
            email = security_manager.sanitize_input(form.email.data)
            first_name = security_manager.sanitize_input(form.first_name.data)
            last_name = security_manager.sanitize_input(form.last_name.data)
            
            # Check if user already exists
            if User.query.filter_by(email=email).first():
                flash('A user with this email already exists.', 'error')
                return render_template('admin/create_user.html', form=form)
            
            if User.query.filter_by(username=username).first():
                flash('A user with this username already exists.', 'error')
                return render_template('admin/create_user.html', form=form)
            
            # Create user with temporary password
            user = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone_number=form.phone_number.data,
                role=UserRole(form.role.data),
                is_active=True
            )
            
            # Generate secure temporary password
            temp_password = user.set_temporary_password()
            user.save()
            
            logger.info(f"Admin {current_user.email} created new user: {user.email}")
            flash(f'User {user.email} has been created successfully with temporary password: {temp_password}', 'success')
            flash('The user will be required to change their password on first login.', 'info')
            
            return redirect(url_for('admin.manage_users'))
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            flash('An error occurred while creating the user.', 'error')
    
    return render_template('admin/create_user.html', form=form)

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
@rate_limit(max_requests=15, window_seconds=300)
def edit_user(user_id):
    """Edit user with enhanced security."""
    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)
    
    if form.validate_on_submit():
        try:
            # Sanitize input
            username = security_manager.sanitize_input(form.username.data)
            email = security_manager.sanitize_input(form.email.data)
            first_name = security_manager.sanitize_input(form.first_name.data)
            last_name = security_manager.sanitize_input(form.last_name.data)
            
            # Check for conflicts
            existing_user = User.query.filter_by(email=email).first()
            if existing_user and existing_user.id != user_id:
                flash('A user with this email already exists.', 'error')
                return render_template('admin/edit_user.html', form=form, user=user)
            
            existing_user = User.query.filter_by(username=username).first()
            if existing_user and existing_user.id != user_id:
                flash('A user with this username already exists.', 'error')
                return render_template('admin/edit_user.html', form=form, user=user)
            
            # Update user
            user.username = username
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.phone_number = form.phone_number.data
            user.role = UserRole(form.role.data)
            user.is_active = form.is_active.data
            user.save()
            
            logger.info(f"Admin {current_user.email} updated user: {user.email}")
            flash('User has been updated successfully.', 'success')
            return redirect(url_for('admin.manage_users'))
            
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            flash('An error occurred while updating the user.', 'error')
    
    return render_template('admin/edit_user.html', form=form, user=user)

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
@rate_limit(max_requests=5, window_seconds=300)
def delete_user(user_id):
    """Delete user with enhanced security."""
    user = User.query.get_or_404(user_id)
    
    # Prevent self-deletion
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('admin.manage_users'))
    
    try:
        user_email = user.email
        user.delete()
        
        logger.info(f"Admin {current_user.email} deleted user: {user_email}")
        flash(f'User {user_email} has been deleted successfully.', 'success')
        
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        flash('An error occurred while deleting the user.', 'error')
    
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
@admin_required
@rate_limit(max_requests=5, window_seconds=300)
def reset_user_password(user_id):
    """Reset user password with enhanced security."""
    user = User.query.get_or_404(user_id)
    
    try:
        # Generate new temporary password
        temp_password = user.set_temporary_password()
        user.save()
        
        logger.info(f"Admin {current_user.email} reset password for user: {user.email}")
        flash(f'Password has been reset for {user.full_name}. Temporary password: {temp_password}', 'success')
        
    except Exception as e:
        logger.error(f"Error resetting password for user {user.email}: {e}")
        flash('An error occurred while resetting the password.', 'error')
    
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
@rate_limit(max_requests=5, window_seconds=300)
def toggle_user_status(user_id):
    """Toggle user active status with enhanced security."""
    user = User.query.get_or_404(user_id)
    
    # Prevent self-deactivation
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'error')
        return redirect(url_for('admin.manage_users'))
    
    try:
        # Toggle the status
        user.is_active = not user.is_active
        user.save()
        
        status = 'activated' if user.is_active else 'deactivated'
        logger.info(f"Admin {current_user.email} {status} user: {user.email}")
        flash(f'User {user.full_name} has been {status} successfully.', 'success')
        
    except Exception as e:
        logger.error(f"Error toggling status for user {user.email}: {e}")
        flash('An error occurred while updating the user status.', 'error')
    
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/companies')
@login_required
@admin_required
@rate_limit(max_requests=20, window_seconds=60)
def manage_companies():
    """Manage companies with enhanced security."""
    try:
        companies = CompanyManager.get_all_companies()
        return render_template('admin/manage_companies.html', companies=companies)
        
    except Exception as e:
        logger.error(f"Error loading companies: {e}")
        flash('An error occurred while loading companies.', 'error')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/contacts')
@login_required
@admin_required
@rate_limit(max_requests=20, window_seconds=60)
def manage_contacts():
    """Manage contacts with enhanced security."""
    try:
        contacts = ContactManager.get_all_contacts()
        return render_template('admin/manage_contacts.html', contacts=contacts)
        
    except Exception as e:
        logger.error(f"Error loading contacts: {e}")
        flash('An error occurred while loading contacts.', 'error')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/deal-owners')
@login_required
@admin_required
@rate_limit(max_requests=20, window_seconds=60)
def manage_deal_owners():
    """Manage deal owners with enhanced security."""
    try:
        deal_owners = DealOwnerManager.get_all_deal_owners()
        return render_template('admin/manage_deal_owners.html', deal_owners=deal_owners)
        
    except Exception as e:
        logger.error(f"Error loading deal owners: {e}")
        flash('An error occurred while loading deal owners.', 'error')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/system-info')
@login_required
@admin_required
@rate_limit(max_requests=10, window_seconds=300)
def system_info():
    """Display system information with security logging."""
    try:
        from app import db
        from sqlalchemy import text
        
        # Get database information
        result = db.session.execute(text("SELECT version()"))
        db_version = result.scalar()
        
        # Get table information
        result = db.session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        tables = [row[0] for row in result.fetchall()]
        
        system_info = {
            'database_version': db_version,
            'tables': tables,
            'total_users': User.query.count(),
            'active_users': User.query.filter_by(is_active=True).count(),
        }
        
        logger.info(f"Admin {current_user.email} accessed system information")
        return render_template('admin/system_info.html', system_info=system_info)
        
    except Exception as e:
        logger.error(f"Error loading system info: {e}")
        flash('An error occurred while loading system information.', 'error')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/<item_type>/add', methods=['GET', 'POST'])
@login_required
@admin_required
@rate_limit(max_requests=10, window_seconds=300)
def add_item(item_type):
    """Add new item of specified type."""
    if item_type not in MANAGEMENT_ITEMS:
        flash(f'Invalid item type: {item_type}', 'error')
        return redirect(url_for('admin.dashboard'))
    
    config = MANAGEMENT_ITEMS[item_type]
    form_class = config['form']
    model_class = config['model']
    form = form_class()
    
    if form.validate_on_submit():
        try:
            new_item = model_class()
            form.populate_obj(new_item)
            new_item.save()
            
            logger.info(f"Admin {current_user.email} created new {item_type}: {new_item}")
            flash(f'{config["display_name"].rstrip("s")} added successfully!', 'success')
            return redirect(url_for('admin.manage_items', item_type=item_type))
            
        except Exception as e:
            logger.error(f"Error creating {item_type}: {e}")
            flash(f'Error adding {config["display_name"].rstrip("s")}.', 'error')
    
    return render_template('admin/create_generic.html', form=form, item_type=item_type, config=config)

@admin_bp.route('/<item_type>/manage')
@login_required
@admin_required
@rate_limit(max_requests=20, window_seconds=60)
def manage_items(item_type):
    """Manage items of specified type."""
    if item_type not in MANAGEMENT_ITEMS:
        flash(f'Invalid item type: {item_type}', 'error')
        return redirect(url_for('admin.dashboard'))
    
    config = MANAGEMENT_ITEMS[item_type]
    model_class = config['model']
    
    page = request.args.get('page', 1, type=int)
    pagination = model_class.query.paginate(page=page, per_page=10, error_out=False)
    items = pagination.items
    
    # Special template for BOM management with component references
    if item_type == 'pump-bom':
        # Load all component types for reference
        inertia_bases = InertiaBase.query.filter_by(is_active=True).order_by(InertiaBase.part_number).all()
        seismic_springs = SeismicSpring.query.filter_by(is_active=True).order_by(SeismicSpring.part_number).all()
        rubber_mounts = RubberMount.query.filter_by(is_active=True).order_by(RubberMount.sku).all()
        crossbars = Crossbar.query.filter_by(is_active=True).order_by(Crossbar.sku).all()
        
        # Aggregate BOM data by pump (one row per pump)
        pump_bom_data = []
        pumps_with_bom = Pump.query.join(PumpBOM).distinct().order_by(Pump.part_number).all()
        
        for pump in pumps_with_bom:
            pump_data = {
                'pump_id': pump.id,
                'pump_part': pump.part_number,
                'pump_name': pump.name,
                'series_code': pump.series.series_code if pump.series else '',
                'inertia_pn': None,
                'inertia_size': None,
                'spring_pn': None,
                'spring_qty': None
            }
            
            # Get BOM items for this pump
            for bom_item in pump.bom_items:
                if bom_item.component_type == 'inertia_base':
                    base = InertiaBase.query.get(bom_item.component_id)
                    if base:
                        pump_data['inertia_pn'] = base.part_number
                        if base.length_mm and base.width_mm and base.depth_mm:
                            pump_data['inertia_size'] = f"{base.length_mm} x {base.width_mm} x {base.depth_mm}"
                
                elif bom_item.component_type == 'seismic_spring':
                    spring = SeismicSpring.query.get(bom_item.component_id)
                    if spring:
                        pump_data['spring_pn'] = spring.part_number
                        pump_data['spring_qty'] = bom_item.quantity
            
            pump_bom_data.append(pump_data)
        
        return render_template('admin/manage_pump_bom.html',
                             items=items,
                             item_type=item_type,
                             config=config,
                             pagination=pagination,
                             pump_bom_data=pump_bom_data,
                             inertia_bases=inertia_bases,
                             seismic_springs=seismic_springs,
                             rubber_mounts=rubber_mounts,
                             crossbars=crossbars)
    
    return render_template('admin/manage_base.html', 
                         items=items, 
                         item_type=item_type, 
                         config=config,
                         pagination=pagination)

@admin_bp.route('/<item_type>/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
@rate_limit(max_requests=15, window_seconds=300)
def edit_item(item_type, item_id):
    """Edit item of specified type."""
    if item_type not in MANAGEMENT_ITEMS:
        flash(f'Invalid item type: {item_type}', 'error')
        return redirect(url_for('admin.dashboard'))
    
    config = MANAGEMENT_ITEMS[item_type]
    model_class = config['model']
    form_class = config['form']
    
    item = model_class.query.get_or_404(item_id)
    form = form_class(obj=item)
    
    if form.validate_on_submit():
        try:
            form.populate_obj(item)
            item.save()
            
            logger.info(f"Admin {current_user.email} updated {item_type}: {item}")
            flash(f'{config["display_name"].rstrip("s")} updated successfully!', 'success')
            return redirect(url_for('admin.manage_items', item_type=item_type))
            
        except Exception as e:
            logger.error(f"Error updating {item_type}: {e}")
            flash(f'Error updating {config["display_name"].rstrip("s")}.', 'error')
    
    return render_template('admin/create_generic.html', form=form, item_type=item_type, config=config, item=item)

@admin_bp.route('/<item_type>/<int:item_id>/delete', methods=['POST'])
@login_required
@admin_required
@rate_limit(max_requests=5, window_seconds=300)
def delete_item(item_type, item_id):
    """Delete item of specified type."""
    if item_type not in MANAGEMENT_ITEMS:
        flash(f'Invalid item type: {item_type}', 'error')
        return redirect(url_for('admin.dashboard'))
    
    config = MANAGEMENT_ITEMS[item_type]
    model_class = config['model']
    
    item = model_class.query.get_or_404(item_id)
    
    try:
        item_name = str(item)
        item.delete()
        
        logger.info(f"Admin {current_user.email} deleted {item_type}: {item_name}")
        flash(f'{config["display_name"].rstrip("s")} deleted successfully!', 'success')
        
    except Exception as e:
        logger.error(f"Error deleting {item_type}: {e}")
        flash(f'Error deleting {config["display_name"].rstrip("s")}.', 'error')
    
    return redirect(url_for('admin.manage_items', item_type=item_type))

@admin_bp.route('/bom/export')
@login_required
@admin_required
@rate_limit(max_requests=10, window_seconds=60)
def export_bom():
    """Export BOM data to CSV"""
    try:
        from flask import make_response
        from datetime import datetime
        
        csv_data = export_bom_to_csv()
        
        response = make_response(csv_data)
        response.headers['Content-Type'] = 'text/csv'
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response.headers['Content-Disposition'] = f'attachment; filename=pump_bom_export_{timestamp}.csv'
        
        logger.info(f"Admin {current_user.email} exported BOM data")
        return response
        
    except Exception as e:
        logger.error(f"Error exporting BOM: {e}", exc_info=True)
        flash('An error occurred while exporting BOM data.', 'error')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/bom/export-sample')
@login_required
@admin_required
@rate_limit(max_requests=10, window_seconds=60)
def export_bom_sample():
    """Export sample BOM CSV template"""
    try:
        from flask import make_response
        
        csv_data = generate_sample_csv()
        
        response = make_response(csv_data)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=pump_bom_sample_template.csv'
        
        logger.info(f"Admin {current_user.email} downloaded BOM sample template")
        return response
        
    except Exception as e:
        logger.error(f"Error generating sample BOM: {e}", exc_info=True)
        flash('An error occurred while generating sample template.', 'error')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/bom/import', methods=['GET', 'POST'])
@login_required
@admin_required
@rate_limit(max_requests=5, window_seconds=300)
def import_bom():
    """Import BOM data from CSV"""
    form = BOMImportForm()
    
    if form.validate_on_submit():
        try:
            # Read file content
            file = form.file.data
            file_content = file.read().decode('utf-8')
            
            # Process import
            successful, failed, errors = import_bom_from_csv(
                file_content,
                overwrite_existing=form.overwrite_existing.data,
                create_missing_components=form.create_missing_components.data
            )
            
            # Show results
            if successful > 0:
                flash(f'Successfully imported {successful} pump(s) with BOM data!', 'success')
            
            if failed > 0:
                flash(f'Failed to import {failed} pump(s). See errors below.', 'warning')
            
            if errors:
                for error in errors[:10]:  # Show first 10 errors
                    flash(error, 'error')
                if len(errors) > 10:
                    flash(f'... and {len(errors) - 10} more errors', 'error')
            
            logger.info(f"Admin {current_user.email} imported BOM data: {successful} successful, {failed} failed")
            
            if successful > 0:
                return redirect(url_for('admin.manage_items', item_type='pump-bom'))
                
        except Exception as e:
            logger.error(f"Error importing BOM: {e}", exc_info=True)
            flash(f'An error occurred while importing: {str(e)}', 'error')
    
    return render_template('admin/import_bom.html', form=form)


@admin_bp.route('/seismic-springs/export')
@login_required
@admin_required
@rate_limit(max_requests=10, window_seconds=60)
def export_seismic_springs():
    """Export seismic spring data to CSV"""
    try:
        from flask import make_response
        from datetime import datetime
        
        csv_data = export_seismic_springs_to_csv()
        
        response = make_response(csv_data)
        response.headers['Content-Type'] = 'text/csv'
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response.headers['Content-Disposition'] = f'attachment; filename=seismic_springs_export_{timestamp}.csv'
        
        logger.info(f"Admin {current_user.email} exported seismic spring data")
        return response
        
    except Exception as e:
        logger.error(f"Error exporting seismic springs: {e}", exc_info=True)
        flash('An error occurred while exporting seismic spring data.', 'error')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/seismic-springs/export-sample')
@login_required
@admin_required
@rate_limit(max_requests=10, window_seconds=60)
def export_seismic_springs_sample():
    """Export sample seismic spring CSV template"""
    try:
        from flask import make_response
        
        csv_data = generate_seismic_spring_sample_csv()
        
        response = make_response(csv_data)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=seismic_springs_sample_template.csv'
        
        logger.info(f"Admin {current_user.email} downloaded seismic spring sample template")
        return response
        
    except Exception as e:
        logger.error(f"Error generating seismic spring sample: {e}", exc_info=True)
        flash('An error occurred while generating sample template.', 'error')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/seismic-springs/import', methods=['GET', 'POST'])
@login_required
@admin_required
@rate_limit(max_requests=5, window_seconds=300)
def import_seismic_springs():
    """Import seismic spring data from CSV"""
    form = SeismicSpringImportForm()
    
    if form.validate_on_submit():
        try:
            # Read file content
            file = form.file.data
            file_content = file.read().decode('utf-8')
            
            # Process import
            successful, failed, errors = import_seismic_springs_from_csv(
                file_content,
                overwrite_existing=form.overwrite_existing.data,
                update_existing=form.update_existing.data
            )
            
            # Show results
            if successful > 0:
                flash(f'Successfully imported {successful} seismic spring(s)!', 'success')
            
            if failed > 0:
                flash(f'Failed to import {failed} seismic spring(s). See errors below.', 'warning')
            
            if errors:
                for error in errors[:10]:  # Show first 10 errors
                    flash(error, 'error')
                if len(errors) > 10:
                    flash(f'... and {len(errors) - 10} more errors', 'error')
            
            logger.info(f"Admin {current_user.email} imported seismic spring data: {successful} successful, {failed} failed")
            
            if successful > 0:
                return redirect(url_for('admin.manage_items', item_type='seismic-spring'))
                
        except Exception as e:
            logger.error(f"Error importing seismic springs: {e}", exc_info=True)
            flash(f'An error occurred while importing: {str(e)}', 'error')
    
    return render_template('admin/import_seismic_springs.html', form=form)


# ============================================================================
# BULK COMPONENT IMPORT/EXPORT ROUTES
# ============================================================================

# Mapping of component types to their import/export functions
COMPONENT_TYPES = {
    'pump-series': {
        'display_name': 'Pump Series',
        'export_func': export_pump_series_to_csv,
        'import_func': import_pump_series_from_csv,
        'filename': 'pump_series'
    },
    'pump': {
        'display_name': 'Pumps',
        'export_func': export_pumps_to_csv,
        'import_func': import_pumps_from_csv,
        'filename': 'pumps'
    },
    'inertia-base': {
        'display_name': 'Inertia Bases',
        'export_func': export_inertia_bases_to_csv,
        'import_func': import_inertia_bases_from_csv,
        'filename': 'inertia_bases'
    },
    'rubber-mount': {
        'display_name': 'Rubber Mounts',
        'export_func': export_rubber_mounts_to_csv,
        'import_func': import_rubber_mounts_from_csv,
        'filename': 'rubber_mounts'
    },
    'crossbar': {
        'display_name': 'Crossbars',
        'export_func': export_crossbars_to_csv,
        'import_func': import_crossbars_from_csv,
        'filename': 'crossbars'
    },
    'motor-protection': {
        'display_name': 'Motor Protection',
        'export_func': export_motor_protection_to_csv,
        'import_func': import_motor_protection_from_csv,
        'filename': 'motor_protection'
    },
    'drip-trip-tray': {
        'display_name': 'Drip Trip Trays',
        'export_func': export_drip_trays_to_csv,
        'import_func': import_drip_trays_from_csv,
        'filename': 'drip_trays'
    },
    'duty-point': {
        'display_name': 'Duty Points',
        'export_func': export_duty_points_to_csv,
        'import_func': import_duty_points_from_csv,
        'filename': 'duty_points'
    },
    'pump-component': {
        'display_name': 'Generic Components',
        'export_func': export_generic_components_to_csv,
        'import_func': import_generic_components_from_csv,
        'filename': 'generic_components'
    }
}


@admin_bp.route('/bulk-data-manager')
@login_required
@admin_required
@rate_limit(max_requests=20, window_seconds=60)
def bulk_data_manager():
    """Central hub for bulk data import/export operations"""
    return render_template('admin/bulk_data_manager.html', component_types=COMPONENT_TYPES)


@admin_bp.route('/<item_type>/export-csv')
@login_required
@admin_required
@rate_limit(max_requests=10, window_seconds=60)
def export_component_csv(item_type):
    """Generic export route for component types"""
    if item_type not in COMPONENT_TYPES:
        flash(f'Invalid component type: {item_type}', 'error')
        return redirect(url_for('admin.bulk_data_manager'))
    
    config = COMPONENT_TYPES[item_type]
    
    try:
        from flask import make_response
        from datetime import datetime
        
        csv_data = config['export_func']()
        
        response = make_response(csv_data)
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response.headers['Content-Disposition'] = f'attachment; filename={config["filename"]}_export_{timestamp}.csv'
        
        logger.info(f"Admin {current_user.email} exported {config['display_name']} data")
        return response
        
    except Exception as e:
        logger.error(f"Error exporting {item_type}: {e}", exc_info=True)
        flash(f'An error occurred while exporting {config["display_name"]} data.', 'error')
        return redirect(url_for('admin.bulk_data_manager'))


@admin_bp.route('/<item_type>/import-csv', methods=['GET', 'POST'])
@login_required
@admin_required
@rate_limit(max_requests=5, window_seconds=300)
def import_component_csv(item_type):
    """Generic import route for component types"""
    if item_type not in COMPONENT_TYPES:
        flash(f'Invalid component type: {item_type}', 'error')
        return redirect(url_for('admin.bulk_data_manager'))
    
    config = COMPONENT_TYPES[item_type]
    form = BulkComponentImportForm()
    
    if form.validate_on_submit():
        try:
            # Read file content
            file = form.file.data
            file_content = file.read().decode('utf-8')
            
            # Process import
            successful, failed, errors = config['import_func'](
                file_content,
                update_existing=form.update_existing.data
            )
            
            # Show results
            if successful > 0:
                flash(f'Successfully imported {successful} {config["display_name"]}!', 'success')
            
            if failed > 0:
                flash(f'Failed to import {failed} items. See errors below.', 'warning')
            
            if errors:
                for error in errors[:10]:  # Show first 10 errors
                    flash(error, 'error')
                if len(errors) > 10:
                    flash(f'... and {len(errors) - 10} more errors', 'error')
            
            logger.info(f"Admin {current_user.email} imported {config['display_name']}: {successful} successful, {failed} failed")
            
            if successful > 0:
                return redirect(url_for('admin.manage_items', item_type=item_type))
                
        except Exception as e:
            logger.error(f"Error importing {item_type}: {e}", exc_info=True)
            flash(f'An error occurred while importing: {str(e)}', 'error')
    
    return render_template('admin/bulk_import_generic.html', 
                         form=form, 
                         item_type=item_type, 
                         config=config)
