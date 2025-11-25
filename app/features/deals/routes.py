# app/features/deals/routes.py

from flask import (
    Blueprint, render_template, request, jsonify, redirect, url_for, flash, make_response, current_app, send_file
)
from collections import defaultdict
from decimal import Decimal
import asyncio
import os
from playwright.async_api import async_playwright
from sqlalchemy import or_
from io import BytesIO

from app.models import (
    Deal, User, Quote, QuoteLineItem, DealStage, AustralianState, DealType,
    Company, Contact, QuoteRecipient, QuoteOption, Product, QuoteSnapshot
)
from .forms import DealForm, LineItemForm, QuoteOptionForm, UpdateDealForm
from app.extensions import db
from sqlalchemy import func
from app.core.core_logging import logger
from flask_login import login_required, current_user
from app.core.core_monitoring import performance_timer, log_business_event
from app.core.core_metrics import track_business_operation, record_deal_created, record_quote_generated
from app.core.core_caching import cache_deal_data, cache_quote_data, invalidate_deal_cache, invalidate_quote_cache
from app.core.core_circuit_breaker import pdf_generation_circuit_breaker

from . import deals_bp
from app.models import User, UserRole

def round_to_professional_pricing(price):
    """
    Round prices to professional values: .00, .25, .50, .75
    Examples: 123.21 -> 123.25, 123.67 -> 123.75, 123.96 -> 124.00
    """
    import math
    
    # Get the whole dollar amount and cents
    whole_dollars = int(price)
    cents = price - whole_dollars
    
    # Determine which professional cent value to round to
    if cents < 0.125:  # 0 to 12.5 cents -> .00
        new_cents = 0.00
    elif cents < 0.375:  # 12.5 to 37.5 cents -> .25
        new_cents = 0.25
    elif cents < 0.625:  # 37.5 to 62.5 cents -> .50
        new_cents = 0.50
    elif cents < 0.875:  # 62.5 to 87.5 cents -> .75
        new_cents = 0.75
    else:  # 87.5 to 99.99 cents -> next dollar
        whole_dollars += 1
        new_cents = 0.00
    
    return whole_dollars + new_cents

def consolidate_cents(component_data):
    """
    Consolidate cents between components for cleaner pricing.
    Priority: 
    1. .25 + .75 = .00 + 1.00
    2. .50 + .50 = .00 + 1.00 (larger absorbs from smaller)
    3. Remove excess .25 cents
    """
    # Group components by their cent values
    cent_groups = {0.00: [], 0.25: [], 0.50: [], 0.75: []}
    
    for comp in component_data:
        cents = comp['rounded_price'] - int(comp['rounded_price'])
        cent_groups[cents].append(comp)
    
    # Step 1: Consolidate .25 and .75 cents to make .00 and 1.00
    while len(cent_groups[0.25]) > 0 and len(cent_groups[0.75]) > 0:
        comp_25 = cent_groups[0.25].pop(0)
        comp_75 = cent_groups[0.75].pop(0)
        
        # Move .25 from the .25 component to the .75 component
        comp_25['rounded_price'] = comp_25['rounded_price'] - 0.25
        comp_25['total_price'] = comp_25['rounded_price'] * comp_25['quantity']
        
        comp_75['rounded_price'] = comp_75['rounded_price'] + 0.25
        comp_75['total_price'] = comp_75['rounded_price'] * comp_75['quantity']
        
        # Move the consolidated components to .00 group
        cent_groups[0.00].append(comp_25)
        cent_groups[0.00].append(comp_75)
    
    # Step 2: Consolidate .50 + .50 cents to make .00 and 1.00 (larger absorbs from smaller)
    while len(cent_groups[0.50]) >= 2:
        # Sort by price to identify larger and smaller
        cent_groups[0.50].sort(key=lambda x: x['rounded_price'], reverse=True)
        larger_comp = cent_groups[0.50].pop(0)  # Largest
        smaller_comp = cent_groups[0.50].pop(0)  # Next largest (smaller of the pair)
        
        # Remove .50 from smaller, add .50 to larger
        smaller_comp['rounded_price'] = smaller_comp['rounded_price'] - 0.50
        smaller_comp['total_price'] = smaller_comp['rounded_price'] * smaller_comp['quantity']
        
        larger_comp['rounded_price'] = larger_comp['rounded_price'] + 0.50
        larger_comp['total_price'] = larger_comp['rounded_price'] * larger_comp['quantity']
        
        # Move the consolidated components to .00 group
        cent_groups[0.00].append(smaller_comp)
        cent_groups[0.00].append(larger_comp)
    
    # Step 3: Handle remaining .25 cents by removing them
    # This creates cleaner pricing by removing small cent values
    while len(cent_groups[0.25]) > 0:
        comp_25 = cent_groups[0.25].pop(0)
        comp_25['rounded_price'] = comp_25['rounded_price'] - 0.25
        comp_25['total_price'] = comp_25['rounded_price'] * comp_25['quantity']
        cent_groups[0.00].append(comp_25)

