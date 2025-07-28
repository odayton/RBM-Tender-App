from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from urllib.parse import urlparse
from app.core.core_security import security_manager
from app.core.core_security import SecurityManager
from app.core.core_logging import logger
from app.models import User, UserRole
from . import auth_bp
from .forms import (
    LoginForm, RegistrationForm, ChangePasswordForm, 
    ResetPasswordRequestForm, ResetPasswordForm
)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Check rate limiting
        if security_manager.check_rate_limit(request.remote_addr):
            flash('Too many login attempts. Please try again later.', 'error')
            return render_template('auth/login.html', form=form)
        
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.verify_password(form.password.data):
            # Track failed login attempt
            security_manager._track_failed_login(request.remote_addr)
            flash('Invalid email or password', 'error')
            return render_template('auth/login.html', form=form)
        
        if not user.is_active:
            flash('Account is disabled. Please contact administrator.', 'error')
            return render_template('auth/login.html', form=form)
        
        # Successful login
        login_user(user, remember=form.remember_me.data)
        user.last_login = datetime.utcnow()
        user.save()
        
        logger.info(f"User {user.email} logged in successfully")
        
        # Redirect to next page or home
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.home')
        return redirect(next_page)
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logger.info(f"User {current_user.email} logged out")
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
@login_required
@SecurityManager.roles_required('Admin')
def register():
    """Handle user registration (admin only)."""
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User(
                username=form.username.data,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                phone_number=form.phone_number.data,
                role=UserRole(form.role.data),
                is_active=True
            )
            user.password = form.password.data
            user.save()
            
            logger.info(f"Admin {current_user.email} created new user: {user.email}")
            flash(f'User {user.email} has been registered successfully.', 'success')
            return redirect(url_for('admin.dashboard'))
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            flash('An error occurred while creating the user.', 'error')
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Handle password change for current user."""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.verify_password(form.current_password.data):
            flash('Current password is incorrect.', 'error')
            return render_template('auth/change_password.html', form=form)
        
        try:
            current_user.password = form.new_password.data
            current_user.save()
            
            logger.info(f"User {current_user.email} changed password")
            flash('Your password has been changed successfully.', 'success')
            return redirect(url_for('main.home'))
            
        except Exception as e:
            logger.error(f"Error changing password: {e}")
            flash('An error occurred while changing your password.', 'error')
    
    return render_template('auth/change_password.html', form=form)

@auth_bp.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    """Handle password reset request."""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # In a real application, you would send an email here
            # For now, we'll just show a message
            flash('If an account with that email exists, you will receive password reset instructions.', 'info')
        else:
            # Don't reveal if email exists or not for security
            flash('If an account with that email exists, you will receive password reset instructions.', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_request.html', form=form)

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset with token."""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    # In a real application, you would verify the token here
    # For now, we'll just show the form
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # In a real application, you would find the user by token and update password
        flash('Your password has been reset successfully.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form)

@auth_bp.route('/profile')
@login_required
def profile():
    """Display user profile."""
    return render_template('auth/profile.html', user=current_user) 