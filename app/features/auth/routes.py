from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from datetime import datetime
from app.features.auth import auth_bp
from app.features.auth.forms import (LoginForm, ChangePasswordForm, ForcePasswordChangeForm, 
                                     RegistrationForm, TwoFactorSetupForm, TwoFactorVerifyForm, 
                                     TwoFactorDisableForm, BackupCodeForm)
from app.models import User, UserRole
from app.core.core_security import security_manager, admin_required
from app.core.core_logging import logger
from app.core.core_rate_limiting import auth_rate_limit, sensitive_rate_limit, security_rate_limit
from app.core.core_metrics import record_login_attempt, record_2fa_attempt

@auth_bp.route('/login', methods=['GET', 'POST'])
@auth_rate_limit()
def login():
    """Handle user login with enhanced security."""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Enhanced rate limiting for login attempts
        if security_manager.check_login_rate_limit(request.remote_addr):
            flash('Too many login attempts. Please try again later.', 'error')
            return render_template('auth/login.html', form=form)
        
        # Sanitize input
        email = security_manager.sanitize_input(form.email.data)
        password = form.password.data
        
        user = User.query.filter_by(email=email).first()
        if user is None or not user.verify_password(password):
            # Track failed login attempt
            security_manager._track_failed_login(request.remote_addr)
            record_login_attempt('failed', 'standard')
            flash('Invalid email or password', 'error')
            return render_template('auth/login.html', form=form)
        
        if not user.is_active:
            flash('Account is disabled. Please contact administrator.', 'error')
            return render_template('auth/login.html', form=form)
        
        # Successful login
        login_user(user, remember=form.remember_me.data)
        user.last_login = datetime.utcnow()
        user.save()
        
        # Record successful login metrics
        user_type = 'admin' if user.has_role('admin') else 'standard'
        record_login_attempt('success', user_type)
        
        logger.info(f"User {user.email} logged in successfully from IP {request.remote_addr}")
        
        # Check if user needs to change password
        if user.needs_password_change():
            flash('Please change your password before continuing.', 'warning')
            return redirect(url_for('auth.force_password_change'))
        
        # Redirect to next page or home
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.home')
        return redirect(next_page)
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout with security logging."""
    user_email = current_user.email
    logout_user()
    logger.info(f"User {user_email} logged out from IP {request.remote_addr}")
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
@login_required
@admin_required
@sensitive_rate_limit("2/hour")
def register():
    """Handle user registration (admin only)."""
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            # Check if user already exists
            if User.query.filter_by(email=form.email.data).first():
                flash('A user with this email already exists.', 'error')
                return render_template('auth/register.html', form=form)
            
            if User.query.filter_by(username=form.username.data).first():
                flash('A user with this username already exists.', 'error')
                return render_template('auth/register.html', form=form)
            
            # Create new user with temporary password
            user = User(
                username=form.username.data,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
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
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/force-password-change', methods=['GET', 'POST'])
@login_required
def force_password_change():
    """Handle forced password change for temporary passwords."""
    if not current_user.needs_password_change():
        return redirect(url_for('main.home'))
    
    form = ForcePasswordChangeForm()
    if form.validate_on_submit():
        try:
            # Validate new password strength
            new_password = form.new_password.data
            if len(new_password) < 8:
                flash('Password must be at least 8 characters long.', 'error')
                return render_template('auth/force_password_change.html', form=form)
            
            # Check for common weak passwords
            weak_passwords = ['password', '123456', 'admin', 'user', 'test']
            if new_password.lower() in weak_passwords:
                flash('Please choose a stronger password.', 'error')
                return render_template('auth/force_password_change.html', form=form)
            
            current_user.password = new_password
            current_user.force_password_change = False
            current_user.save()
            
            logger.info(f"User {current_user.email} changed temporary password")
            flash('Your password has been changed successfully. You can now use the application.', 'success')
            return redirect(url_for('main.home'))
            
        except Exception as e:
            logger.error(f"Error changing password: {e}")
            flash('An error occurred while changing your password.', 'error')
    
    return render_template('auth/force_password_change.html', form=form)

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Handle password change for current user with enhanced validation."""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.verify_password(form.current_password.data):
            flash('Current password is incorrect.', 'error')
            return render_template('auth/change_password.html', form=form)
        
        # Validate new password strength
        new_password = form.new_password.data
        if len(new_password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return render_template('auth/change_password.html', form=form)
        
        # Check for common weak passwords
        weak_passwords = ['password', '123456', 'admin', 'user', 'test']
        if new_password.lower() in weak_passwords:
            flash('Please choose a stronger password.', 'error')
            return render_template('auth/change_password.html', form=form)
        
        # Check if new password is same as current
        if current_user.verify_password(new_password):
            flash('New password must be different from current password.', 'error')
            return render_template('auth/change_password.html', form=form)
        
        try:
            current_user.password = new_password
            current_user.save()
            
            logger.info(f"User {current_user.email} changed password")
            flash('Your password has been changed successfully.', 'success')
            return redirect(url_for('main.home'))
            
        except Exception as e:
            logger.error(f"Error changing password: {e}")
            flash('An error occurred while changing your password.', 'error')
    
    return render_template('auth/change_password.html', form=form)

@auth_bp.route('/profile')
@login_required
def profile():
    """Display user profile with security information."""
    return render_template('auth/profile.html')

@auth_bp.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    """Handle password reset requests with rate limiting."""
    # Rate limit password reset requests
    if security_manager.check_rate_limit(request.remote_addr, 'password_reset', 3, 3600):
        flash('Too many password reset requests. Please try again later.', 'error')
        return render_template('auth/reset_password_request.html')
    
    # Implementation for password reset request
    flash('Password reset functionality not implemented yet.', 'info')
    return render_template('auth/reset_password_request.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset with token validation."""
    # Implementation for password reset with token
    flash('Password reset functionality not implemented yet.', 'info')
    return render_template('auth/reset_password.html')


# Two-Factor Authentication Routes
@auth_bp.route('/2fa/setup', methods=['GET', 'POST'])
@login_required
@sensitive_rate_limit("2/hour")
def setup_2fa():
    """Set up two-factor authentication for the current user."""
    if current_user.two_factor_enabled:
        flash('Two-factor authentication is already enabled.', 'info')
        return redirect(url_for('auth.profile'))
    
    form = TwoFactorSetupForm()
    
    if form.validate_on_submit():
        # Generate 2FA secret
        secret = current_user.generate_2fa_secret()
        backup_codes = current_user.generate_backup_codes()
        
        # Save to database
        current_user.save()
        
        # Generate QR code URL
        qr_code_url = current_user.get_2fa_qr_code_url()
        
        flash('Two-factor authentication setup initiated. Please scan the QR code and verify with a code.', 'info')
        return render_template('auth/2fa_verify_setup.html', 
                             qr_code_url=qr_code_url, 
                             backup_codes=backup_codes,
                             secret=secret)
    
    return render_template('auth/2fa_setup.html', form=form)


@auth_bp.route('/2fa/verify-setup', methods=['POST'])
@login_required
@auth_rate_limit()
def verify_2fa_setup():
    """Verify 2FA setup with a code."""
    form = TwoFactorVerifyForm()
    
    if form.validate_on_submit():
        if current_user.verify_2fa_code(form.code.data):
            # Enable 2FA
            current_user.enable_2fa()
            current_user.save()
            
            flash('Two-factor authentication has been enabled successfully!', 'success')
            return redirect(url_for('auth.profile'))
        else:
            flash('Invalid authentication code. Please try again.', 'error')
    
    return render_template('auth/2fa_verify_setup.html', form=form)


@auth_bp.route('/2fa/disable', methods=['GET', 'POST'])
@login_required
def disable_2fa():
    """Disable two-factor authentication."""
    if not current_user.two_factor_enabled:
        flash('Two-factor authentication is not enabled.', 'info')
        return redirect(url_for('auth.profile'))
    
    form = TwoFactorDisableForm()
    
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            current_user.disable_2fa()
            current_user.save()
            
            flash('Two-factor authentication has been disabled.', 'success')
            return redirect(url_for('auth.profile'))
        else:
            flash('Invalid password. Please try again.', 'error')
    
    return render_template('auth/2fa_disable.html', form=form)


@auth_bp.route('/2fa/verify', methods=['GET', 'POST'])
def verify_2fa():
    """Verify 2FA code during login."""
    # This would be called after successful password verification
    # Implementation depends on your login flow
    form = TwoFactorVerifyForm()
    
    if form.validate_on_submit():
        # Verify the code (this would be called with the user context)
        # Implementation depends on your session management
        pass
    
    return render_template('auth/2fa_verify.html', form=form) 