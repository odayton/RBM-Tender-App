from app.core.core_forms import FlaskForm
# Add FileRequired to this import statement
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import (
    StringField,
    TextAreaField,
    DecimalField,
    SelectField,
    IntegerField,
    SubmitField,
    BooleanField,
    DateTimeField
)
from wtforms.validators import DataRequired, Optional, NumberRange, Email
from app.models import Company, User, UserRole


class CreateUserForm(FlaskForm):
    """Form for creating new users"""
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[Optional()])
    role = SelectField('Role', choices=[
        ('Admin', 'Admin'),
        ('Sales', 'Sales'),
        ('Manager', 'Manager'),
        ('Viewer', 'Viewer')
    ], validators=[DataRequired()])
    submit = SubmitField('Create User')


class EditUserForm(FlaskForm):
    """Form for editing existing users"""
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[Optional()])
    role = SelectField('Role', choices=[
        ('Admin', 'Admin'),
        ('Sales', 'Sales'),
        ('Manager', 'Manager'),
        ('Viewer', 'Viewer')
    ], validators=[DataRequired()])
    is_active = BooleanField('Active')
    submit = SubmitField('Update User')




class BOMUploadForm(FlaskForm):
    """Form for uploading BOM data"""
    file = FileField('Excel File', validators=[
        FileRequired(),
        FileAllowed(['xlsx', 'xls'], 'Excel files only!')
    ])
    pump_series = SelectField('Pump Series', choices=[('NBG', 'NBG Series'), ('CR', 'CR Series'), ('TP', 'TP Series'), ('CM', 'CM Series')], validators=[DataRequired()])

class AdditionalPriceAdderForm(FlaskForm):
    """Form for managing additional price adders"""
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0)])

