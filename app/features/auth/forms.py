from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User, UserRole

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
    role = SelectField('Role', choices=[
        (UserRole.SALES.value, 'Sales'),
        (UserRole.MANAGER.value, 'Manager'),
        (UserRole.ADMIN.value, 'Admin'),
        (UserRole.VIEWER.value, 'Viewer')
    ], validators=[DataRequired(message='Role is required')])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register User')

    def validate_email(self, field):
        """Check if email is already registered."""
        user = User.query.filter_by(email=field.data).first()
        if user:
            raise ValidationError('Email address is already registered.')

    def validate_username(self, field):
        """Check if username is already taken."""
        user = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError('Username is already taken.')

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