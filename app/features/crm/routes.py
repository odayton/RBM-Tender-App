# app/features/crm/routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import and_, or_, desc
from datetime import datetime, timedelta

from app.extensions import db
from app.models import (
    Activity, ActivityType, ActivityStatus, Task, TaskPriority, TaskStatus, TaskType,
    Call, Email, Meeting, Note, Company, Contact, Deal, User
)
from app.models.crm import (
    CallDirection, CallOutcome, EmailDirection, MeetingType, NoteType
)
from .forms import (
    ActivityForm, TaskForm, CallForm, EmailForm, MeetingForm, NoteForm,
    ActivitySearchForm, TaskSearchForm
)

crm_bp = Blueprint('crm', __name__)

# ============================================================================
# TEST ROUTE
# ============================================================================

@crm_bp.route('/test')
def test():
    """Test route to verify CRM blueprint is working."""
    return "CRM Blueprint is working!"

@crm_bp.route('/test-template')
def test_template():
    """Test route to verify template rendering is working."""
    return render_template('crm/simple_test.html')

# ============================================================================
# CUSTOMER MANAGEMENT
# ============================================================================

@crm_bp.route('/customers')
@login_required
def customers_dashboard():
    """Customer dashboard showing companies and contacts overview."""
    try:
        # Get companies with contact counts
        companies = db.session.query(
            Company,
            db.func.count(Contact.id).label('contact_count')
        ).outerjoin(Contact).group_by(Company.id).order_by(Company.company_name).all()
        
        # Get recent contacts
        recent_contacts = Contact.query.join(Company).order_by(desc(Contact.created_at)).limit(10).all()
        
        # Get companies with recent activity (simplified for now)
        companies_with_activity = Company.query.limit(10).all()
        
        return render_template('crm/customers_dashboard.html',
                             companies=companies,
                             recent_contacts=recent_contacts,
                             companies_with_activity=companies_with_activity)
    except Exception as e:
        flash(f'Error loading customer dashboard: {str(e)}', 'error')
        # Return empty data if there's an error
        return render_template('crm/customers_dashboard.html',
                             companies=[],
                             recent_contacts=[],
                             companies_with_activity=[])

@crm_bp.route('/customers/companies')
@login_required
def companies_list():
    """List all companies with search and filtering."""
    try:
        search_term = request.args.get('search', '')
        page = request.args.get('page', 1, type=int)
        
        query = Company.query
        
        if search_term:
            query = query.filter(
                or_(
                    Company.company_name.ilike(f'%{search_term}%'),
                    Company.address.ilike(f'%{search_term}%'),
                    Company.phone_number.ilike(f'%{search_term}%')
                )
            )
        
        companies = query.order_by(Company.company_name).paginate(
            page=page, per_page=20, error_out=False
        )
        
        return render_template('crm/companies_list.html',
                             companies=companies,
                             search_term=search_term)
    except Exception as e:
        flash(f'Error loading companies: {str(e)}', 'error')
        # Return empty pagination object if there's an error
        from flask import current_app
        companies = current_app.extensions['sqlalchemy'].db.paginate(
            Company.query, page=1, per_page=20, error_out=False
        )
        return render_template('crm/companies_list.html',
                             companies=companies,
                             search_term='')

@crm_bp.route('/customers/companies/<int:company_id>')
@login_required
def company_detail(company_id):
    """Show detailed company information with contacts and activities."""
    company = Company.query.get_or_404(company_id)
    
    # Get contacts for this company
    contacts = Contact.query.filter_by(company_id=company_id).order_by(Contact.name).all()
    
    # Get recent activities for this company's contacts
    recent_activities = Activity.query.join(Contact).filter(
        Contact.company_id == company_id
    ).order_by(desc(Activity.created_at)).limit(10).all()
    
    # Get deals involving this company (simplified for now)
    deals = Deal.query.limit(10).all()
    
    # Get tasks related to this company's contacts (simplified for now)
    tasks = Task.query.limit(10).all()
    
    return render_template('crm/company_detail.html',
                         company=company,
                         contacts=contacts,
                         recent_activities=recent_activities,
                         deals=deals,
                         tasks=tasks)

