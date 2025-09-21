from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.features.admin import admin_bp
from app.core.core_security import admin_required, rate_limit, security_manager
from app.core.core_rate_limiting import admin_rate_limit, security_rate_limit
from app.core.core_logging import logger
from app.models import User, UserRole, Company, Contact
from app.features.admin.forms import CreateUserForm, EditUserForm, CompanyForm, ContactForm
from app.utils.db_utils.organization.db_companies import CompanyManager
from app.utils.db_utils.organization.db_contacts import ContactManager
from app.utils.db_utils.organization.db_deal_owners import DealOwnerManager

# Import helpers to register additional routes
from . import helpers

# Management items configuration
MANAGEMENT_ITEMS = {
    'company': {
        'display_name': 'Companies',
        'model': Company,
        'form': CompanyForm,
        'columns': ['company_name', 'phone_number', 'domain']
    },
    'contact': {
        'display_name': 'Contacts',
        'model': Contact,
        'form': ContactForm,
        'columns': ['name', 'email', 'phone_number', 'position']
    }
}

# Import additional models and forms for specific routes
from app.models import User, UserRole, Company, Contact
from app.features.admin.forms import CompanyForm, ContactForm, DealOwnerForm
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