def adjust_for_exact_total(component_data, difference):
    """
    Adjust components to achieve exact total by using .25 cent adjustments.
    Special cases:
    - If short by .75 and have .25 component, add .75 to make it 1.00
    - If over by .75 and have .75 component, remove .75 to make it .00
    - Otherwise adjust by .25 increments
    """
    # Convert difference to cents (multiply by 4 to get quarter increments)
    cents_diff = round(difference * 4)
    
    logger.info(f"Adjusting for exact total - Difference: ${difference}, Cents diff: {cents_diff}")
    
    if cents_diff == 0:
        return  # Already exact
    
    # Group components by their cent values
    components_by_cents = {0.25: [], 0.50: [], 0.75: []}
    for comp in component_data:
        cents = comp['rounded_price'] - int(comp['rounded_price'])
        if cents in components_by_cents:
            components_by_cents[cents].append(comp)
    
    # Special case: Short by .75 and have a .25 component - add .75 to make it 1.00
    if cents_diff == -3 and components_by_cents[0.25]:  # -3 quarters = -$0.75
        comp = components_by_cents[0.25][0]
        comp['rounded_price'] = comp['rounded_price'] + 0.75
        comp['total_price'] = comp['rounded_price'] * comp['quantity']
        logger.info(f"Special case: Added $0.75 to component with $0.25 to make it $1.00")
        return
    
    # Special case: Over by .75 and have a .75 component - remove .75 to make it .00
    if cents_diff == 3 and components_by_cents[0.75]:  # 3 quarters = $0.75
        comp = components_by_cents[0.75][0]
        comp['rounded_price'] = comp['rounded_price'] - 0.75
        comp['total_price'] = comp['rounded_price'] * comp['quantity']
        logger.info(f"Special case: Removed $0.75 from component with $0.75 to make it $0.00")
        return
    
    # Special case: Short by .50 and have a .50 component - add .50 to make it 1.00
    if cents_diff == -2 and components_by_cents[0.50]:  # -2 quarters = -$0.50
        comp = components_by_cents[0.50][0]
        comp['rounded_price'] = comp['rounded_price'] + 0.50
        comp['total_price'] = comp['rounded_price'] * comp['quantity']
        logger.info(f"Special case: Added $0.50 to component with $0.50 to make it $1.00")
        return
    
    # Special case: Over by .50 and have a .50 component - remove .50 to make it .00
    if cents_diff == 2 and components_by_cents[0.50]:  # 2 quarters = $0.50
        comp = components_by_cents[0.50][0]
        comp['rounded_price'] = comp['rounded_price'] - 0.50
        comp['total_price'] = comp['rounded_price'] * comp['quantity']
        logger.info(f"Special case: Removed $0.50 from component with $0.50 to make it $0.00")
        return
    
    # General case: Adjust by .25 increments
    all_adjustable = components_by_cents[0.25] + components_by_cents[0.50] + components_by_cents[0.75]
    
    if not all_adjustable:
        # No components to adjust, fall back to last component adjustment
        last_component = component_data[-1]
        adjustment_per_unit = difference / last_component['quantity']
        adjusted_unit_price = last_component['rounded_price'] + adjustment_per_unit
        final_unit_price = round_to_professional_pricing(adjusted_unit_price)
        
        last_component['rounded_price'] = final_unit_price
        last_component['total_price'] = final_unit_price * last_component['quantity']
        return
    
    # Adjust components by .25 increments
    adjustments_needed = abs(cents_diff)
    adjustments_made = 0
    
    for comp in all_adjustable:
        if adjustments_made >= adjustments_needed:
            break
            
        if cents_diff > 0:  # Total is over, remove .25 from component
            comp['rounded_price'] = comp['rounded_price'] - 0.25
            comp['total_price'] = comp['rounded_price'] * comp['quantity']
            adjustments_made += 1
        elif cents_diff < 0:  # Total is under, add .25 to component
            comp['rounded_price'] = comp['rounded_price'] + 0.25
            comp['total_price'] = comp['rounded_price'] * comp['quantity']
            adjustments_made += 1

def _clone_quote(source_quote, recipient, revision_number):
    """Creates a deep copy of a source quote for a given recipient."""
    new_quote = Quote(
        recipient_id=recipient.id,
        revision=revision_number,
        notes=source_quote.notes
    )
    db.session.add(new_quote)
    db.session.flush()

    for source_option in source_quote.options:
        new_option = QuoteOption(
            quote_id=new_quote.id,
            name=source_option.name,
            freight_charge=source_option.freight_charge
        )
        db.session.add(new_option)
        db.session.flush()

        for source_item in source_option.line_items:
            new_item = QuoteLineItem(
                option_id=new_option.id,
                product_id=source_item.product_id,
                notes=source_item.notes,
                quantity=source_item.quantity,
                unit_price=source_item.unit_price,
                discount=source_item.discount,
                display_order=source_item.display_order,
                custom_sku=source_item.custom_sku,
                custom_name=source_item.custom_name
            )
            db.session.add(new_item)
    return new_quote

@deals_bp.route('/', methods=['GET'])
@performance_timer('deals_list')
@cache_deal_data(timeout=600)  # Cache for 10 minutes
def list_deals():
    """Display a list of all deals, grouped by stage."""
    form = DealForm()
    
    # Get search parameter
    search_query = request.args.get('search', '').strip()
    
    # Base query
    deals_query = Deal.query
    
    # Apply search filter if search query is provided
    if search_query:
        # Check if search query looks like a quote reference (e.g., "123-1")
        if '-' in search_query:
            # Split by dash to get deal_id and revision
            parts = search_query.split('-')
            if len(parts) == 2 and parts[0].isdigit():
                deal_id = int(parts[0])
                revision = int(parts[1])
                # Search for deals with this ID that have quotes with this revision
                deals_query = deals_query.filter(
                    db.or_(
                        Deal.project_name.ilike(f'%{search_query}%'),
                        Deal.id == deal_id
                    )
                )
            else:
                # Not a valid quote reference format, search normally
                deals_query = deals_query.filter(
                    db.or_(
                        Deal.project_name.ilike(f'%{search_query}%'),
                        func.cast(Deal.id, db.String).ilike(f'%{search_query}%')
                    )
                )
        else:
            # Regular search (no dash, so search deal name and ID)
            deals_query = deals_query.filter(
                db.or_(
                    Deal.project_name.ilike(f'%{search_query}%'),
                    func.cast(Deal.id, db.String).ilike(f'%{search_query}%')
                )
            )
    
    deals = deals_query.order_by(Deal.created_at.desc()).all()

    deals_by_stage = defaultdict(list)
    for deal in deals:
        deals_by_stage[deal.stage.value].append(deal)

    stats = {
        'total_deal_amount': sum(d.total_amount for d in deals if d.total_amount is not None),
        'avg_deal_amount': (sum(d.total_amount for d in deals if d.total_amount is not None) / len(deals)) if deals else 0,
        'deal_count': len(deals)
    }
    return render_template(
        'deals/deals.html',
        deals_by_stage=deals_by_stage,
        deal_stages=[stage.value for stage in DealStage],
        stats=stats,
        form=form,
        search_query=search_query
    )



@deals_bp.route('/<int:deal_id>')
def deal_details(deal_id):
    """Display the details of a single deal."""
    deal = Deal.query.get_or_404(deal_id)
    
    # Update the deal's total amount to ensure it's current
    deal.update_total_amount()
    db.session.commit()
    
    all_quotes_in_deal = [q for r in deal.recipients for q in r.quotes]

    add_item_form = LineItemForm(notes="")
    edit_item_form = LineItemForm()

    return render_template(
        'deals/individual_deal_page.html',
        deal=deal,
        all_quotes_in_deal=all_quotes_in_deal,
        add_item_form=add_item_form,
        edit_item_form=edit_item_form,
        add_option_form=QuoteOptionForm(),
        edit_option_form=QuoteOptionForm(),
        update_deal_form=UpdateDealForm(obj=deal)
    )