@crm_bp.route('/customers/contacts')
@login_required
def contacts_list():
    """List all contacts with search and filtering."""
    search_term = request.args.get('search', '')
    company_id = request.args.get('company_id', type=int)
    page = request.args.get('page', 1, type=int)
    
    query = Contact.query.join(Company)
    
    if search_term:
        query = query.filter(
            or_(
                Contact.name.ilike(f'%{search_term}%'),
                Contact.email.ilike(f'%{search_term}%'),
                Contact.position.ilike(f'%{search_term}%'),
                Company.company_name.ilike(f'%{search_term}%')
            )
        )
    
    if company_id:
        query = query.filter(Contact.company_id == company_id)
    
    contacts = query.order_by(Contact.name).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Get companies for filter dropdown
    companies = Company.query.order_by(Company.company_name).all()
    
    return render_template('crm/contacts_list.html',
                         contacts=contacts,
                         companies=companies,
                         search_term=search_term,
                         selected_company_id=company_id)

@crm_bp.route('/customers/contacts/<int:contact_id>')
@login_required
def contact_detail(contact_id):
    """Show detailed contact information with activities and tasks."""
    contact = Contact.query.get_or_404(contact_id)
    
    # Get recent activities for this contact
    recent_activities = Activity.query.filter_by(contact_id=contact_id).order_by(
        desc(Activity.created_at)
    ).limit(10).all()
    
    # Get tasks for this contact
    tasks = Task.query.filter_by(contact_id=contact_id).order_by(Task.due_date).all()
    
    # Get deals involving this contact (simplified for now)
    deals = Deal.query.limit(10).all()
    
    return render_template('crm/contact_detail.html',
                         contact=contact,
                         recent_activities=recent_activities,
                         tasks=tasks,
                         deals=deals)

