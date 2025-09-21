from flask import (
    render_template, 
    request, 
    redirect, 
    url_for, 
    flash
)
from flask_login import login_required
from app.core.core_security import admin_required, security_manager
from app.core.core_logging import logger

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
# Removed duplicate creation routes - they're now defined in the main routes file

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