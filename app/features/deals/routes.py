from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required
from app.models import (
    Deal, Quote, QuoteLineItem, DealStage, AustralianState, DealType, 
    Company, Contact, User
)
from .forms import (
    DealForm, QuoteForm, QuoteLineItemForm, DealCustomerForm, 
    DealStageUpdateForm, QuoteRevisionForm
)
from app.extensions import db
from app.core.core_logging import logger
from collections import defaultdict

from . import deals_bp


@deals_bp.route('/')
def list_deals():
    """Display a list of all deals, grouped by stage."""
    deals = Deal.query.order_by(Deal.created_at.desc()).all()
    
    deals_by_stage = defaultdict(list)
    for deal in deals:
        deals_by_stage[deal.stage.value].append(deal)
        
    # Create an empty form instance to pass to the template
    form = DealForm()
        
    return render_template(
        'deals/deals.html', 
        deals_by_stage=deals_by_stage, 
        deal_stages=[stage.value for stage in DealStage],
        # Pass the form object to the template
        form=form
    )


@deals_bp.route('/<int:deal_id>')
#@login_required
def deal_details(deal_id):
    """Display the details of a single deal."""
    deal = Deal.query.get_or_404(deal_id)
    return render_template('deals/individual_deal_page.html', deal=deal)


@deals_bp.route('/create', methods=['GET', 'POST'])
#@login_required
def create_deal():
    """Create a new deal."""
    form = DealForm()
    if form.validate_on_submit():
        try:
            new_deal = Deal()
            form.populate_obj(new_deal)
            db.session.add(new_deal)
            db.session.commit()
            flash('Deal created successfully!', 'success')
            return redirect(url_for('deals.list_deals'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating deal: {e}")
            flash('An error occurred while creating the deal.', 'error')
            
    # This view already correctly handles the form for the modal
    return render_template('deals/create_deal_panel.html', form=form)


@deals_bp.route('/search/modal', methods=['GET'])
#@login_required
def search_modal_data():
    """
    Provide data for search modals.
    """
    search_type = request.args.get('type')
    query = request.args.get('q', '')
    
    results = []
    
    if search_type == 'company':
        companies = Company.query.filter(Company.company_name.ilike(f'%{query}%')).limit(10).all()
        results = [{'id': c.id, 'text': c.company_name} for c in companies]
        
    elif search_type == 'contact':
        contacts = Contact.query.filter(Contact.name.ilike(f'%{query}%')).limit(10).all()
        results = [{'id': c.id, 'text': f"{c.name} ({c.company.company_name})"} for c in contacts]

    elif search_type == 'deal_owner':
        users = User.query.filter(User.username.ilike(f'%{query}%')).limit(10).all()
        results = [{'id': u.id, 'text': u.username} for u in users]
        
    return jsonify(results)