@crm_bp.route('/customers/companies/<int:company_id>/log-activity', methods=['GET', 'POST'])
@login_required
def log_company_activity(company_id):
    """Log an activity for a company (will be associated with primary contact)."""
    company = Company.query.get_or_404(company_id)
    
    # Get primary contact for this company
    primary_contact = Contact.query.filter_by(
        company_id=company_id, is_primary=True
    ).first()
    
    if not primary_contact:
        flash('No primary contact found for this company. Please assign a primary contact first.', 'warning')
        return redirect(url_for('crm.company_detail', company_id=company_id))
    
    form = ActivityForm()
    form.contact_id.data = primary_contact.id
    form.company_id.data = company_id
    
    if form.validate_on_submit():
        try:
            activity = Activity(
                activity_type=form.activity_type.data,
                subject=form.subject.data,
                description=form.description.data,
                contact_id=form.contact_id.data,
                deal_id=form.deal_id.data if form.deal_id.data else None,
                user_id=current_user.id,
                status=ActivityStatus.COMPLETED
            )
            db.session.add(activity)
            db.session.commit()
            
            flash('Activity logged successfully!', 'success')
            return redirect(url_for('crm.company_detail', company_id=company_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error logging activity: {str(e)}', 'error')
    
    return render_template('crm/log_company_activity.html',
                         form=form,
                         company=company,
                         primary_contact=primary_contact)

@crm_bp.route('/customers/contacts/<int:contact_id>/log-activity', methods=['GET', 'POST'])
@login_required
def log_contact_activity(contact_id):
    """Log an activity for a specific contact."""
    contact = Contact.query.get_or_404(contact_id)
    
    form = ActivityForm()
    form.contact_id.data = contact_id
    form.company_id.data = contact.company_id
    
    if form.validate_on_submit():
        try:
            activity = Activity(
                activity_type=form.activity_type.data,
                subject=form.subject.data,
                description=form.description.data,
                contact_id=form.contact_id.data,
                deal_id=form.deal_id.data if form.deal_id.data else None,
                user_id=current_user.id,
                status=ActivityStatus.COMPLETED
            )
            db.session.add(activity)
            db.session.commit()
            
            flash('Activity logged successfully!', 'success')
            return redirect(url_for('crm.contact_detail', contact_id=contact_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error logging activity: {str(e)}', 'error')
    
    return render_template('crm/log_contact_activity.html',
                         form=form,
                         contact=contact)

# ============================================================================
# DASHBOARD & OVERVIEW
# ============================================================================

@crm_bp.route('/dashboard')
@login_required
def dashboard():
    """CRM Dashboard with overview of activities and tasks."""
    # Get upcoming tasks
    upcoming_tasks = Task.query.filter(
        and_(
            Task.assigned_to_id == current_user.id,
            Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS]),
            Task.due_date >= datetime.utcnow()
        )
    ).order_by(Task.due_date).limit(10).all()
    
    # Get overdue tasks
    overdue_tasks = Task.query.filter(
        and_(
            Task.assigned_to_id == current_user.id,
            Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS]),
            Task.due_date < datetime.utcnow()
        )
    ).order_by(Task.due_date).limit(10).all()
    
    # Get recent activities
    recent_activities = Activity.query.filter(
        Activity.user_id == current_user.id
    ).order_by(desc(Activity.created_at)).limit(10).all()
    
    # Get today's activities
    today = datetime.utcnow().date()
    today_activities = Activity.query.filter(
        and_(
            Activity.user_id == current_user.id,
            db.func.date(Activity.created_at) == today
        )
    ).all()
    
    # Get statistics
    total_tasks = Task.query.filter(Task.assigned_to_id == current_user.id).count()
    completed_tasks = Task.query.filter(
        and_(
            Task.assigned_to_id == current_user.id,
            Task.status == TaskStatus.COMPLETED
        )
    ).count()
    
    return render_template('crm/dashboard.html',
                         upcoming_tasks=upcoming_tasks,
                         overdue_tasks=overdue_tasks,
                         recent_activities=recent_activities,
                         today_activities=today_activities,
                         total_tasks=total_tasks,
                         completed_tasks=completed_tasks)

# ============================================================================
# ACTIVITIES
# ============================================================================

@crm_bp.route('/activities')
@login_required
def activities_list():
    """List all activities with search and filtering."""
    form = ActivitySearchForm()
    
    # Build query
    query = Activity.query
    
    # Check for deal_id in URL parameters (for filtering from deal page)
    deal_id_param = request.args.get('deal_id', type=int)
    if deal_id_param:
        query = query.filter(Activity.deal_id == deal_id_param)
        form.deal_id.data = deal_id_param
    
    # Apply filters
    if form.search_term.data:
        search_term = f"%{form.search_term.data}%"
        query = query.filter(
            or_(
                Activity.title.ilike(search_term),
                Activity.description.ilike(search_term),
                Activity.outcome.ilike(search_term)
            )
        )
    
    if form.activity_type.data:
        query = query.filter(Activity.activity_type == ActivityType(form.activity_type.data))
    
    if form.status.data:
        query = query.filter(Activity.status == ActivityStatus(form.status.data))
    
    if form.date_from.data:
        query = query.filter(Activity.created_at >= form.date_from.data)
    
    if form.date_to.data:
        query = query.filter(Activity.created_at <= form.date_to.data)
    
    if form.company_id.data:
        query = query.filter(Activity.company_id == form.company_id.data)
    
    if form.contact_id.data:
        query = query.filter(Activity.contact_id == form.contact_id.data)
    
    if form.deal_id.data and not deal_id_param:
        query = query.filter(Activity.deal_id == form.deal_id.data)
    
    # Order by creation date
    activities = query.order_by(desc(Activity.created_at)).paginate(
        page=request.args.get('page', 1, type=int),
        per_page=20
    )
    
    # Populate form choices
    companies = Company.query.filter(Company.is_active == True).all()
    contacts = Contact.query.filter(Contact.is_active == True).all()
    deals = Deal.query.filter(Deal.is_active == True).all()
    
    form.company_id.choices = [('', 'All Companies')] + [(c.id, c.company_name) for c in companies]
    form.contact_id.choices = [('', 'All Contacts')] + [(c.id, c.name) for c in contacts]
    form.deal_id.choices = [('', 'All Deals')] + [(d.id, d.project_name) for d in deals]
    
    return render_template('crm/activities_list.html',
                         activities=activities,
                         form=form)

