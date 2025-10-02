from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User, UserRole
import pyotp

class LoginForm(FlaskForm):
    """Form for user login."""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    """Form for user registration (admin only)."""
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=50, message='Username must be between 3 and 50 characters')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])
    first_name = StringField('First Name', validators=[
        DataRequired(message='First name is required'),
        Length(max=50, message='First name must be less than 50 characters')
    ])
    last_name = StringField('Last Name', validators=[
        DataRequired(message='Last name is required'),
        Length(max=50, message='Last name must be less than 50 characters')
    ])
    phone_number = StringField('Phone Number', validators=[
        Length(max=20, message='Phone number must be less than 20 characters')
    ])
    role = SelectField('Role', validators=[DataRequired(message='Role is required')])
    submit = SubmitField('Create User')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        try:
            from flask import current_app
            if not current_app:
                return  # Skip population if no app context
            
            # Set role choices
            self.role.choices = [
                (UserRole.SALES.value, 'Sales'),
                (UserRole.MANAGER.value, 'Manager'),
                (UserRole.ADMIN.value, 'Admin'),
                (UserRole.VIEWER.value, 'Viewer')
            ]
        except RuntimeError:
            # Skip population if we're outside application context
            pass

    def validate_email(self, field):
        """Check if email is already registered."""
        try:
            from flask import current_app
            if not current_app:
                return  # Skip validation if no app context
            
            user = User.query.filter_by(email=field.data).first()
            if user:
                raise ValidationError('Email address is already registered.')
        except RuntimeError:
            # Skip validation if we're outside application context
            pass

    def validate_username(self, field):
        """Check if username is already taken."""
        try:
            from flask import current_app
            if not current_app:
                return  # Skip validation if no app context
            
            user = User.query.filter_by(username=field.data).first()
            if user:
                raise ValidationError('Username is already taken.')
        except RuntimeError:
            # Skip validation if we're outside application context
            pass

class ChangePasswordForm(FlaskForm):
    """Form for changing user password."""
    current_password = PasswordField('Current Password', validators=[
        DataRequired(message='Current password is required')
    ])
    new_password = PasswordField('New Password', validators=[
        DataRequired(message='New password is required'),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message='Please confirm your new password'),
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Change Password')

class ForcePasswordChangeForm(FlaskForm):
    """Form for forced password change (no current password required)."""
    new_password = PasswordField('New Password', validators=[
        DataRequired(message='New password is required'),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message='Please confirm your new password'),
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Set New Password')

class ResetPasswordRequestForm(FlaskForm):
    """Form for requesting password reset."""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    """Form for resetting password with token."""
    password = PasswordField('New Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')

class EditProfileForm(FlaskForm):
    """Form for users to edit their own profile."""
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=50, message='Username must be between 3 and 50 characters')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])
    first_name = StringField('First Name', validators=[
        DataRequired(message='First name is required'),
        Length(max=50, message='First name must be less than 50 characters')
    ])
    last_name = StringField('Last Name', validators=[
        DataRequired(message='Last name is required'),
        Length(max=50, message='Last name must be less than 50 characters')
    ])
    phone_number = StringField('Phone Number', validators=[
        Length(max=20, message='Phone number must be less than 20 characters')
    ])
    submit = SubmitField('Update Profile')

    def __init__(self, current_user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_user = current_user

    def validate_email(self, field):
        """Check if email is already registered by another user."""
        try:
            from flask import current_app
            if not current_app:
                return  # Skip validation if no app context
            
            user = User.query.filter_by(email=field.data).first()
            if user and user.id != self.current_user.id:
                raise ValidationError('Email address is already registered by another user.')
        except RuntimeError:
            # Skip validation if we're outside application context
            pass

    def validate_username(self, field):
        """Check if username is already taken by another user."""
        try:
            from flask import current_app
            if not current_app:
                return  # Skip validation if no app context
            
            user = User.query.filter_by(username=field.data).first()
            if user and user.id != self.current_user.id:
                raise ValidationError('Username is already taken by another user.')
        except RuntimeError:
            # Skip validation if we're outside application context
            pass


class TwoFactorSetupForm(FlaskForm):
    """Form for setting up 2FA."""
    submit = SubmitField('Enable Two-Factor Authentication')


class TwoFactorVerifyForm(FlaskForm):
    """Form for verifying 2FA code."""
    code = StringField('Authentication Code', validators=[
        DataRequired(message='Authentication code is required'),
        Length(min=6, max=6, message='Code must be 6 digits')
    ])
    submit = SubmitField('Verify Code')
    
    def validate_code(self, field):
        """Validate the 2FA code format."""
        if not field.data.isdigit():
            raise ValidationError('Code must contain only numbers.')
        if len(field.data) != 6:
            raise ValidationError('Code must be exactly 6 digits.')


class TwoFactorDisableForm(FlaskForm):
    """Form for disabling 2FA."""
    password = PasswordField('Current Password', validators=[
        DataRequired(message='Password is required to disable 2FA')
    ])
    submit = SubmitField('Disable Two-Factor Authentication')


class BackupCodeForm(FlaskForm):
    """Form for using backup codes."""
    backup_code = StringField('Backup Code', validators=[
        DataRequired(message='Backup code is required'),
        Length(min=8, max=8, message='Backup code must be 8 characters')
    ])
    submit = SubmitField('Use Backup Code') 