class ContactForm(FlaskForm):
    """Form for creating and editing contacts"""
    name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number', validators=[Optional()])
    mobile_number = StringField('Mobile Number', validators=[Optional()])
    position = StringField('Position/Title', validators=[Optional()])
    company_id = SelectField('Company', coerce=lambda x: int(x) if x and x != '' else None, validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save Contact')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        try:
            from flask import current_app
            if not current_app:
                return  # Skip population if no app context
            
            # Populate company choices
            companies = Company.query.order_by(Company.company_name).all()
            self.company_id.choices = [('', 'Select Company')] + [(str(c.id), c.company_name) for c in companies]
        except RuntimeError:
            # Skip population if we're outside application context
            pass

class DealOwnerForm(FlaskForm):
    """A simple form to create a new Deal Owner (User) for development."""
    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number', validators=[Optional()])
    submit = SubmitField('Create Deal Owner')

class CompanyForm(FlaskForm):
    """Form for creating a new Company"""
    company_name = StringField('Company Name', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[Optional()])
    domain = StringField('Email Domain', validators=[Optional()], 
                        description='e.g., example.com - contacts with this domain will be auto-assigned')
    submit = SubmitField('Create Company')

class DiscountForm(FlaskForm):
    """Form for creating and editing discounts"""
    code = StringField('Discount Code', validators=[DataRequired()], 
                      description='Unique code for the discount (e.g., "P1", "H1")')
    percentage = DecimalField('Discount Percentage', validators=[DataRequired(), NumberRange(min=0, max=100)], 
                            description='Percentage discount (0-100)')
    is_active = BooleanField('Active', default=True, 
                           description='Whether this discount is currently active')
    submit = SubmitField('Save Discount')


# ==================== HVAC/Pump Management Forms ====================

class PumpSeriesForm(FlaskForm):
    """Form for creating and editing pump series"""
    series_code = StringField('Series Code', validators=[DataRequired()], 
                            description='Unique code (e.g., "NBG", "CR", "MAGNA")')
    series_name = StringField('Series Name', validators=[DataRequired()],
                            description='Full series name')
    description = TextAreaField('Description', validators=[Optional()])
    curve_url_pattern = StringField('Curve URL Pattern', validators=[Optional()],
                                   description='Pattern for pump curve URLs')
    series_path = StringField('Series Path', validators=[Optional()],
                            description='Path segment for Grundfos URLs')
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Series')


class PumpForm(FlaskForm):
    """Form for creating and editing pumps"""
    part_number = StringField('Part Number', validators=[DataRequired()],
                            description='Manufacturer part number')
    name = StringField('Pump Name', validators=[DataRequired()],
                     description='Pump description/name')
    series_id = SelectField('Pump Series', coerce=lambda x: int(x) if x and x != '' else None, 
                          validators=[Optional()])
    item_number = StringField('Item Number', validators=[Optional()])
    description = TextAreaField('Description', validators=[Optional()])
    kw_rating = DecimalField('KW Rating', validators=[Optional(), NumberRange(min=0)])
    poles = IntegerField('Poles', validators=[Optional(), NumberRange(min=1)])
    min_flow_rate_lps = DecimalField('Min Flow Rate (L/s)', validators=[Optional(), NumberRange(min=0)])
    max_flow_rate_lps = DecimalField('Max Flow Rate (L/s)', validators=[Optional(), NumberRange(min=0)])
    optimal_flow_rate_lps = DecimalField('Optimal Flow Rate (L/s)', validators=[Optional(), NumberRange(min=0)])
    min_head_pressure_kpa = DecimalField('Min Head Pressure (kPa)', validators=[Optional(), NumberRange(min=0)])
    max_head_pressure_kpa = DecimalField('Max Head Pressure (kPa)', validators=[Optional(), NumberRange(min=0)])
    optimal_head_pressure_kpa = DecimalField('Optimal Head Pressure (kPa)', validators=[Optional(), NumberRange(min=0)])
    model_slug = StringField('Model Slug', validators=[Optional()])
    pump_curve_url = StringField('Pump Curve URL', validators=[Optional()])
    list_price = DecimalField('List Price', validators=[Optional(), NumberRange(min=0)])
    nett_price = DecimalField('Nett Price', validators=[Optional(), NumberRange(min=0)])
    ip56_list_price = DecimalField('IP56 List Price', validators=[Optional(), NumberRange(min=0)])
    ip56_nett_price = DecimalField('IP56 Nett Price', validators=[Optional(), NumberRange(min=0)])
    ip66_list_price = DecimalField('IP66 List Price', validators=[Optional(), NumberRange(min=0)])
    ip66_nett_price = DecimalField('IP66 Nett Price', validators=[Optional(), NumberRange(min=0)])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Pump')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            from flask import current_app
            if not current_app:
                return
            from app.models.pumps import PumpSeries
            series = PumpSeries.query.order_by(PumpSeries.series_code).all()
            self.series_id.choices = [('', 'Select Series')] + [(str(s.id), s.series_code) for s in series]
        except (RuntimeError, ModuleNotFoundError, ImportError):
            pass


class InertiaBaseForm(FlaskForm):
    """Form for creating and editing inertia bases"""
    part_number = StringField('Part Number', validators=[DataRequired()],
                            description='Unique part number')
    description = StringField('Description', validators=[Optional()])
    weight_kg = DecimalField('Weight (kg)', validators=[Optional(), NumberRange(min=0)],
                           places=3)
    length_mm = IntegerField('Length (mm)', validators=[Optional(), NumberRange(min=0)])
    width_mm = IntegerField('Width (mm)', validators=[Optional(), NumberRange(min=0)])
    depth_mm = IntegerField('Depth (mm)', validators=[Optional(), NumberRange(min=0)])
    mount_height_mm = IntegerField('Mount Height (mm)', validators=[Optional(), NumberRange(min=0)])
    list_price = DecimalField('List Price', validators=[Optional(), NumberRange(min=0)])
    nett_cost = DecimalField('Nett Cost', validators=[Optional(), NumberRange(min=0)])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Inertia Base')


class SeismicSpringForm(FlaskForm):
    """Form for creating and editing seismic springs"""
    part_number = StringField('Part Number', validators=[DataRequired()],
                            description='Unique part number')
    description = TextAreaField('Description', validators=[Optional()])
    max_load_kg = DecimalField('Max Load (kg)', validators=[Optional(), NumberRange(min=0)])
    static_deflection_mm = DecimalField('Static Deflection (mm)', validators=[Optional(), NumberRange(min=0)])
    spring_constant = DecimalField('Spring Constant', validators=[Optional(), NumberRange(min=0)],
                                  places=4)
    stripe_1_color = StringField('Stripe 1 Color', validators=[Optional()])
    stripe_2_color = StringField('Stripe 2 Color', validators=[Optional()])
    list_price = DecimalField('List Price', validators=[Optional(), NumberRange(min=0)])
    nett_price = DecimalField('Nett Price', validators=[Optional(), NumberRange(min=0)])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Seismic Spring')


class RubberMountForm(FlaskForm):
    """Form for creating and editing rubber mounts"""
    sku = StringField('SKU', validators=[DataRequired()],
                    description='Unique SKU')
    item_description = TextAreaField('Description', validators=[Optional()])
    static_deflection_mm = DecimalField('Static Deflection (mm)', validators=[Optional(), NumberRange(min=0)])
    list_price = DecimalField('List Price', validators=[Optional(), NumberRange(min=0)])
    nett_price = DecimalField('Nett Price', validators=[Optional(), NumberRange(min=0)])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Rubber Mount')


class CrossbarForm(FlaskForm):
    """Form for creating and editing crossbars"""
    sku = StringField('SKU', validators=[DataRequired()],
                    description='Unique SKU')
    description = TextAreaField('Description', validators=[Optional()])
    list_price = DecimalField('List Price', validators=[Optional(), NumberRange(min=0)])
    nett_price = DecimalField('Nett Price', validators=[Optional(), NumberRange(min=0)])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Crossbar')


class MotorProtectionForm(FlaskForm):
    """Form for creating and editing motor protection accessories"""
    description = TextAreaField('Description', validators=[DataRequired()])
    nett_cost = DecimalField('Nett Cost', validators=[DataRequired(), NumberRange(min=0)])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Motor Protection')


class DripTripTrayForm(FlaskForm):
    """Form for creating and editing drip trip trays"""
    series_id = SelectField('Pump Series', coerce=lambda x: int(x) if x and x != '' else None,
                          validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    nett_cost = DecimalField('Nett Cost', validators=[DataRequired(), NumberRange(min=0)])
    is_standard = BooleanField('Standard for Series', default=False,
                              description='Check if this is the standard tray for this series')
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Drip Trip Tray')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            from flask import current_app
            if not current_app:
                return
            from app.models.pumps import PumpSeries
            series = PumpSeries.query.order_by(PumpSeries.series_code).all()
            self.series_id.choices = [('', 'Select Series')] + [(str(s.id), s.series_code) for s in series]
        except (RuntimeError, ModuleNotFoundError, ImportError):
            pass


class PumpDutyPointForm(FlaskForm):
    """Form for creating and editing pump duty points"""
    flow_rate_lps = DecimalField('Flow Rate (L/s)', validators=[DataRequired(), NumberRange(min=0.01)])
    head_pressure_kpa = DecimalField('Head Pressure (kPa)', validators=[DataRequired(), NumberRange(min=0.01)])
    series_id = SelectField('Pump Series', coerce=lambda x: int(x) if x and x != '' else None,
                          validators=[Optional()],
                          description='Optional - filter by series')
    tolerance_percentage = DecimalField('Tolerance (%)', validators=[Optional(), NumberRange(min=0)],
                                       default=5.0,
                                       description='Matching tolerance percentage (default: 5%)')
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save Duty Point')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            from flask import current_app
            if not current_app:
                return
            from app.models.pumps import PumpSeries
            series = PumpSeries.query.order_by(PumpSeries.series_code).all()
            self.series_id.choices = [('', 'All Series')] + [(str(s.id), s.series_code) for s in series]
        except (RuntimeError, ModuleNotFoundError, ImportError):
            pass


class PumpBOMForm(FlaskForm):
    """Form for creating and editing pump BOM (Bill of Materials)"""
    pump_id = SelectField('Pump', coerce=lambda x: int(x) if x and x != '' else None,
                         validators=[DataRequired()])
    component_type = SelectField('Component Type', choices=[
        ('', 'Select Type'),
        ('inertia_base', 'Inertia Base'),
        ('seismic_spring', 'Seismic Spring'),
        ('rubber_mount', 'Rubber Mount'),
        ('crossbar', 'Crossbar'),
        ('motor_protection', 'Motor Protection'),
        ('drip_trip_tray', 'Drip Trip Tray'),
    ], validators=[DataRequired()],
    description='Type of component to link to pump')
    component_id = IntegerField('Component ID', validators=[DataRequired()],
                               description='ID of the specific component (use Manage pages to find IDs)')
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)],
                          default=1,
                          description='Number of this component needed')
    is_optional = BooleanField('Optional Component', default=False,
                              description='Check if this component is optional')
    submit = SubmitField('Save BOM Entry')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            from flask import current_app
            if not current_app:
                return
            from app.models.pumps import Pump
            pumps = Pump.query.order_by(Pump.part_number).all()
            self.pump_id.choices = [('', 'Select Pump')] + [
                (str(p.id), f"{p.part_number} - {p.name[:50]}") for p in pumps
            ]
        except (RuntimeError, ModuleNotFoundError, ImportError):
            pass