@crm_bp.route('/activities/new', methods=['GET', 'POST'])
@login_required
def create_activity():
    """Create a new activity."""
    form = ActivityForm()
    
    # Populate form choices
    companies = Company.query.filter(Company.is_active == True).all()
    contacts = Contact.query.filter(Contact.is_active == True).all()
    deals = Deal.query.filter(Deal.is_active == True).all()
    
    form.company_id.choices = [('', 'Select Company')] + [(c.id, c.company_name) for c in companies]
    form.contact_id.choices = [('', 'Select Contact')] + [(c.id, c.name) for c in contacts]
    form.deal_id.choices = [('', 'Select Deal')] + [(d.id, d.project_name) for d in deals]
    
    if form.validate_on_submit():
        activity = Activity(
            title=form.title.data,
            description=form.description.data,
            activity_type=ActivityType(form.activity_type.data),
            status=ActivityStatus(form.status.data),
            scheduled_date=form.scheduled_date.data,
            duration_minutes=form.duration_minutes.data,
            company_id=form.company_id.data if form.company_id.data else None,
            contact_id=form.contact_id.data if form.contact_id.data else None,
            deal_id=form.deal_id.data if form.deal_id.data else None,
            is_private=form.is_private.data,
            tags=form.tags.data,
            outcome=form.outcome.data,
            next_action=form.next_action.data,
            user_id=current_user.id
        )
        
        db.session.add(activity)
        db.session.commit()
        
        flash('Activity created successfully!', 'success')
        return redirect(url_for('crm.activities_list'))
    
    return render_template('crm/activity_form.html', form=form, title='Create Activity')

@crm_bp.route('/activities/<int:activity_id>')
@login_required
def view_activity(activity_id):
    """View a specific activity."""
    activity = Activity.query.get_or_404(activity_id)
    
    # Check permissions
    if activity.is_private and activity.user_id != current_user.id and not current_user.is_admin():
        flash('You do not have permission to view this activity.', 'error')
        return redirect(url_for('crm.activities_list'))
    
    return render_template('crm/activity_detail.html', activity=activity)

