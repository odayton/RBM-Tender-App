# app/features/crm/forms.py

from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, SelectField, DateTimeField, 
    IntegerField, BooleanField, HiddenField, FieldList, FormField
)
from wtforms.validators import DataRequired, Email, Optional, Length, NumberRange
from wtforms.widgets import DateTimeInput
from datetime import datetime

from app.models.crm import (
    ActivityType, ActivityStatus, TaskPriority, TaskStatus, TaskType,
    CallDirection, CallOutcome, EmailDirection, MeetingType, NoteType
)

class ActivityForm(FlaskForm):
    """Base form for creating/editing activities."""
    subject = StringField('Subject', validators=[DataRequired(), Length(min=3, max=200)])
    description = TextAreaField('Description')
    activity_type = SelectField('Activity Type', coerce=str, validators=[DataRequired()])
    status = SelectField('Status', coerce=str, validators=[DataRequired()])
    
    # Timing
    scheduled_date = DateTimeField('Scheduled Date', 
                                 widget=DateTimeInput(),
                                 validators=[Optional()])
    duration_minutes = IntegerField('Duration (minutes)', 
                                  validators=[Optional(), NumberRange(min=0)])
    
    # Relationships
    company_id = SelectField('Company', coerce=lambda x: int(x) if x and x != '' else None, validators=[Optional()])
    contact_id = SelectField('Contact', coerce=lambda x: int(x) if x and x != '' else None, validators=[Optional()])
    deal_id = SelectField('Deal', coerce=lambda x: int(x) if x and x != '' else None, validators=[Optional()])
    
    # Additional fields
    is_private = BooleanField('Private Activity')
    tags = StringField('Tags (comma-separated)')
    outcome = StringField('Outcome')
    next_action = TextAreaField('Next Action')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.activity_type.choices = [(t.value, t.value) for t in ActivityType]
        self.status.choices = [(s.value, s.value) for s in ActivityStatus]
        
        # Populate company choices
        from app.models import Company
        companies = Company.query.order_by(Company.company_name).all()
        self.company_id.choices = [('', 'Select Company')] + [(str(c.id), c.company_name) for c in companies]
        
        # Populate contact choices
        from app.models import Contact
        contacts = Contact.query.join(Company).order_by(Contact.name).all()
        self.contact_id.choices = [('', 'Select Contact')] + [(str(c.id), f"{c.name} ({c.company.company_name})") for c in contacts]
        
        # Populate deal choices
        from app.models import Deal
        deals = Deal.query.order_by(Deal.project_name).all()
        self.deal_id.choices = [('', 'Select Deal')] + [(str(d.id), d.project_name) for d in deals]

class TaskForm(FlaskForm):
    """Form for creating/editing tasks."""
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=200)])
    description = TextAreaField('Description')
    task_type = SelectField('Task Type', coerce=str, validators=[DataRequired()])
    priority = SelectField('Priority', coerce=str, validators=[DataRequired()])
    status = SelectField('Status', coerce=str, validators=[DataRequired()])
    
    # Timing
    due_date = DateTimeField('Due Date', 
                           widget=DateTimeInput(),
                           validators=[DataRequired()])
    start_date = DateTimeField('Start Date', 
                             widget=DateTimeInput(),
                             validators=[Optional()])
    estimated_hours = IntegerField('Estimated Hours', 
                                 validators=[Optional(), NumberRange(min=0)])
    
    # Relationships
    assigned_to_id = SelectField('Assigned To', coerce=int, validators=[DataRequired()])
    company_id = SelectField('Company', coerce=lambda x: int(x) if x and x != '' else None, validators=[Optional()])
    contact_id = SelectField('Contact', coerce=lambda x: int(x) if x and x != '' else None, validators=[Optional()])
    deal_id = SelectField('Deal', coerce=lambda x: int(x) if x and x != '' else None, validators=[Optional()])
    
    # Task management
    is_recurring = BooleanField('Recurring Task')
    recurrence_pattern = SelectField('Recurrence Pattern', 
                                   choices=[('', 'None'), ('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')])
    recurrence_interval = IntegerField('Recurrence Interval', 
                                     validators=[Optional(), NumberRange(min=1)])
    tags = StringField('Tags (comma-separated)')
    notes = TextAreaField('Notes')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_type.choices = [(t.value, t.value) for t in TaskType]
        self.priority.choices = [(p.value, p.value) for p in TaskPriority]
        self.status.choices = [(s.value, s.value) for s in TaskStatus]

class CallForm(FlaskForm):
    """Form for logging calls."""
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=5, max=30)])
    direction = SelectField('Direction', coerce=str, validators=[DataRequired()])
    outcome = SelectField('Outcome', coerce=str, validators=[DataRequired()])
    duration_seconds = IntegerField('Duration (seconds)', 
                                  validators=[Optional(), NumberRange(min=0)])
    
    # Call specific fields
    call_notes = TextAreaField('Call Notes')
    follow_up_required = BooleanField('Follow-up Required')
    follow_up_date = DateTimeField('Follow-up Date', 
                                 widget=DateTimeInput(),
                                 validators=[Optional()])
    call_recording_url = StringField('Call Recording URL')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.direction.choices = [(d.value, d.value) for d in CallDirection]
        self.outcome.choices = [(o.value, o.value) for o in CallOutcome]

