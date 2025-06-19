from flask import (
    render_template, 
    request, 
    redirect, 
    url_for, 
    flash, 
    jsonify, 
    Blueprint
)
from datetime import datetime, timedelta
from collections import defaultdict
from decimal import Decimal

# Import the new blueprint object from the __init__.py in this folder
from . import deals_bp
# Import the forms from the forms.py file in this folder
from .forms import DealForm, QuoteForm, QuoteLineItemForm, DealStageUpdateForm

# Import all necessary models
from app.models import Deal, Quote, QuoteLineItem, DealStage, AustralianState, DealType, Company, Customer, User
from app.core.core_errors import ValidationError
# Import the refactored manager
from app.utils.db_utils.deal.db_deals import DealDatabaseManager


# All routes now use the @deals_bp decorator
@deals_bp.route('/deals', methods=['GET'])
def list_deals():
    """Lists all deals and groups them by stage for the template."""
    # Use the manager to fetch all deals
    all_deals = DealDatabaseManager.get_all_deals()
    
    # Group deals by their stage value for display in the template
    deals_by_stage = defaultdict(list)
    for deal in all_deals:
        deals_by_stage[deal.stage.value].append(deal)

    form = DealForm()
    current_date = datetime.utcnow()
    default_valid_until = current_date + timedelta(days=90)

    # Render the main deals page, passing in the grouped deals and the form
    return render_template(
        'deals/deals.html', 
        deals_by_stage=deals_by_stage, 
        form=form,
        current_date=current_date,
        default_valid_until=default_valid_until
    )

@deals_bp.route('/deals/create', methods=['POST'])
def create_deal():
    """Handles the creation of a new deal from form submission."""
    form = DealForm()
    if form.validate_on_submit():
        # Prepare data dictionary from the form
        deal_data = {
            'project_name': form.project_name.data,
            'state': form.state.data,
            'deal_type': form.deal_type.data,
            'stage': form.stage.data,
            'total_amount': form.total_amount.data,
            'created_date': form.created_date.data,
            'company_id': form.company_id.data,
            'owner_id': form.deal_owner_id.data
        }
        # Use the manager to create the deal
        try:
            new_deal = DealDatabaseManager.create_deal(deal_data)
            flash('Deal created successfully', 'success')
            # Redirect to the page for the newly created deal
            return redirect(url_for('deals.view_deal', deal_id=new_deal.id))
        except Exception as e:
            flash(f"Error creating deal: {e}", 'danger')
    else:
        # If validation fails, flash the errors and redirect back to the main page
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {getattr(form, field).label.text}: {error}", 'danger')

    return redirect(url_for('deals.list_deals'))


@deals_bp.route('/deals/<int:deal_id>')
def view_deal(deal_id):
    """Displays a page for a single, specific deal."""
    # Use the manager to fetch the deal by its ID
    deal = DealDatabaseManager.get_deal_by_id(deal_id)
    if not deal:
        flash("Deal not found.", "danger")
        return redirect(url_for('deals.list_deals'))
        
    # The template can now access all related data via the deal object, e.g., deal.quotes
    return render_template('deals/individual_deal_page.html', deal=deal)

@deals_bp.route('/deals/<int:deal_id>/update_stage', methods=['POST'])
def update_deal_stage(deal_id):
    """API endpoint to update a deal's stage."""
    # This route is intended to be called by JavaScript
    new_stage_str = request.json.get('new_stage')
    try:
        # Convert the string from the request into a DealStage enum member
        new_stage = DealStage[new_stage_str]
        DealDatabaseManager.update_deal_stage(deal_id, new_stage)
        return jsonify({"status": "success", "message": "Stage updated successfully."})
    except KeyError:
        return jsonify({"status": "error", "message": "Invalid stage value."}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# --- API Endpoints for Search Modals (from our previous plan) ---

@deals_bp.route('/api/search/companies')
def search_companies():
    """API endpoint to search for companies by name."""
    search_term = request.args.get('q', '').strip()
    if not search_term or len(search_term) < 2:
        return jsonify([])

    companies = Company.query.filter(Company.company_name.ilike(f'%{search_term}%')).limit(10).all()
    results = [{'id': company.id, 'text': company.company_name} for company in companies]
    return jsonify(results)


@deals_bp.route('/api/search/contacts')
def search_contacts():
    """API endpoint to search for contacts (customers) by name."""
    search_term = request.args.get('q', '').strip()
    if not search_term or len(search_term) < 2:
        return jsonify([])

    contacts = Customer.query.filter(Customer.name.ilike(f'%{search_term}%')).limit(10).all()
    results = [{'id': contact.id, 'text': f"{contact.name} ({contact.company.company_name})"} for contact in contacts]
    return jsonify(results)


@deals_bp.route('/api/search/deal_owners')
def search_deal_owners():
    """API endpoint to search for deal owners (users) by username."""
    search_term = request.args.get('q', '').strip()
    if not search_term or len(search_term) < 2:
        return jsonify([])
    
    users = User.query.filter(User.username.ilike(f'%{search_term}%')).limit(10).all()
    results = [{'id': user.id, 'text': user.username} for user in users]
    return jsonify(results)