@crm_bp.route('/activities/<int:activity_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_activity(activity_id):
    """Edit an activity."""
    activity = Activity.query.get_or_404(activity_id)
    
    # Check permissions
    if activity.user_id != current_user.id and not current_user.is_admin():
        flash('You do not have permission to edit this activity.', 'error')
        return redirect(url_for('crm.activities_list'))
    
    form = ActivityForm(obj=activity)
    
    # Populate form choices
    companies = Company.query.filter(Company.is_active == True).all()
    contacts = Contact.query.filter(Contact.is_active == True).all()
    deals = Deal.query.filter(Deal.is_active == True).all()
    
    form.company_id.choices = [('', 'Select Company')] + [(c.id, c.company_name) for c in companies]
    form.contact_id.choices = [('', 'Select Contact')] + [(c.id, c.name) for c in contacts]
    form.deal_id.choices = [('', 'Select Deal')] + [(d.id, d.project_name) for d in deals]
    
    if form.validate_on_submit():
        activity.title = form.title.data
        activity.description = form.description.data
        activity.activity_type = ActivityType(form.activity_type.data)
        activity.status = ActivityStatus(form.status.data)
        activity.scheduled_date = form.scheduled_date.data
        activity.duration_minutes = form.duration_minutes.data
        activity.company_id = form.company_id.data if form.company_id.data else None
        activity.contact_id = form.contact_id.data if form.contact_id.data else None
        activity.deal_id = form.deal_id.data if form.deal_id.data else None
        activity.is_private = form.is_private.data
        activity.tags = form.tags.data
        activity.outcome = form.outcome.data
        activity.next_action = form.next_action.data
        
        db.session.commit()
        
        flash('Activity updated successfully!', 'success')
        return redirect(url_for('crm.view_activity', activity_id=activity.id))
    
    return render_template('crm/activity_form.html', form=form, title='Edit Activity')

@crm_bp.route('/activities/<int:activity_id>/delete', methods=['POST'])
@login_required
def delete_activity(activity_id):
    """Delete an activity."""
    activity = Activity.query.get_or_404(activity_id)
    
    # Check permissions
    if activity.user_id != current_user.id and not current_user.is_admin():
        flash('You do not have permission to delete this activity.', 'error')
        return redirect(url_for('crm.activities_list'))
    
    db.session.delete(activity)
    db.session.commit()
    
    flash('Activity deleted successfully!', 'success')
    return redirect(url_for('crm.activities_list'))

# ============================================================================
# TASKS
# ============================================================================

@crm_bp.route('/tasks')
@login_required
def tasks_list():
    """List all tasks with search and filtering."""
    form = TaskSearchForm()
    
    # Build query
    query = Task.query
    
    # Apply filters
    if form.search_term.data:
        search_term = f"%{form.search_term.data}%"
        query = query.filter(
            or_(
                Task.title.ilike(search_term),
                Task.description.ilike(search_term),
                Task.notes.ilike(search_term)
            )
        )
    
    if form.task_type.data:
        query = query.filter(Task.task_type == TaskType(form.task_type.data))
    
    if form.priority.data:
        query = query.filter(Task.priority == TaskPriority(form.priority.data))
    
    if form.status.data:
        query = query.filter(Task.status == TaskStatus(form.status.data))
    
    if form.assigned_to_id.data:
        query = query.filter(Task.assigned_to_id == form.assigned_to_id.data)
    
    if form.due_date_from.data:
        query = query.filter(Task.due_date >= form.due_date_from.data)
    
    if form.due_date_to.data:
        query = query.filter(Task.due_date <= form.due_date_to.data)
    
    if form.company_id.data:
        query = query.filter(Task.company_id == form.company_id.data)
    
    if form.contact_id.data:
        query = query.filter(Task.contact_id == form.contact_id.data)
    
    if form.deal_id.data:
        query = query.filter(Task.deal_id == form.deal_id.data)
    
    # Order by due date
    tasks = query.order_by(Task.due_date).paginate(
        page=request.args.get('page', 1, type=int),
        per_page=20
    )
    
    # Populate form choices
    users = User.query.filter(User.is_active == True).all()
    companies = Company.query.filter(Company.is_active == True).all()
    contacts = Contact.query.filter(Contact.is_active == True).all()
    deals = Deal.query.filter(Deal.is_active == True).all()
    
    form.assigned_to_id.choices = [('', 'All Users')] + [(u.id, u.full_name) for u in users]
    form.company_id.choices = [('', 'All Companies')] + [(c.id, c.company_name) for c in companies]
    form.contact_id.choices = [('', 'All Contacts')] + [(c.id, c.name) for c in contacts]
    form.deal_id.choices = [('', 'All Deals')] + [(d.id, d.project_name) for d in deals]
    
    return render_template('crm/tasks_list.html',
                         tasks=tasks,
                         form=form)

@crm_bp.route('/tasks/new', methods=['GET', 'POST'])
@login_required
def create_task():
    """Create a new task."""
    form = TaskForm()
    
    # Populate form choices
    users = User.query.filter(User.is_active == True).all()
    companies = Company.query.filter(Company.is_active == True).all()
    contacts = Contact.query.filter(Contact.is_active == True).all()
    deals = Deal.query.filter(Deal.is_active == True).all()
    
    form.assigned_to_id.choices = [(u.id, u.full_name) for u in users]
    form.company_id.choices = [('', 'Select Company')] + [(c.id, c.company_name) for c in companies]
    form.contact_id.choices = [('', 'Select Contact')] + [(c.id, c.name) for c in contacts]
    form.deal_id.choices = [('', 'Select Deal')] + [(d.id, d.project_name) for d in deals]
    
    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            description=form.description.data,
            task_type=TaskType(form.task_type.data),
            priority=TaskPriority(form.priority.data),
            status=TaskStatus(form.status.data),
            due_date=form.due_date.data,
            start_date=form.start_date.data,
            estimated_hours=form.estimated_hours.data,
            assigned_to_id=form.assigned_to_id.data,
            company_id=form.company_id.data if form.company_id.data else None,
            contact_id=form.contact_id.data if form.contact_id.data else None,
            deal_id=form.deal_id.data if form.deal_id.data else None,
            is_recurring=form.is_recurring.data,
            recurrence_pattern=form.recurrence_pattern.data,
            recurrence_interval=form.recurrence_interval.data,
            tags=form.tags.data,
            notes=form.notes.data,
            created_by_id=current_user.id
        )
        
        db.session.add(task)
        db.session.commit()
        
        flash('Task created successfully!', 'success')
        return redirect(url_for('crm.tasks_list'))
    
    return render_template('crm/task_form.html', form=form, title='Create Task')