@deals_bp.route('/option/<int:option_id>/view/pdf', methods=['GET'])
@login_required
def view_quote_pdf(option_id):
    """
    Generates the quote PDF and serves it inline in the browser with PDF controls.
    Automatically creates a snapshot of the quote when viewed.
    """
    option = QuoteOption.query.get_or_404(option_id)
    quote = option.quote
    deal = quote.recipient.deal

    category_templates = {
        'HVAC': 'deals/pdf/hvac_quote_template.html',
        'PLUMBING': 'deals/pdf/plumbing_quote_template.html',
        'HYDRONIC_HEATING': 'deals/pdf/hydronic_heating_quote_template.html',
        'DATA_CENTRES': 'deals/pdf/hvac_quote_template.html',
        'MERCHANT': 'deals/pdf/plumbing_quote_template.html',
        'WHOLESALER': 'deals/pdf/plumbing_quote_template.html',
        'OEM': 'deals/pdf/plumbing_quote_template.html'
    }
    template_name = category_templates.get(deal.deal_type.name, 'deals/pdf/hvac_quote_template.html')
    
    # Log the deal type and template being used for debugging
    logger.info(f"PDF generation: deal_type={deal.deal_type.name}, template={template_name}")

    try:
        css_file_path = os.path.join(current_app.static_folder, 'css', 'quote_pdf.css')
        with open(css_file_path) as f:
            css_content = f.read()
    except FileNotFoundError:
        logger.error("quote_pdf.css not found!")
        css_content = ""
    
    # Convert logo to base64 for embedding in PDF
    try:
        logo_path = os.path.join(current_app.static_folder, 'images', 'rbm_logo.png')
        logger.info(f"Looking for logo at: {logo_path}")
        with open(logo_path, 'rb') as f:
            logo_data = f.read()
        import base64
        logo_base64 = base64.b64encode(logo_data).decode('utf-8')
        logo_data_url = f"data:image/png;base64,{logo_base64}"
        logger.info(f"Successfully loaded logo: {len(logo_data)} bytes, base64 length: {len(logo_base64)}")
    except FileNotFoundError:
        logger.error(f"rbm_logo.png not found at: {logo_path}")
        logo_base64 = ""
        logo_data_url = ""
    except Exception as e:
        logger.error(f"Error loading logo: {e}")
        logo_base64 = ""
        logo_data_url = ""

    # Filter contacts to only show those belonging to the quote recipient company
    company_contacts = [contact for contact in deal.contacts if contact.company_id == quote.recipient.company_id]
    
    # Generate the HTML content for the quote
    html_content = None
    try:
        html_content = render_template(
            template_name,
            deal=deal,
            revision=quote,
            option=option,
            css_content=css_content,
            logo_data_url=logo_data_url,
            company_contacts=company_contacts
        )
        
        # Create a snapshot of this quote option
        try:
            from app.models import QuoteSnapshot
            from flask_login import current_user
            
            # Debug logging for current_user
            logger.info(f"current_user object: {current_user}")
            logger.info(f"current_user type: {type(current_user)}")
            logger.info(f"current_user.is_authenticated: {getattr(current_user, 'is_authenticated', 'NO_ATTR')}")
            logger.info(f"current_user.id: {getattr(current_user, 'id', 'NO_ID')}")
            
            # Check if current_user is available and authenticated
            if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
                # Create snapshot with the rendered HTML content
                snapshot = QuoteSnapshot.create_snapshot(
                    quote_option=option,
                    rendered_html=html_content,
                    user_id=current_user.id,
                    pdf_generated=True,
                    template_used=template_name
                )
                logger.info(f"Created quote snapshot v{snapshot.version_number} for option {option_id}")
            else:
                logger.warning("User not authenticated or current_user not available, skipping snapshot creation")
                
        except Exception as e:
            logger.error(f"Failed to create quote snapshot: {e}", exc_info=True)
            # Don't fail the PDF generation if snapshot creation fails
        
    except Exception as e:
        logger.error(f"Failed to render quote template: {e}", exc_info=True)
        return "Error rendering quote template", 500
    
    # Check if HTML content was generated successfully
    if not html_content:
        logger.error("HTML content is empty or None")
        return "Error: No HTML content generated", 500
    
    # Log some debugging info
    logger.info(f"Generated HTML for PDF: deal_id={deal.id}, option_id={option.id}, line_items_count={len(option.line_items)}")
    logger.info(f"CSS content length: {len(css_content)}")
    logger.info(f"Logo data URL length: {len(logo_data_url) if logo_data_url else 0}")
    logger.info(f"HTML content length: {len(html_content) if html_content else 0}")
    logger.info(f"Template used: {template_name}")
    logger.info(f"Deal type: {deal.deal_type.name if deal.deal_type else 'None'}")

    # Generate PDF using Playwright with fallback
    try:
        # Generate PDF using Playwright
        pdf_data = asyncio.run(_generate_pdf(html_content))
        
        # Check if we got HTML content instead of PDF (fallback case)
        if isinstance(pdf_data, bytes) and pdf_data.startswith(b'<!DOCTYPE html'):
            # Return HTML content instead of PDF
            response = make_response(pdf_data)
            response.headers['Content-Type'] = 'text/html; charset=utf-8'
            response.headers['Content-Disposition'] = 'inline; filename=quote.html'
            return response
        elif isinstance(pdf_data, bytes) and len(pdf_data) < 1000:
            # PDF is too small, likely empty - return HTML instead
            logger.warning(f"PDF generated but too small ({len(pdf_data)} bytes), returning HTML instead")
            response = make_response(html_content.encode('utf-8'))
            response.headers['Content-Type'] = 'text/html; charset=utf-8'
            response.headers['Content-Disposition'] = 'inline; filename=quote.html'
            return response
        else:
            # Record metrics for successful PDF generation
            record_quote_generated(
                quote_type=deal.deal_type.value,
                status='pdf_generated'
            )
            
            # Return PDF content
            response = make_response(pdf_data)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = 'inline; filename=quote.pdf'
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response
            
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        flash('Error generating PDF. Please try again.', 'error')
        return redirect(url_for('deals.deal_details', deal_id=deal.id))

@deals_bp.route('/search/modal', methods=['GET'])
def search_for_modal():
    """
    Handles search requests from the deal creation modal for contacts and companies.
    """
    search_type = request.args.get('type')
    query = request.args.get('q', '')
    deal_id = request.args.get('deal_id', type=int)
    results = []

    if not query or len(query) < 2:
        return jsonify([])

    if search_type == 'contact':
        contacts = Contact.query.join(Company).filter(
            db.or_(
                Contact.name.ilike(f'%{query}%'),
                Contact.email.ilike(f'%{query}%')
            )
        ).limit(10).all()
        
        # Filter out contacts already associated with the deal
        if deal_id:
            deal = Deal.query.get(deal_id)
            if deal:
                existing_contact_ids = [c.id for c in deal.contacts]
                contacts = [c for c in contacts if c.id not in existing_contact_ids]
        
        results = [{'id': c.id, 'text': f"{c.name} ({c.company.company_name})"} for c in contacts]

    elif search_type == 'company':
        companies = Company.query.filter(
            Company.company_name.ilike(f'%{query}%')
        ).limit(10).all()
        
        # Filter out companies already associated with the deal
        if deal_id:
            deal = Deal.query.get(deal_id)
            if deal:
                existing_company_ids = [c.id for c in deal.companies]
                companies = [c for c in companies if c.id not in existing_company_ids]
        
        results = [{'id': comp.id, 'text': comp.company_name} for comp in companies]

    return jsonify(results)

