from flask import (
    Blueprint, render_template, request, jsonify, redirect, url_for, flash, make_response, current_app
)
from collections import defaultdict
from decimal import Decimal
import asyncio
import os
from pyppeteer import launch

from app.models import (
    Deal, User, Quote, QuoteLineItem, DealStage, AustralianState, DealType,
    Company, Contact, QuoteRecipient, QuoteOption, Product
)
from .forms import DealForm, LineItemForm, QuoteOptionForm, UpdateDealForm
from app.extensions import db
from app.core.core_logging import logger

from . import deals_bp

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
def list_deals():
    """Display a list of all deals, grouped by stage."""
    form = DealForm()
    deals = Deal.query.order_by(Deal.created_at.desc()).all()

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
        form=form
    )

@deals_bp.route('/<int:deal_id>')
def deal_details(deal_id):
    """Display the details of a single deal."""
    deal = Deal.query.get_or_404(deal_id)
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

@deals_bp.route('/search/modal', methods=['GET'])
def search_for_modal():
    """
    Handles search requests from the deal creation modal for contacts and companies.
    """
    search_type = request.args.get('type')
    query = request.args.get('q', '')
    results = []

    if not query or len(query) < 2:
        return jsonify([])

    if search_type == 'contact':
        # Search for contacts by name or email
        contacts = Contact.query.join(Company).filter(
            db.or_(
                Contact.name.ilike(f'%{query}%'),
                Contact.email.ilike(f'%{query}%')
            )
        ).limit(10).all()
        # Format results for the frontend, using the CORRECT attribute 'company_name'
        results = [{'id': c.id, 'text': f"{c.name} ({c.company.company_name})"} for c in contacts]

    elif search_type == 'company':
        # Search for companies by name, using the CORRECT attribute 'company_name'
        companies = Company.query.filter(
            Company.company_name.ilike(f'%{query}%')
        ).limit(10).all()
        # Format results for the frontend, using the CORRECT attribute 'company_name'
        results = [{'id': comp.id, 'text': comp.company_name} for comp in companies]

    return jsonify(results)

@deals_bp.route('/create', methods=['POST'])
def create_deal():
    """Creates a new deal from the form on the main deals page."""
    form = DealForm()
    if form.validate_on_submit():
        try:
            # --- MODIFIED SECTION ---
            # Don't rely on a hardcoded user. Just find the first user.
            # A better long-term solution is to use the logged-in user.
            owner = User.query.first()
            if not owner:
                # This will only fail if the users table is completely empty
                flash('No users found in the database to assign as owner.', 'error')
                return redirect(url_for('deals.list_deals'))
            # --- END MODIFIED SECTION ---

            new_deal = Deal(
                project_name=form.project_name.data,
                deal_type=DealType[form.deal_type.data],
                state=AustralianState[form.state.data],
                owner_id=owner.id,
                stage=DealStage.SALES_LEAD
            )
            db.session.add(new_deal)
            
            # This logic remains the same
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
            flash('Deal created successfully!', 'success')
            # On success, we go to the new deal's page
            return redirect(url_for('deals.deal_details', deal_id=new_deal.id))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating deal: {e}")
            flash(f'An error occurred: {e}', 'error')
            return redirect(url_for('deals.list_deals'))
    else:
        # If validation fails, show the specific errors
        for field, errors in form.errors.items():
            for error in errors:
                # Use getattr to get the field's label for a more user-friendly message
                flash(f"Error in field '{getattr(form, field).label.text}': {error}", 'error')
        return redirect(url_for('deals.list_deals'))
    
@deals_bp.route('/update/<int:deal_id>', methods=['POST'])
def update_deal(deal_id):
    """Updates the core details of an existing deal."""
    deal = Deal.query.get_or_404(deal_id)
    form = UpdateDealForm(request.form, obj=deal)
    form.owner_id.choices = [(u.id, u.username) for u in User.query.order_by('username').all()]

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