@crm_bp.route('/tasks/<int:task_id>')
@login_required
def view_task(task_id):
    """View a specific task."""
    task = Task.query.get_or_404(task_id)
    
    # Check permissions
    if task.assigned_to_id != current_user.id and not current_user.is_admin():
        flash('You do not have permission to view this task.', 'error')
        return redirect(url_for('crm.tasks_list'))
    
    return render_template('crm/task_detail.html', task=task)

@crm_bp.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    """Edit a task."""
    task = Task.query.get_or_404(task_id)
    
    # Check permissions
    if task.assigned_to_id != current_user.id and not current_user.is_admin():
        flash('You do not have permission to edit this task.', 'error')
        return redirect(url_for('crm.tasks_list'))
    
    form = TaskForm(obj=task)
    
    # Populate form choices
    users = User.query.filter(User.is_active == True).all()
    companies = Company.query.filter(Company.is_active == True).all()
    contacts = Contact.query.filter(Contact.is_active == True).all()
    deals = Deal.query.filter(Deal.is_active == True).all()
    
    form.assigned_to_id.choices = [(u.id, u.full_name) for u in users]
    form.company_id.choices = [('', 'Select Company')] + [(c.id, c.company_name) for c in companies]
    form.contact_id.choices = [('', 'Select Contact')] + [(c.id, c.name) for c in contacts]
    form.deal_id.choices = [('', 'Select Deal')] + [(d.id, d.project_name) for d in deals]
    
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.task_type = TaskType(form.task_type.data)
        task.priority = TaskPriority(form.priority.data)
        task.status = TaskStatus(form.status.data)
        task.due_date = form.due_date.data
        task.start_date = form.start_date.data
        task.estimated_hours = form.estimated_hours.data
        task.assigned_to_id = form.assigned_to_id.data
        task.company_id = form.company_id.data if form.company_id.data else None
        task.contact_id = form.contact_id.data if form.contact_id.data else None
        task.deal_id = form.deal_id.data if form.deal_id.data else None
        task.is_recurring = form.is_recurring.data
        task.recurrence_pattern = form.recurrence_pattern.data
        task.recurrence_interval = form.recurrence_interval.data
        task.tags = form.tags.data
        task.notes = form.notes.data
        
        db.session.commit()
        
        flash('Task updated successfully!', 'success')
        return redirect(url_for('crm.view_task', task_id=task.id))
    
    return render_template('crm/task_form.html', form=form, title='Edit Task')