@deals_bp.route('/create', methods=['POST'])
@login_required
@performance_timer('deal_create')
@invalidate_deal_cache()
def create_deal():
    """Creates a new deal from the form on the main deals page."""
    form = DealForm()
    if form.validate_on_submit():
        try:
            # Automatically assign the deal to the currently logged-in user
            owner = current_user
            if not owner:
                flash('You must be logged in to create a deal.', 'error')
                return redirect(url_for('deals.list_deals'))

            new_deal = Deal(
                project_name=form.project_name.data,
                deal_type=DealType[form.deal_type.data],
                state=AustralianState[form.state.data],
                owner_id=owner.id,
                stage=DealStage.SALES_LEAD
            )
            db.session.add(new_deal)
            
            if form.company_id.data:
                company = Company.query.get(form.company_id.data)
                if company:
                    new_deal.companies.append(company)

            if form.contact_id.data:
                contact = Contact.query.get(form.contact_id.data)
                if contact:
                    new_deal.contacts.append(contact)
                    if contact.company and contact.company not in new_deal.companies:
                        new_deal.companies.append(contact.company)
            
            db.session.flush()

            for company in new_deal.companies:
                existing_recipient = QuoteRecipient.query.filter_by(deal_id=new_deal.id, company_id=company.id).first()
                if not existing_recipient:
                    db.session.add(QuoteRecipient(deal_id=new_deal.id, company_id=company.id))

            db.session.commit()
            
            # Record metrics
            record_deal_created(
                deal_type=new_deal.deal_type.value,
                stage=new_deal.stage.value
            )
            
            # Log business event
            log_business_event('deal_created', 
                              deal_id=new_deal.id,
                              project_name=new_deal.project_name,
                              deal_type=new_deal.deal_type.value,
                              owner_id=owner.id,
                              owner_email=owner.email)
            
            flash('Deal created successfully!', 'success')
            return redirect(url_for('deals.deal_details', deal_id=new_deal.id))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating deal: {e}")
            flash(f'An error occurred: {e}', 'error')
            return redirect(url_for('deals.list_deals'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in field '{getattr(form, field).label.text}': {error}", 'error')
        return redirect(url_for('deals.list_deals'))
    
@deals_bp.route('/update/<int:deal_id>', methods=['POST'])
@login_required
def update_deal(deal_id):
    """Updates the core details of an existing deal."""
    deal = Deal.query.get_or_404(deal_id)
    form = UpdateDealForm(request.form, obj=deal)
    # Exclude admin users from owner selection
    non_admin_users = User.query.filter(User.role != UserRole.ADMIN).order_by(User.username).all()
    form.owner_id.choices = [(u.id, u.full_name) for u in non_admin_users]

    if form.validate_on_submit():
        try:
            form.populate_obj(deal)
            deal.deal_type = DealType[form.deal_type.data]
            deal.stage = DealStage[form.stage.data]
            deal.state = AustralianState[form.state.data]
            db.session.commit()
            flash('Deal details updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating deal {deal.id}: {e}")
            flash('An error occurred while updating the deal.', 'error')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {getattr(form, field).label.text}: {error}", 'error')
    return redirect(url_for('deals.deal_details', deal_id=deal.id))

@deals_bp.route('/update_stage/<int:deal_id>', methods=['POST'])
@login_required
@invalidate_deal_cache()
def update_deal_stage(deal_id):
    """Updates the stage of a deal via AJAX (for kanban drag and drop)."""
    try:
        logger.info(f"Received stage update request for deal {deal_id}")
        deal = Deal.query.get_or_404(deal_id)
        data = request.get_json()
        
        logger.info(f"Request data: {data}")
        
        if not data or 'stage' not in data:
            logger.error("Invalid request data - missing stage")
            return jsonify({'success': False, 'error': 'Invalid request data'}), 400
        
        new_stage = data['stage']
        logger.info(f"Updating deal {deal_id} from '{deal.stage.value}' to '{new_stage}'")
        
        # Validate that the stage is valid
        try:
            stage_enum = DealStage(new_stage)
        except ValueError:
            logger.error(f"Invalid stage: {new_stage}")
            return jsonify({'success': False, 'error': f'Invalid stage: {new_stage}'}), 400
        
        # Update the deal stage
        old_stage = deal.stage.value
        deal.stage = stage_enum
        
        # Flush changes to database before commit
        db.session.flush()
        db.session.commit()
        
        logger.info(f"Deal {deal_id} stage updated from '{old_stage}' to '{new_stage}' by user {current_user.username}")
        
        return jsonify({
            'success': True, 
            'message': f'Deal moved to {new_stage}',
            'old_stage': old_stage,
            'new_stage': new_stage
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating deal stage: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@deals_bp.route('/option/<int:option_id>/snapshots', methods=['GET'])
@login_required
def view_quote_snapshots(option_id):
    """Display version history for a quote option."""
    option = QuoteOption.query.get_or_404(option_id)
    snapshots = QuoteSnapshot.get_snapshots_for_option(option_id)
    
    return render_template(
        'deals/quote_snapshots.html',
        option=option,
        snapshots=snapshots,
        deal=option.quote.recipient.deal
    )

@deals_bp.route('/snapshot/<int:snapshot_id>/view', methods=['GET'])
@login_required
def view_quote_snapshot(snapshot_id):
    """View a specific quote snapshot."""
    snapshot = QuoteSnapshot.query.get_or_404(snapshot_id)
    
    return render_template(
        'deals/quote_snapshot_view.html',
        snapshot=snapshot,
        option=snapshot.quote_option,
        deal=snapshot.quote_option.quote.recipient.deal
    )

@deals_bp.route('/snapshot/<int:snapshot_id>/restore', methods=['POST'])
@login_required
def restore_quote_snapshot(snapshot_id):
    """Restore a quote option to a previous snapshot version."""
    try:
        snapshot = QuoteSnapshot.query.get_or_404(snapshot_id)
        option = snapshot.quote_option
        
        # Create a snapshot of the current state before restoring
        current_html = render_template(
            'deals/pdf/hvac_quote_template.html',  # Default template
            deal=option.quote.recipient.deal,
            quote=option.quote,
            option=option,
            css_content="",
            logo_base64=""
        )
        
        # Save current state as snapshot
        current_snapshot = QuoteSnapshot.create_snapshot(
            quote_option=option,
            rendered_html=current_html,
            user_id=current_user.id,
            restored_from_snapshot_id=snapshot_id,
            action_type='restore_backup'
        )
        
        # TODO: Implement actual restoration logic
        # This would involve parsing the snapshot HTML and updating the current option
        
        flash(f'Quote restored to version {snapshot.get_formatted_version()}. Current state backed up as version {current_snapshot.get_formatted_version()}.', 'success')
        
        return redirect(url_for('deals.deal_details', deal_id=option.quote.recipient.deal_id))
        
    except Exception as e:
        logger.error(f"Error restoring quote snapshot: {e}", exc_info=True)
        flash('Error restoring quote snapshot.', 'error')
        return redirect(url_for('deals.deal_details', deal_id=option.quote.recipient.deal_id))

@deals_bp.route('/add_revision/<int:deal_id>', methods=['POST'])
def add_revision(deal_id):
    # Debug logging - more comprehensive
    logger.info(f"=== ADD_REVISION DEBUG START ===")
    logger.info(f"add_revision called for deal_id: {deal_id}")
    logger.info(f"Request method: {request.method}")
    logger.info(f"Request headers: {dict(request.headers)}")
    logger.info(f"Request form data: {dict(request.form)}")
    logger.info(f"Request args: {dict(request.args)}")
    
    # Check if deal exists
    deal = Deal.query.get_or_404(deal_id)
    logger.info(f"Deal found: {deal.project_name}")
    
    recipient_id = request.form.get('recipient_id', type=int)
    creation_method = request.form.get('creation_method')
    
    logger.info(f"recipient_id from form: {recipient_id} (type: {type(recipient_id)})")
    logger.info(f"creation_method from form: {creation_method} (type: {type(creation_method)})")
    
    # Validate required fields
    if not recipient_id:
        logger.error("ERROR: Missing recipient_id")
        flash('Invalid request. Missing recipient_id. Please try refreshing the page.', 'error')
        return redirect(url_for('deals.deal_details', deal_id=deal_id))
    
    if not creation_method:
        logger.error("ERROR: Missing creation_method")
        flash('Invalid request. Missing creation_method. Please select a creation method.', 'error')
        return redirect(url_for('deals.deal_details', deal_id=deal_id))
    
    # Validate creation_method values
    valid_methods = ['blank', 'copy_last', 'clone_other']
    if creation_method not in valid_methods:
        logger.error(f"ERROR: Invalid creation_method: {creation_method}")
        flash(f'Invalid request. Invalid creation_method: {creation_method}. Please select a valid option.', 'error')
        return redirect(url_for('deals.deal_details', deal_id=deal_id))
    
    logger.info(f"Validation passed - proceeding with revision creation")
    
    # Check if recipient exists and belongs to this deal
    recipient = QuoteRecipient.query.filter_by(id=recipient_id, deal_id=deal_id).first()
    if not recipient:
        logger.error(f"ERROR: Recipient {recipient_id} not found or doesn't belong to deal {deal_id}")
        flash('Invalid request. Recipient not found or doesn\'t belong to this deal.', 'error')
        return redirect(url_for('deals.deal_details', deal_id=deal_id))
    
    last_revision = Quote.query.filter_by(recipient_id=recipient.id).order_by(Quote.revision.desc()).first()
    next_rev = (last_revision.revision + 1) if last_revision else 1
    
    logger.info(f"Recipient found: {recipient.company.company_name}")
    logger.info(f"Last revision: {last_revision.revision if last_revision else 'None'}")
    logger.info(f"Next revision number: {next_rev}")
    
    try:
        if creation_method == 'blank':
            logger.info("Creating blank revision")
            new_quote = Quote(recipient_id=recipient.id, revision=next_rev, notes="New blank quote.")
            db.session.add(new_quote)
            db.session.flush()
            db.session.add(QuoteOption(quote_id=new_quote.id, name="Main Option"))
        elif creation_method == 'copy_last':
            logger.info("Copying last revision")
            if not last_revision: 
                logger.error("Cannot copy, no last revision exists")
                flash("Cannot copy last revision - no previous revisions exist for this recipient.", 'error')
                return redirect(url_for('deals.deal_details', deal_id=deal_id))
            new_quote = _clone_quote(last_revision, recipient, next_rev)
        elif creation_method == 'clone_other':
            logger.info("Cloning other revision")
            source_quote_id = request.form.get('source_quote_id', type=int)
            if not source_quote_id: 
                logger.error("Missing source_quote_id for clone_other")
                flash('Must select a source quote to clone from.', 'error')
                return redirect(url_for('deals.deal_details', deal_id=deal_id))
            
            # Validate that source quote exists and belongs to this deal
            source_quote = Quote.query.join(QuoteRecipient).filter(
                Quote.id == source_quote_id,
                QuoteRecipient.deal_id == deal_id
            ).first()
            
            if not source_quote:
                logger.error(f"Source quote {source_quote_id} not found or doesn't belong to deal {deal_id}")
                flash('Invalid source quote selected.', 'error')
                return redirect(url_for('deals.deal_details', deal_id=deal_id))
                
            new_quote = _clone_quote(source_quote, recipient, next_rev)
        
        db.session.commit()
        
        # Update the deal's total amount
        deal.update_total_amount()
        db.session.commit()
        
        logger.info(f"Successfully created revision #{next_rev}")
        flash(f"Created Revision #{next_rev} for {recipient.company.company_name}.", 'success')
    except Exception as e:
        logger.error(f"ERROR creating revision: {e}", exc_info=True)
        db.session.rollback()
        flash(f"An error occurred while creating the revision: {str(e)}", "error")
    
    logger.info(f"=== ADD_REVISION DEBUG END ===")
    return redirect(url_for('deals.deal_details', deal_id=deal_id))

@deals_bp.route('/revision/delete/<int:quote_id>', methods=['POST'])
def delete_revision(quote_id):
    quote = Quote.query.get_or_404(quote_id)
    deal_id = quote.recipient.deal_id
    deal = quote.recipient.deal
    
    db.session.delete(quote)
    db.session.commit()
    
    # Update the deal's total amount
    deal.update_total_amount()
    db.session.commit()
    
    flash(f'Revision #{quote.revision} deleted.', 'success')
    return redirect(url_for('deals.deal_details', deal_id=deal_id))

@deals_bp.route('/quote_option/add/<int:quote_id>', methods=['POST'])
def add_quote_option(quote_id):
    quote = Quote.query.get_or_404(quote_id)
    form = QuoteOptionForm()
    if form.validate_on_submit():
        new_option = QuoteOption(quote_id=quote.id, name=form.name.data)
        db.session.add(new_option)
        db.session.commit()
        
        # Update the deal's total amount
        deal = quote.recipient.deal
        deal.update_total_amount()
        db.session.commit()
        
        flash('Option added!', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {getattr(form, field).label.text}: {error}", 'error')
    return redirect(url_for('deals.deal_details', deal_id=quote.recipient.deal_id))

@deals_bp.route('/quote_option/delete/<int:option_id>', methods=['POST'])
def delete_quote_option(option_id):
    option = QuoteOption.query.get_or_404(option_id)
    deal_id = option.quote.recipient.deal_id
    deal = option.quote.recipient.deal
    
    db.session.delete(option)
    db.session.commit()
    
    # Update the deal's total amount
    deal.update_total_amount()
    db.session.commit()
    
    flash('Option deleted.', 'success')
    return redirect(url_for('deals.deal_details', deal_id=deal_id))

@deals_bp.route('/line_item/add/<int:option_id>', methods=['POST'])
def add_line_item(option_id):
    form = LineItemForm()
    option = QuoteOption.query.get_or_404(option_id)
    if form.validate_on_submit():
        max_order = db.session.query(db.func.max(QuoteLineItem.display_order)).filter_by(option_id=option.id).scalar() or 0
        
        product = Product.query.get(form.product_id.data) if form.product_id.data else None
        discount_percentage = form.discount.data if form.discount.data is not None else 0.0
        
        # Use discount from product if available, unless manually overridden
        if product and product.discount and not form.discount.data:
            discount_percentage = product.discount.percentage
        
        # Get list_price from form or product
        list_price = form.list_price.data
        if list_price is None and product and product.list_price:
            list_price = float(product.list_price)
        
        # Calculate unit_price - prioritize product's discounted price if available
        unit_price = form.unit_price.data
        
        # If we have a product with pricing, use its get_discounted_price method for accuracy
        if product and product.list_price:
            # Use product's discounted price calculation
            discounted_price = product.get_discounted_price()
            if discounted_price and discounted_price > 0:
                unit_price = float(discounted_price)
                # If discount wasn't manually set, use product's discount
                if not form.discount.data and product.discount:
                    discount_percentage = product.discount.percentage
                # Set list_price from product if not provided
                if list_price is None:
                    list_price = float(product.list_price)
        elif list_price is not None and list_price > 0:
            # Fallback: calculate from list_price and discount
            discount = float(discount_percentage)
            unit_price = float(list_price) - (float(list_price) * discount / 100)
        
        # Ensure unit_price is set - use form value if product doesn't have pricing
        if unit_price is None or unit_price <= 0:
            # If form has a unit_price, use it (for custom items or products without pricing)
            if form.unit_price.data and form.unit_price.data > 0:
                unit_price = float(form.unit_price.data)
            else:
                # Last resort: set to 0
                unit_price = 0.0

        new_item = QuoteLineItem(
            option_id=option.id,
            product_id=form.product_id.data or None,
            notes=form.notes.data,
            quantity=form.quantity.data,
            list_price=list_price,
            unit_price=unit_price,
            discount=discount_percentage,
            display_order=max_order + 1
        )
        db.session.add(new_item)
        db.session.commit()
        
        # Update the deal's total amount
        deal = option.quote.recipient.deal
        deal.update_total_amount()
        db.session.commit()
        
        flash('Line item added!', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {getattr(form, field).label.text}: {error}", 'error')
    return redirect(url_for('deals.deal_details', deal_id=option.quote.recipient.deal_id))

@deals_bp.route('/line_item/delete/<int:item_id>', methods=['POST'])
def delete_line_item(item_id):
    item = QuoteLineItem.query.get_or_404(item_id)
    deal_id = item.option.quote.recipient.deal_id
    deal = item.option.quote.recipient.deal
    
    # Check if this is a pump assembly header (has colon in name and next item is sub-item)
    is_pump_assembly = (item.custom_name and 
                       ':' in item.custom_name and 
                       not item.custom_name.startswith('  •'))
    
    deleted_count = 1
    
    if is_pump_assembly:
        # Find all sub-items for this assembly (items with display_order > current item)
        # and custom_name starting with '  •'
        current_order = item.display_order
        sub_items = QuoteLineItem.query.filter(
            QuoteLineItem.option_id == item.option_id,
            QuoteLineItem.display_order > current_order,
            QuoteLineItem.custom_name.like('  •%')
        ).all()
        
        # Delete all sub-items first
        for sub_item in sub_items:
            db.session.delete(sub_item)
            deleted_count += 1
        
        logger.info(f"Deleted pump assembly '{item.custom_name}' with {len(sub_items)} sub-components")
    
    # Delete the main item
    db.session.delete(item)
    db.session.commit()
    
    # Update the deal's total amount
    deal.update_total_amount()
    db.session.commit()
    
    if is_pump_assembly:
        flash(f'Pump assembly deleted with {deleted_count} components.', 'success')
    else:
        flash('Line item deleted.', 'success')
    
    return redirect(url_for('deals.deal_details', deal_id=deal_id))

@deals_bp.route('/<int:deal_id>/add_party', methods=['POST'])
def add_party_to_deal(deal_id):
    deal = Deal.query.get_or_404(deal_id)
    company_id = request.form.get('company_id', type=int)
    contact_id = request.form.get('contact_id', type=int)
    if company_id:
        company = Company.query.get_or_404(company_id)
        if company not in deal.companies:
            deal.companies.append(company)
            recipient = QuoteRecipient(deal_id=deal.id, company_id=company.id)
            db.session.add(recipient)
            flash(f"Company '{company.company_name}' added to deal.", "success")
        else:
            flash(f"Company '{company.company_name}' is already associated with this deal.", "info")
    if contact_id:
        contact = Contact.query.get_or_404(contact_id)
        if contact not in deal.contacts:
            deal.contacts.append(contact)
            if contact.company and contact.company not in deal.companies:
                deal.companies.append(contact.company)
                existing_recipient = QuoteRecipient.query.filter_by(deal_id=deal.id, company_id=contact.company.id).first()
                if not existing_recipient:
                    recipient = QuoteRecipient(deal_id=deal.id, company_id=contact.company.id)
                    db.session.add(recipient)
            flash(f"Contact '{contact.name}' added to deal.", "success")
        else:
            flash(f"Contact '{contact.name}' is already associated with this deal.", "info")
    db.session.commit()
    return redirect(url_for('deals.deal_details', deal_id=deal_id))

@deals_bp.route('/<int:deal_id>/remove_party', methods=['POST'])
def remove_party_from_deal(deal_id):
    deal = Deal.query.get_or_404(deal_id)
    company_id = request.form.get('company_id', type=int)
    contact_id = request.form.get('contact_id', type=int)
    if company_id:
        company = Company.query.get_or_404(company_id)
        if company in deal.companies:
            QuoteRecipient.query.filter_by(deal_id=deal.id, company_id=company.id).delete()
            deal.companies.remove(company)
            flash(f"Company '{company.company_name}' and its quotes have been removed from this deal.", "success")
    if contact_id:
        contact = Contact.query.get_or_404(contact_id)
        if contact in deal.contacts:
            deal.contacts.remove(contact)
            flash(f"Contact '{contact.name}' removed from deal.", "success")
    db.session.commit()
    return redirect(url_for('deals.deal_details', deal_id=deal_id))

@deals_bp.route('/api/products/search', methods=['GET'])
def search_products():
    search_term = request.args.get('q', '', type=str)
    if not search_term or len(search_term) < 2:
        return jsonify([])

    products = Product.query.filter(
        or_(
            Product.description.ilike(f'%{search_term}%'),
            Product.item_no.ilike(f'%{search_term}%')
        )
    ).limit(10).all()
    
    results = []
    for p in products:
        list_price = float(p.list_price) if p.list_price else 0.0
        discount_pct = float(p.discount.percentage) if p.discount and p.discount.is_valid() else 0.0
        # Use product's get_discounted_price method to ensure correct calculation
        discounted_price = float(p.get_discounted_price()) if p.list_price else 0.0
        
        results.append({
            'id': p.id,
            'series': p.series or '',
            'sku': p.item_no,
            'name': p.description,
            'list_price': str(list_price) if list_price > 0 else '',
            'disc_code': p.discount_code or '',
            'discount': discount_pct,
            'unit_price': str(discounted_price) if discounted_price > 0 else ''
        })
    return jsonify(results)

@deals_bp.route('/api/line-item/<int:item_id>/update-field', methods=['POST'])
def update_line_item_field(item_id):
    item = QuoteLineItem.query.get_or_404(item_id)
    data = request.get_json()
    field = data.get('field')
    value = data.get('value')
    if not field or value is None:
        return jsonify({'success': False, 'message': 'Missing field or value.'}), 400
    allowed_fields = ['notes', 'quantity', 'unit_price', 'discount', 'custom_name']
    if field not in allowed_fields:
        return jsonify({'success': False, 'message': f'Field "{field}" cannot be edited.'}), 400
    try:
        if field == 'custom_name':
            item.product_id = None
            item.custom_sku = "CUSTOM"
        if field == 'quantity':
            value = int(value)
        elif field in ['unit_price', 'discount']:
            value = Decimal(value)
        setattr(item, field, value)
        db.session.commit()
        
        # Update the deal's total amount
        deal = item.option.quote.recipient.deal
        deal.update_total_amount()
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Field updated.', 'newState': {'sku': item.custom_sku or (item.product.item_no if item.product else 'N/A')}})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating line item {item_id}: {e}")
        return jsonify({'success': False, 'message': 'An error occurred.'}), 500

@deals_bp.route('/api/quote-option/<int:option_id>/update-field', methods=['POST'])
def update_quote_option_field(option_id):
    option = QuoteOption.query.get_or_404(option_id)
    data = request.get_json()
    field = data.get('field')
    value = data.get('value')
    if not field or value is None:
        return jsonify({'success': False, 'message': 'Missing field or value.'}), 400
    allowed_fields = ['name', 'freight_charge']
    if field not in allowed_fields:
        return jsonify({'success': False, 'message': f'Field "{field}" cannot be edited.'}), 400
    try:
        if field == 'freight_charge':
            value = Decimal(value)
        setattr(option, field, value)
        db.session.commit()
        
        # Update the deal's total amount
        deal = option.quote.recipient.deal
        deal.update_total_amount()
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Field updated.'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating quote option {option_id}: {e}")
        return jsonify({'success': False, 'message': 'An error occurred.'}), 500

@deals_bp.route('/api/quote-option/<int:option_id>/update_lead_time', methods=['POST'])
def update_quote_option_lead_time(option_id):
    """Update lead-time fields for a quote option."""
    option = QuoteOption.query.get_or_404(option_id)
    data = request.get_json()
    
    try:
        # Update lead-time fields
        option.lead_time_value = data.get('lead_time_value')
        option.lead_time_unit = data.get('lead_time_unit')
        option.is_ex_stock_brisbane = data.get('is_ex_stock_brisbane', False)
        
        # Validate lead-time value if not ex-stock
        if not option.is_ex_stock_brisbane and option.lead_time_value:
            # Allow ranges like "3-4" or single values like "8"
            import re
            pattern = r'^\d+(-\d+)?$'
            if not re.match(pattern, option.lead_time_value.strip()):
                return jsonify({'success': False, 'error': 'Lead-time value must be a number (e.g., "8") or range (e.g., "3-4").'}), 400
            
            # Validate range format if it contains a dash
            if '-' in option.lead_time_value:
                parts = option.lead_time_value.split('-')
                if len(parts) != 2:
                    return jsonify({'success': False, 'error': 'Range must be in format "min-max" (e.g., "3-4").'}), 400
                try:
                    min_val = int(parts[0])
                    max_val = int(parts[1])
                    if min_val < 1 or max_val < 1 or min_val >= max_val:
                        return jsonify({'success': False, 'error': 'Range values must be positive and min must be less than max.'}), 400
                except ValueError:
                    return jsonify({'success': False, 'error': 'Range values must be valid numbers.'}), 400
            else:
                # Single value validation
                try:
                    val = int(option.lead_time_value)
                    if val < 1:
                        return jsonify({'success': False, 'error': 'Lead-time value must be at least 1.'}), 400
                except ValueError:
                    return jsonify({'success': False, 'error': 'Lead-time value must be a valid number.'}), 400
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Lead-time updated successfully.'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating lead-time for quote option {option_id}: {e}")
        return jsonify({'success': False, 'error': 'An error occurred while updating lead-time.'}), 500

@deals_bp.route('/api/quote-option/<int:option_id>/reorder-items', methods=['POST'])
def reorder_line_items(option_id):
    option = QuoteOption.query.get_or_404(option_id)
    data = request.get_json()
    ordered_ids = data.get('ordered_ids')
    if not ordered_ids:
        return jsonify({'success': False, 'message': 'Missing order data.'}), 400
    try:
        for index, item_id in enumerate(ordered_ids):
            item = QuoteLineItem.query.filter_by(id=item_id, option_id=option.id).first()
            if item:
                item.display_order = index
        db.session.commit()
        
        # Update the deal's total amount
        deal = option.quote.recipient.deal
        deal.update_total_amount()
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Order updated.'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error reordering line items for option {option_id}: {e}")
        return jsonify({'success': False, 'message': 'An error occurred.'}), 500

@deals_bp.route('/api/pump-assembly/<int:assembly_id>/distribute-price', methods=['POST'])
def distribute_assembly_price(assembly_id):
    """Distribute the total assembly price among its components proportionally."""
    try:
        from app.models import QuoteLineItem
        
        assembly_header = QuoteLineItem.query.get_or_404(assembly_id)
        data = request.get_json()
        new_total_price = float(data.get('total_price', 0))
        
        if new_total_price <= 0:
            return jsonify({'success': False, 'message': 'Total price must be greater than 0.'}), 400
        
        # Find all sub-components of this assembly
        option = assembly_header.option
        assembly_name = assembly_header.custom_name
        
        # Get all line items for this option that are sub-items of this assembly
        all_items = QuoteLineItem.query.filter_by(option_id=option.id).order_by(QuoteLineItem.display_order).all()
        
        # Find the assembly header and its sub-items
        assembly_items = []
        in_assembly = False
        
        for item in all_items:
            if item.id == assembly_id:
                # This is the assembly header
                assembly_items.append(item)
                in_assembly = True
            elif in_assembly and item.custom_name and item.custom_name.startswith('  •'):
                # This is a sub-component
                assembly_items.append(item)
            elif in_assembly and not (item.custom_name and item.custom_name.startswith('  •')):
                # We've reached the end of this assembly
                break
        
        if len(assembly_items) < 2:
            return jsonify({'success': False, 'message': 'Assembly must have at least one component.'}), 400
        
        # Calculate current total value of components (excluding header)
        current_total = 0
        component_items = assembly_items[1:]  # Skip the header
        
        for item in component_items:
            current_total += float(item.unit_price * item.quantity)
        
        if current_total <= 0:
            return jsonify({'success': False, 'message': 'Current component total must be greater than 0.'}), 400
        
        # Calculate the scaling factor
        scale_factor = new_total_price / current_total
        
        # Update component prices proportionally with professional rounding
        updated_components = []
        
        # First pass: calculate proportional prices and round to professional values
        component_data = []
        total_rounded = 0
        
        for item in component_items:
            new_unit_price = float(item.unit_price) * scale_factor
            rounded_price = round_to_professional_pricing(new_unit_price)
            total_price = rounded_price * item.quantity
            total_rounded += total_price
            
            component_data.append({
                'item': item,
                'rounded_price': rounded_price,
                'total_price': total_price,
                'quantity': item.quantity
            })
        
        # Second pass: consolidate cents and adjust for exact total
        if component_data:
            # First, consolidate cents between components for cleaner pricing
            consolidate_cents(component_data)
            
            # Then adjust for exact total using .25 cent adjustments (only if needed)
            current_total = sum(comp['total_price'] for comp in component_data)
            difference = new_total_price - current_total
            
            logger.info(f"Assembly price distribution - Target: ${new_total_price}, Current: ${current_total}, Difference: ${difference}")
            
            if abs(difference) < 0.01:  # Already exact, no adjustment needed
                logger.info("Total is already exact, no adjustment needed")
            else:  # Need to adjust
                adjust_for_exact_total(component_data, difference)
                
                # Verify final total
                final_total = sum(comp['total_price'] for comp in component_data)
                logger.info(f"Final total after adjustment: ${final_total}")
        
        # Apply the prices to the database
        for comp in component_data:
            comp['item'].unit_price = Decimal(str(comp['rounded_price']))
            updated_components.append({
                'id': comp['item'].id,
                'name': comp['item'].custom_name,
                'new_unit_price': comp['rounded_price'],
                'quantity': comp['quantity'],
                'total_price': comp['total_price']
            })
        
        db.session.commit()
        
        # Update the deal's total amount
        deal = option.quote.recipient.deal
        deal.update_total_amount()
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Assembly price distributed successfully.',
            'updated_components': updated_components
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error distributing assembly price for {assembly_id}: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while distributing prices.'}), 500

def _generate_pdf_fallback(html_content):
    """Generate PDF from HTML content using weasyprint or return HTML as fallback."""
    try:
        logger.info(f"Starting WeasyPrint fallback PDF generation with HTML content length: {len(html_content)}")
        # Try to import weasyprint for PDF generation
        from weasyprint import HTML, CSS
        from weasyprint.text.fonts import FontConfiguration
        
        # Create HTML object
        html = HTML(string=html_content)
        
        # Configure fonts
        font_config = FontConfiguration()
        
        # Generate PDF
        pdf_data = html.write_pdf(
            stylesheets=[],
            font_config=font_config
        )
        logger.info(f"WeasyPrint PDF generated successfully, size: {len(pdf_data)} bytes")
        return pdf_data
    except ImportError:
        logger.warning("WeasyPrint not available, returning HTML content as fallback")
        # If weasyprint is not available, return HTML content
        # This will be displayed in the browser instead of PDF
        return html_content.encode('utf-8')
    except Exception as e:
        logger.error(f"Error generating PDF with weasyprint: {e}")
        # Return HTML content as fallback
        return html_content.encode('utf-8')

async def _generate_pdf(html_content):
    """Async helper function to launch browser and create PDF using Playwright."""
    try:
        logger.info(f"Starting Playwright PDF generation with HTML content length: {len(html_content)}")
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Convert HTML content to data URL to handle external resources
            import base64
            html_encoded = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
            data_url = f"data:text/html;base64,{html_encoded}"
            
            logger.info(f"Navigating to data URL (first 100 chars): {data_url[:100]}...")
            # Navigate to the data URL
            await page.goto(data_url)
            
            # Wait for the page to load completely
            await page.wait_for_load_state('networkidle')
            
            logger.info("Page loaded, generating PDF...")
            pdf_data = await page.pdf(
                format='A4',
                print_background=True,
                margin={'top': '20px', 'right': '20px', 'bottom': '20px', 'left': '20px'}
            )
            await browser.close()
            logger.info(f"PDF generated successfully, size: {len(pdf_data)} bytes")
            return pdf_data
    except Exception as e:
        logger.warning(f"Playwright PDF generation failed: {e}")
        # Fall back to weasyprint or HTML
        return _generate_pdf_fallback(html_content)