@deals_bp.route('/add_revision/<int:deal_id>', methods=['POST'])
def add_revision(deal_id):
    recipient_id = request.form.get('recipient_id', type=int)
    creation_method = request.form.get('creation_method')
    if not recipient_id or not creation_method:
        flash('Invalid request.', 'error'); return redirect(url_for('deals.deal_details', deal_id=deal_id))
    recipient = QuoteRecipient.query.get_or_404(recipient_id)
    last_revision = Quote.query.filter_by(recipient_id=recipient.id).order_by(Quote.revision.desc()).first()
    next_rev = (last_revision.revision + 1) if last_revision else 1
    try:
        if creation_method == 'blank':
            new_quote = Quote(recipient_id=recipient.id, revision=next_rev, notes="New blank quote.")
            db.session.add(new_quote); db.session.flush()
            db.session.add(QuoteOption(quote_id=new_quote.id, name="Main Option"))
        elif creation_method == 'copy_last':
            if not last_revision: flash("Cannot copy, none exist.", 'error'); return redirect(url_for('deals.deal_details', deal_id=deal_id))
            _clone_quote(last_revision, recipient, next_rev)
        elif creation_method == 'clone_other':
            source_quote_id = request.form.get('source_quote_id', type=int)
            if not source_quote_id: flash('Must select a source quote.', 'error'); return redirect(url_for('deals.deal_details', deal_id=deal_id))
            _clone_quote(Quote.query.get_or_404(source_quote_id), recipient, next_rev)
        db.session.commit()
        flash(f"Created Revision #{next_rev} for {recipient.company.company_name}.", 'success')
    except Exception as e:
        db.session.rollback(); logger.error(f"Error creating revision: {e}"); flash(f"An error occurred: {e}", "error")
    return redirect(url_for('deals.deal_details', deal_id=deal_id))

@deals_bp.route('/revision/delete/<int:quote_id>', methods=['POST'])
def delete_revision(quote_id):
    quote = Quote.query.get_or_404(quote_id); deal_id = quote.recipient.deal_id
    db.session.delete(quote); db.session.commit()
    flash(f'Revision #{quote.revision} deleted.', 'success')
    return redirect(url_for('deals.deal_details', deal_id=deal_id))

@deals_bp.route('/quote_option/add/<int:quote_id>', methods=['POST'])
def add_quote_option(quote_id):
    quote = Quote.query.get_or_404(quote_id); form = QuoteOptionForm()
    if form.validate_on_submit():
        db.session.add(QuoteOption(quote_id=quote.id, name=form.name.data))
        db.session.commit(); flash(f"Option '{form.name.data}' added.", 'success')
    else: flash('Error adding option.', 'error')
    return redirect(url_for('deals.deal_details', deal_id=quote.recipient.deal_id))

@deals_bp.route('/quote_option/delete/<int:option_id>', methods=['POST'])
def delete_quote_option(option_id):
    option = QuoteOption.query.get_or_404(option_id); deal_id = option.quote.recipient.deal_id
    db.session.delete(option); db.session.commit(); flash('Option deleted.', 'success')
    return redirect(url_for('deals.deal_details', deal_id=deal_id))