@crm_bp.route('/tasks/<int:task_id>/complete', methods=['POST'])
@login_required
def complete_task(task_id):
    """Mark a task as completed."""
    task = Task.query.get_or_404(task_id)
    
    # Check permissions
    if task.assigned_to_id != current_user.id and not current_user.is_admin():
        flash('You do not have permission to complete this task.', 'error')
        return redirect(url_for('crm.tasks_list'))
    
    completion_notes = request.form.get('completion_notes')
    task.mark_completed(completion_notes)
    db.session.commit()
    
    flash('Task marked as completed!', 'success')
    return redirect(url_for('crm.view_task', task_id=task.id))

@crm_bp.route('/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    """Delete a task."""
    task = Task.query.get_or_404(task_id)
    
    # Check permissions
    if task.assigned_to_id != current_user.id and not current_user.is_admin():
        flash('You do not have permission to delete this task.', 'error')
        return redirect(url_for('crm.tasks_list'))
    
    db.session.delete(task)
    db.session.commit()
    
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('crm.tasks_list'))

# ============================================================================
# INTERACTIONS (CALLS, EMAILS, MEETINGS, NOTES)
# ============================================================================

@crm_bp.route('/calls/new', methods=['GET', 'POST'])
@login_required
def log_call():
    """Log a new call."""
    form = CallForm()
    
    if form.validate_on_submit():
        # Create activity first
        activity = Activity(
            title=f"Call: {form.phone_number.data}",
            activity_type=ActivityType.CALL,
            status=ActivityStatus.COMPLETED,
            user_id=current_user.id,
            company_id=request.form.get('company_id'),
            contact_id=request.form.get('contact_id'),
            deal_id=request.form.get('deal_id')
        )
        
        db.session.add(activity)
        db.session.flush()  # Get the activity ID
        
        # Create call record
        call = Call(
            activity_id=activity.id,
            phone_number=form.phone_number.data,
            direction=CallDirection(form.direction.data),
            outcome=CallOutcome(form.outcome.data),
            duration_seconds=form.duration_seconds.data or 0,
            call_notes=form.call_notes.data,
            follow_up_required=form.follow_up_required.data,
            follow_up_date=form.follow_up_date.data,
            call_recording_url=form.call_recording_url.data
        )
        
        db.session.add(call)
        db.session.commit()
        
        flash('Call logged successfully!', 'success')
        return redirect(url_for('crm.activities_list'))
    
    return render_template('crm/call_form.html', form=form)

@crm_bp.route('/emails/new', methods=['GET', 'POST'])
@login_required
def log_email():
    """Log a new email."""
    form = EmailForm()
    
    if form.validate_on_submit():
        # Create activity first
        activity = Activity(
            title=f"Email: {form.subject.data}",
            activity_type=ActivityType.EMAIL,
            status=ActivityStatus.COMPLETED,
            user_id=current_user.id,
            company_id=request.form.get('company_id'),
            contact_id=request.form.get('contact_id'),
            deal_id=request.form.get('deal_id')
        )
        
        db.session.add(activity)
        db.session.flush()  # Get the activity ID
        
        # Create email record
        email = Email(
            activity_id=activity.id,
            subject=form.subject.data,
            direction=EmailDirection(form.direction.data),
            sender_email=form.sender_email.data,
            recipient_email=form.recipient_email.data,
            email_body=form.email_body.data,
            has_attachments=form.has_attachments.data,
            attachment_count=form.attachment_count.data or 0,
            is_read=form.is_read.data,
            is_replied=form.is_replied.data,
            email_thread_id=form.email_thread_id.data
        )
        
        db.session.add(email)
        db.session.commit()
        
        flash('Email logged successfully!', 'success')
        return redirect(url_for('crm.activities_list'))
    
    return render_template('crm/email_form.html', form=form)

