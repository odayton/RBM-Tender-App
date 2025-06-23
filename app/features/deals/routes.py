from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required
from collections import defaultdict
import datetime

from app.models import (
    Deal, User, Quote, QuoteLineItem, DealStage, AustralianState, DealType, 
    Company, Contact
)
# We only need the DealForm for this part of the refactoring
from .forms import DealForm
from app.extensions import db
from app.core.core_logging import logger

from . import deals_bp


@deals_bp.route('/', methods=['GET'])
#@login_required
def list_deals():
    """Display a list of all deals, grouped by stage, in a Kanban-style board."""
    form = DealForm()  # The form for the "Create" modal
    deals = Deal.query.order_by(Deal.created_at.desc()).all()
    
    deals_by_stage = defaultdict(list)
    for deal in deals:
        deals_by_stage[deal.stage.value].append(deal)
        
    stats = {
        'total_deal_amount': sum(d.total_amount for d in deals if d.total_amount is not None),
        'avg_deal_amount': 0,
        'deal_count': len(deals)
    }
    if deals:
        stats['avg_deal_amount'] = stats['total_deal_amount'] / len(deals) if len(deals) > 0 else 0
        
    return render_template(
        'deals/deals.html', 
        deals_by_stage=deals_by_stage, 
        deal_stages=[stage.value for stage in DealStage],
        stats=stats,
        form=form
    )


@deals_bp.route('/<int:deal_id>')
#@login_required
def deal_details(deal_id):
    """Display the details of a single deal."""
    deal = Deal.query.get_or_404(deal_id)
    return render_template('deals/individual_deal_page.html', deal=deal)


@deals_bp.route('/create', methods=['POST'])
#@login_required
def create_deal():
    """Endpoint for creating a new deal from our refactored form."""
    form = DealForm()
    if form.validate_on_submit():
        try:
            # Find the default owner "Owen" for development
            owner = User.query.filter_by(username="Owen").first()
            if not owner:
                # Fallback if "Owen" is not found, to prevent errors
                flash('Default owner "Owen" not found in database. Please create this user.', 'error')
                return redirect(url_for('deals.list_deals'))

            new_deal = Deal(
                project_name=form.project_name.data,
                deal_type=DealType[form.deal_type.data],
                state=AustralianState[form.state.data],
                contact_id=form.contact_id.data,
                company_id=form.company_id.data,
                # --- Automatically set owner and stage ---
                owner_id=owner.id,
                stage=DealStage.SALES_LEAD # All new deals start as a Sales Lead
            )
            
            # If a contact is selected, ensure the deal is also linked to that contact's company
            if new_deal.contact_id and not new_deal.company_id:
                contact = Contact.query.get(new_deal.contact_id)
                if contact:
                    new_deal.company_id = contact.company_id
            
            db.session.add(new_deal)
            db.session.commit()
            flash('Deal created successfully!', 'success')

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating deal: {e}")
            flash(f'An error occurred while creating the deal: {e}', 'error')
    else:
        # If the form has validation errors, flash them to the user
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {getattr(form, field).label.text}: {error}", 'error')

    return redirect(url_for('deals.list_deals'))


@deals_bp.route('/update_stage/<int:deal_id>', methods=['POST'])
#@login_required
def update_deal_stage(deal_id):
    """Update the stage of a deal, called from drag-and-drop."""
    deal = Deal.query.get_or_404(deal_id)
    data = request.get_json()
    new_stage_value = data.get('stage')

    if not new_stage_value:
        return jsonify({'success': False, 'error': 'New stage not provided'}), 400

    try:
        new_stage_enum = DealStage(new_stage_value)
        deal.stage = new_stage_enum
        db.session.commit()
        logger.info(f"Deal {deal.id} stage updated to {new_stage_enum.value}")
        return jsonify({'success': True})
    except ValueError:
        return jsonify({'success': False, 'error': f"Invalid stage value: {new_stage_value}"}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating deal stage for deal {deal.id}: {e}")
        return jsonify({'success': False, 'error': 'An internal error occurred'}), 500


@deals_bp.route('/search/modal', methods=['GET'])
#@login_required
def search_modal_data():
    """Provide data for search modals."""
    search_type = request.args.get('type')
    query = request.args.get('q', '')
    results = []
    
    if search_type == 'company':
        companies = Company.query.filter(Company.name.ilike(f'%{query}%')).limit(10).all()
        results = [{'id': c.id, 'text': c.name} for c in companies]
    elif search_type == 'contact':
        contacts = Contact.query.filter(Contact.name.ilike(f'%{query}%')).limit(10).all()
        results = [{'id': c.id, 'text': f"{c.name} ({c.company.name})"} for c in contacts]
    elif search_type == 'deal_owner':
        users = User.query.filter(User.username.ilike(f'%{query}%')).limit(10).all()
        results = [{'id': u.id, 'text': u.username} for u in users]
        
    return jsonify(results)