@deals_bp.route('/line_item/add/<int:option_id>', methods=['POST'])
def add_line_item(option_id):
    form = LineItemForm()
    option = QuoteOption.query.get_or_404(option_id)
    if form.validate_on_submit():
        max_order = db.session.query(db.func.max(QuoteLineItem.display_order)).filter_by(option_id=option.id).scalar() or 0
        new_item = QuoteLineItem(
            option_id=option.id,
            product_id=form.product_id.data or None,
            notes=form.notes.data,
            quantity=form.quantity.data,
            unit_price=form.unit_price.data,
            discount=form.discount.data,
            display_order=max_order + 1
        )
        db.session.add(new_item)
        db.session.commit()
        flash('Line item added!', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {getattr(form, field).label.text}: {error}", 'error')
    return redirect(url_for('deals.deal_details', deal_id=option.quote.recipient.deal_id))

@deals_bp.route('/line_item/delete/<int:item_id>', methods=['POST'])
def delete_line_item(item_id):
    item = QuoteLineItem.query.get_or_404(item_id); deal_id = item.option.quote.recipient.deal_id
    db.session.delete(item); db.session.commit(); flash('Line item deleted.', 'success')
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
            flash(f"Contact '{contact.full_name}' added to deal.", "success")
        else:
            flash(f"Contact '{contact.full_name}' is already associated with this deal.", "info")
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
            flash(f"Contact '{contact.full_name}' removed from deal.", "success")
    db.session.commit()
    return redirect(url_for('deals.deal_details', deal_id=deal_id))

@deals_bp.route('/api/products/search', methods=['GET'])
def search_products():
    search_term = request.args.get('q', '', type=str)
    if not search_term or len(search_term) < 2:
        return jsonify([])
    products = Product.query.filter(
        (Product.name.ilike(f'%{search_term}%')) |
        (Product.sku.ilike(f'%{search_term}%'))
    ).limit(10).all()
    results = [
        {'id': p.id, 'sku': p.sku, 'name': p.name, 'unit_price': str(p.unit_price) }
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
        if field in ['quantity', 'unit_price', 'discount']:
            value = Decimal(value)
        setattr(item, field, value)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Field updated.', 'newState': {'sku': item.custom_sku or (item.product.sku if item.product else 'N/A')}})
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
        return jsonify({'success': True, 'message': 'Field updated.'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating quote option {option_id}: {e}")
        return jsonify({'success': False, 'message': 'An error occurred.'}), 500

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
        return jsonify({'success': True, 'message': 'Order updated.'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error reordering line items for option {option_id}: {e}")
        return jsonify({'success': False, 'message': 'An error occurred.'}), 500

async def _generate_pdf(html_content):
    """Async helper function to launch browser and create PDF."""
    possible_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    ]
    chrome_path = next((path for path in possible_paths if os.path.exists(path)), None)

    launch_options = {
        'handleSIGINT': False, 
        'handleSIGTERM': False, 
        'handleSIGHUP': False,
        'args': ['--no-sandbox']
    }

    if chrome_path:
        logger.info(f"Using local Google Chrome installation at: {chrome_path}")
        launch_options['executablePath'] = chrome_path
    else:
        logger.error("Google Chrome not found. Attempting to use pyppeteer's downloaded Chromium.")

    browser = await launch(**launch_options)
    page = await browser.newPage()
    # --- CORRECTED LINE: Removed extra arguments ---
    await page.setContent(html_content)
    pdf_data = await page.pdf({
        'format': 'A4',
        'printBackground': True,
        'margin': {'top': '20px', 'right': '20px', 'bottom': '20px', 'left': '20px'}
    })
    await browser.close()
    return pdf_data

@deals_bp.route('/option/<int:option_id>/export/pdf', methods=['GET'])
def export_quote_pdf(option_id):
    """
    Generates and serves a PDF for a specific quote OPTION.
    """
    option = QuoteOption.query.get_or_404(option_id)
    quote = option.quote
    deal = quote.recipient.deal

    category_templates = {
        'HVAC': 'deals/pdf/hvac_quote_template.html',
        'Plumbing': 'deals/pdf/plumbing_quote_template.html',
        'Hydronic Heating': 'deals/pdf/hydronic_heating_quote_template.html'
    }
    template_name = category_templates.get(deal.deal_type.name, 'deals/pdf/hvac_quote_template.html')

    # --- NEW: Read CSS file content to inline it ---
    try:
        css_file_path = os.path.join(current_app.static_folder, 'css', 'quote_pdf.css')
        with open(css_file_path) as f:
            css_content = f.read()
    except FileNotFoundError:
        logger.error("quote_pdf.css not found!")
        css_content = "" # Fail gracefully

    # --- Pass the css_content to the template ---
    rendered_html = render_template(
        template_name, 
        deal=deal, 
        revision=quote, 
        option=option, 
        css_content=css_content # Pass the string here
    )
    
    try:
        pdf_file = asyncio.run(_generate_pdf(rendered_html))
    except Exception as e:
        logger.error(f"PDF Generation Error: {e}")
        flash('There was an error generating the PDF. Please check the logs.', 'error')
        return redirect(url_for('deals.deal_details', deal_id=deal.id))

    response = make_response(pdf_file)
    response.headers['Content-Type'] = 'application/pdf'
    clean_option_name = "".join(c if c.isalnum() else "_" for c in option.name)
    response.headers['Content-Disposition'] = f'attachment; filename="Quote_{deal.id}_Rev_{quote.revision}_{clean_option_name}.pdf"'

    return response