@crm_bp.route('/meetings/new', methods=['GET', 'POST'])
@login_required
def log_meeting():
    """Log a new meeting."""
    form = MeetingForm()
    
    if form.validate_on_submit():
        # Create activity first
        activity = Activity(
            title=f"Meeting: {form.meeting_type.data}",
            activity_type=ActivityType.MEETING,
            status=ActivityStatus.COMPLETED,
            user_id=current_user.id,
            company_id=request.form.get('company_id'),
            contact_id=request.form.get('contact_id'),
            deal_id=request.form.get('deal_id')
        )
        
        db.session.add(activity)
        db.session.flush()  # Get the activity ID
        
        # Create meeting record
        meeting = Meeting(
            activity_id=activity.id,
            meeting_type=MeetingType(form.meeting_type.data),
            location=form.location.data,
            meeting_notes=form.meeting_notes.data,
            attendees=form.attendees.data,
            agenda=form.agenda.data,
            action_items=form.action_items.data,
            meeting_url=form.meeting_url.data,
            follow_up_required=form.follow_up_required.data,
            follow_up_date=form.follow_up_date.data,
            follow_up_notes=form.follow_up_notes.data
        )
        
        db.session.add(meeting)
        db.session.commit()
        
        flash('Meeting logged successfully!', 'success')
        return redirect(url_for('crm.activities_list'))
    
    return render_template('crm/meeting_form.html', form=form)

@crm_bp.route('/notes/new', methods=['GET', 'POST'])
@login_required
def create_note():
    """Create a new note."""
    form = NoteForm()
    
    if request.method == 'POST':
        # Handle form submission from modal
        title = request.form.get('title')
        content = request.form.get('content')
        note_type = request.form.get('note_type', 'GENERAL')
        tags = request.form.get('tags', '')
        is_important = request.form.get('is_important') == 'on'
        is_internal = request.form.get('is_internal') == 'on'
        deal_id = request.form.get('deal_id')
        company_id = request.form.get('company_id')
        contact_id = request.form.get('contact_id')
        
        if title and content:
            # Create activity first
            activity = Activity(
                title=title,
                activity_type=ActivityType.NOTE,
                status=ActivityStatus.COMPLETED,
                user_id=current_user.id,
                company_id=company_id,
                contact_id=contact_id,
                deal_id=deal_id
            )
            
            db.session.add(activity)
            db.session.flush()  # Get the activity ID
            
            # Create note record
            note = Note(
                activity_id=activity.id,
                note_type=NoteType(note_type),
                content=content,
                is_internal=is_internal,
                is_important=is_important,
                tags=tags
            )
            
            db.session.add(note)
            db.session.commit()
            
            flash('Note created successfully!', 'success')
            
            # Redirect back to deal page if deal_id was provided
            if deal_id:
                return redirect(url_for('deals.deal_details', deal_id=deal_id))
            else:
                return redirect(url_for('crm.activities_list'))
        else:
            flash('Title and content are required!', 'error')
    
    return render_template('crm/note_form.html', form=form)

# ============================================================================
# API ENDPOINTS FOR AJAX
# ============================================================================

@crm_bp.route('/api/upcoming-tasks')
@login_required
def api_upcoming_tasks():
    """API endpoint for upcoming tasks (for dashboard widgets)."""
    tasks = Task.query.filter(
        and_(
            Task.assigned_to_id == current_user.id,
            Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS]),
            Task.due_date >= datetime.utcnow()
        )
    ).order_by(Task.due_date).limit(5).all()
    
    return jsonify([{
        'id': task.id,
        'title': task.title,
        'due_date': task.due_date.isoformat(),
        'priority': task.priority.value,
        'status': task.status.value,
        'is_overdue': task.is_overdue(),
        'days_until_due': task.get_days_until_due()
    } for task in tasks])

@crm_bp.route('/api/recent-activities')
@login_required
def api_recent_activities():
    """API endpoint for recent activities (for dashboard widgets)."""
    activities = Activity.query.filter(
        Activity.user_id == current_user.id
    ).order_by(desc(Activity.created_at)).limit(5).all()
    
    return jsonify([{
        'id': activity.id,
        'title': activity.title,
        'activity_type': activity.activity_type.value,
        'created_at': activity.created_at.isoformat(),
        'company_name': activity.company.company_name if activity.company else None,
        'contact_name': activity.contact.name if activity.contact else None
    } for activity in activities]) 