class PumpComponentForm(FlaskForm):
    """Form for creating and editing generic pump components"""
    component_type = SelectField('Component Type', choices=[
        ('accessory', 'Generic Accessory'),
        ('fitting', 'Fitting'),
        ('valve', 'Valve'),
        ('sensor', 'Sensor'),
        ('controller', 'Controller'),
        ('other', 'Other'),
    ], validators=[DataRequired()],
    description='Type of component')
    part_number = StringField('Part Number', validators=[Optional()],
                            description='Manufacturer part number')
    description = TextAreaField('Description', validators=[Optional()])
    specifications = TextAreaField('Specifications', validators=[Optional()],
                                  description='JSON or text specifications')
    list_price = DecimalField('List Price', validators=[Optional(), NumberRange(min=0)])
    nett_price = DecimalField('Nett Price', validators=[Optional(), NumberRange(min=0)])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Component')


class BOMImportForm(FlaskForm):
    """Form for importing BOM data from CSV"""
    file = FileField('CSV File', validators=[
        FileRequired(),
        FileAllowed(['csv'], 'CSV files only!')
    ], description='Upload a CSV file with pump BOM data')
    overwrite_existing = BooleanField('Overwrite Existing BOM Entries', default=False,
                                     description='If checked, will remove existing BOM entries for pumps in the file')
    create_missing_components = BooleanField('Create Missing Components', default=True,
                                            description='Automatically create components that don\'t exist')
    submit = SubmitField('Import BOM Data')


class SeismicSpringImportForm(FlaskForm):
    """Form for importing seismic spring data from CSV"""
    file = FileField('CSV File', validators=[
        FileRequired(),
        FileAllowed(['csv'], 'CSV files only!')
    ], description='Upload a CSV file with seismic spring data')
    overwrite_existing = BooleanField('Overwrite Existing Springs', default=False,
                                     description='If checked, will delete existing springs with same part numbers')
    update_existing = BooleanField('Update Existing Springs', default=True,
                                  description='If checked, will update existing springs with new data')
    submit = SubmitField('Import Seismic Springs')


class BulkComponentImportForm(FlaskForm):
    """Generic form for bulk importing component data from CSV"""
    file = FileField('CSV File', validators=[
        FileRequired(),
        FileAllowed(['csv'], 'CSV files only!')
    ], description='Upload a CSV file with component data')
    update_existing = BooleanField('Update Existing Items', default=True,
                                  description='If checked, will update existing items with new data')
    submit = SubmitField('Import Data')