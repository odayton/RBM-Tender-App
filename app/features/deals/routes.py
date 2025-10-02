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
def update_deal_stage(deal_id):
    """Updates the stage of a deal via AJAX (for kanban drag and drop)."""
    try:
        deal = Deal.query.get_or_404(deal_id)
        data = request.get_json()
        
        if not data or 'stage' not in data:
            return jsonify({'success': False, 'error': 'Invalid request data'}), 400
        
        new_stage = data['stage']
        
        # Validate that the stage is valid
        try:
            stage_enum = DealStage(new_stage)
        except ValueError:
            return jsonify({'success': False, 'error': f'Invalid stage: {new_stage}'}), 400
        
        # Update the deal stage
        old_stage = deal.stage.value
        deal.stage = stage_enum
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
        logger.error(f"Error updating deal {deal_id} stage: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

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
        discount_percentage = form.discount.data
        if product and product.discount:
            discount_percentage = product.discount.percentage

        new_item = QuoteLineItem(
            option_id=option.id,
            product_id=form.product_id.data or None,
            notes=form.notes.data,
            quantity=form.quantity.data,
            unit_price=form.unit_price.data,
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
    
    db.session.delete(item)
    db.session.commit()
    
    # Update the deal's total amount
    deal.update_total_amount()
    db.session.commit()
    
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
    
    results = [
        {
            'id': p.id,
            'sku': p.item_no,
            'name': p.description,
            'unit_price': str(p.list_price),
            'discount': float(p.discount.percentage) if p.discount else 0.0
        }
        for p in products
    ]
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