class EmailForm(FlaskForm):
    """Form for logging emails."""
    subject = StringField('Subject', validators=[DataRequired(), Length(max=500)])
    direction = SelectField('Direction', coerce=str, validators=[DataRequired()])
    sender_email = StringField('Sender Email', validators=[DataRequired(), Email()])
    recipient_email = StringField('Recipient Email', validators=[DataRequired(), Email()])
    
    # Email specific fields
    email_body = TextAreaField('Email Body')
    has_attachments = BooleanField('Has Attachments')
    attachment_count = IntegerField('Attachment Count', 
                                  validators=[Optional(), NumberRange(min=0)])
    is_read = BooleanField('Read')
    is_replied = BooleanField('Replied')
    email_thread_id = StringField('Email Thread ID')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.direction.choices = [(d.value, d.value) for d in EmailDirection]

class MeetingForm(FlaskForm):
    """Form for logging meetings."""
    meeting_type = SelectField('Meeting Type', coerce=str, validators=[DataRequired()])
    location = StringField('Location', validators=[Length(max=200)])
    meeting_notes = TextAreaField('Meeting Notes')
    
    # Meeting specific fields
    attendees = TextAreaField('Attendees (one per line)')
    agenda = TextAreaField('Agenda')
    action_items = TextAreaField('Action Items (one per line)')
    meeting_url = StringField('Meeting URL')
    
    # Follow-up
    follow_up_required = BooleanField('Follow-up Required')
    follow_up_date = DateTimeField('Follow-up Date', 
                                 widget=DateTimeInput(),
                                 validators=[Optional()])
    follow_up_notes = TextAreaField('Follow-up Notes')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.meeting_type.choices = [(t.value, t.value) for t in MeetingType]

class NoteForm(FlaskForm):
    """Form for creating notes."""
    note_type = SelectField('Note Type', coerce=str, validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    
    # Note specific fields
    is_internal = BooleanField('Internal Note')
    is_important = BooleanField('Important')
    tags = StringField('Tags (comma-separated)')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.note_type.choices = [(t.value, t.value) for t in NoteType]

class ActivitySearchForm(FlaskForm):
    """Form for searching activities."""
    search_term = StringField('Search')
    activity_type = SelectField('Activity Type', coerce=str)
    status = SelectField('Status', coerce=str)
    assigned_to_id = SelectField('Assigned To', coerce=lambda x: int(x) if x and x != '' else None)
    date_from = DateTimeField('From Date', widget=DateTimeInput(), validators=[Optional()])
    date_to = DateTimeField('To Date', widget=DateTimeInput(), validators=[Optional()])
    company_id = SelectField('Company', coerce=lambda x: int(x) if x and x != '' else None)
    contact_id = SelectField('Contact', coerce=lambda x: int(x) if x and x != '' else None)
    deal_id = SelectField('Deal', coerce=lambda x: int(x) if x and x != '' else None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.activity_type.choices = [('', 'All Types')] + [(t.value, t.value) for t in ActivityType]
        self.status.choices = [('', 'All Statuses')] + [(s.value, s.value) for s in ActivityStatus]
        
        # Populate assigned_to choices
        from app.models import User
        users = User.query.order_by(User.username).all()
        self.assigned_to_id.choices = [('', 'All Users')] + [(str(u.id), u.username) for u in users]
        
        # Populate company choices
        from app.models import Company
        companies = Company.query.order_by(Company.company_name).all()
        self.company_id.choices = [('', 'All Companies')] + [(str(c.id), c.company_name) for c in companies]
        
        # Populate contact choices
        from app.models import Contact
        contacts = Contact.query.join(Company).order_by(Contact.name).all()
        self.contact_id.choices = [('', 'All Contacts')] + [(str(c.id), f"{c.name} ({c.company.company_name})") for c in contacts]
        
        # Populate deal choices
        from app.models import Deal
        deals = Deal.query.order_by(Deal.project_name).all()
        self.deal_id.choices = [('', 'All Deals')] + [(str(d.id), d.project_name) for d in deals]

class TaskSearchForm(FlaskForm):
    """Form for searching tasks."""
    search_term = StringField('Search')
    task_type = SelectField('Task Type', coerce=str)
    priority = SelectField('Priority', coerce=str)
    status = SelectField('Status', coerce=str)
    assigned_to_id = SelectField('Assigned To', coerce=lambda x: int(x) if x and x != '' else None)
    due_date_from = DateTimeField('Due From', widget=DateTimeInput(), validators=[Optional()])
    due_date_to = DateTimeField('Due To', widget=DateTimeInput(), validators=[Optional()])
    company_id = SelectField('Company', coerce=lambda x: int(x) if x and x != '' else None)
    contact_id = SelectField('Contact', coerce=lambda x: int(x) if x and x != '' else None)
    deal_id = SelectField('Deal', coerce=lambda x: int(x) if x and x != '' else None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_type.choices = [('', 'All Types')] + [(t.value, t.value) for t in TaskType]
        self.priority.choices = [('', 'All Priorities')] + [(p.value, p.value) for p in TaskPriority]
        self.status.choices = [('', 'All Statuses')] + [(s.value, s.value) for s in TaskStatus] 