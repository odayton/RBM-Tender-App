from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.utils.db_utils.db_deals import insert_deal, fetch_all_deals, update_deal_stage_in_db, fetch_deal_by_id, fetch_revisions_by_deal_id
from app.utils.db_utils.db_contacts import fetch_all_contacts, add_contact_to_deal
from app.utils.db_utils.db_companies import fetch_all_companies, add_company_to_deal
from app.utils.db_utils.db_line_items import insert_line_item, fetch_line_items_by_deal_id
from app.utils.db_utils.db_deal_owners import fetch_all_deal_owners
from app.utils.db_utils.db_connection import get_db_connection
from app.blueprints.forms import DealForm
from datetime import datetime, timedelta

quotes_bp = Blueprint('quotes', __name__)

#region "Quote Dashboard"
@quotes_bp.route('/quotes', methods=['GET', 'POST'])
def view_quotes():
    form = DealForm()

    # Populate the dropdowns dynamically
    deal_owners = fetch_all_deal_owners()
    form.deal_owner.choices = [(owner['id'], owner['owner_name']) for owner in deal_owners]

    contacts = fetch_all_contacts()
    form.contact_id.choices = [(contact['id'], contact['representative_name']) for contact in contacts]

    companies = fetch_all_companies()
    form.company_id.choices = [(company['id'], company['company_name']) for company in companies]

    # Fetch all deals and convert created_at to formatted string
    deals = fetch_all_deals()
    deals = [{**dict(deal), 'created_at': datetime.strptime(deal['created_at'], '%Y-%m-%d').strftime('%d/%m/%Y')} for deal in deals]

    deals_by_stage = {
        'Sales Lead': [],
        'Tender': [],
        'Proposal': [],
        'Negotiation': [],
        'Closed Won': [],
        'Closed Lost': [],
        'Abandoned': []
    }

    for deal in deals:
        stage = deal['stage']
        if stage in deals_by_stage:
            deals_by_stage[stage].append(deal)

    if request.method == 'POST':
        if form.validate_on_submit():
            deal_data = {
                'name': form.deal_name.data,
                'stage': form.deal_stage.data or 'Sales Lead',  # Default stage if none selected
                'type': form.deal_type.data,
                'location': form.deal_location.data,
                'close_date': form.close_date.data,
                'owner': form.deal_owner.data,
                'contact_id': form.contact_id.data,
                'company_id': form.company_id.data,
                'created_at': datetime.now().strftime('%Y-%m-%d'),
                'updated_at': datetime.now().strftime('%Y-%m-%d')
            }
            deal_id = insert_deal(deal_data)

            if deal_id:
                return redirect(url_for('quotes.view_deal', deal_id=deal_id))
            else:
                flash("Error creating deal.", "danger")
        else:
            flash("Please correct the errors in the form.", "danger")

    # Fetch data for rendering the summary stats
    total_deal_amount, avg_deal_amount, quotes_mtd, quotes_last_month, avg_deal_age = get_deal_stats()

    data = {
        'total_deal_amount': total_deal_amount,
        'avg_deal_amount': avg_deal_amount,
        'quotes_mtd': quotes_mtd,
        'quotes_last_month': quotes_last_month,
        'avg_deal_age': avg_deal_age,
        'deals_by_stage': deals_by_stage,
        'timedelta': timedelta,
        'current_date': datetime.now()
    }

    return render_template('quote/quotes.html', form=form, **data)
#endregion

#region "Individual Deals"
@quotes_bp.route('/deals/<int:deal_id>')
def view_deal(deal_id):
    deal = fetch_deal_by_id(deal_id)

    if not deal:
        flash("Deal not found.", "danger")
        return redirect(url_for('quotes.view_quotes'))

    contacts = fetch_all_contacts()
    companies = fetch_all_companies()

    # Fetch revisions for the deal
    revisions = fetch_revisions_by_deal_id(deal_id) or []  # Ensure we pass an empty list if no revisions

    # Fetch line items for the deal
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LineItems WHERE deal_id = ?", (deal_id,))
    line_items = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template(
        'quote/individual_deal_page.html',
        deal=deal,
        all_contacts=contacts,
        all_companies=companies,
        revisions=revisions,
        line_items=line_items  # Pass the line items to the template
    )
#endregion

#region "Update Deal Stage"
@quotes_bp.route('/update_deal_stage', methods=['POST'])
def update_deal_stage():
    data = request.get_json()
    deal_id = data.get('deal_id')
    new_stage = data.get('new_stage')

    try:
        update_deal_stage_in_db(deal_id, new_stage)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
#endregion

#region "Add Contact and Company"
@quotes_bp.route('/add_contact_company/<int:deal_id>', methods=['POST'])
def add_contact_company(deal_id):
    entity_type = request.form.get('entity_type')
    entity_id = request.form.get('entity_id')

    try:
        if entity_type == "contact":
            add_contact_to_deal(deal_id, entity_id)
        elif entity_type == "company":
            add_company_to_deal(deal_id, entity_id)

        flash('Contact/Company added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding Contact/Company: {str(e)}', 'danger')

    return redirect(url_for('quotes.view_deal', deal_id=deal_id))
#endregion

#region "Adding Line Items"
@quotes_bp.route('/add_line_item/<int:deal_id>/<string:entity_type>/<int:entity_id>', methods=['POST'])
def add_line_item(deal_id, entity_type, entity_id):
    description = request.form.get('description')
    amount = float(request.form.get('amount'))

    try:
        insert_line_item({
            'deal_id': deal_id,
            'entity_type': entity_type,
            'entity_id': entity_id,
            'description': description,
            'amount': amount
        })
        flash('Line item added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding line item: {str(e)}', 'danger')

    return redirect(url_for('quotes.view_deal', deal_id=deal_id))
#endregion

#region "Helper Functions"
def get_deal_stats():
    """Helper function to fetch deal stats."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT SUM(amount) FROM Deals')
        total_deal_amount = cursor.fetchone()[0] or 0

        cursor.execute('SELECT AVG(amount) FROM Deals')
        avg_deal_amount = cursor.fetchone()[0] or 0

        cursor.execute('SELECT COUNT(*) FROM Deals WHERE created_at >= date("now", "start of month")')
        quotes_mtd = cursor.fetchone()[0] or 0

        cursor.execute('SELECT COUNT(*) FROM Deals WHERE created_at >= date("now", "-1 month")')
        quotes_last_month = cursor.fetchone()[0] or 0

        cursor.execute('SELECT AVG(julianday("now") - julianday(created_at)) FROM Deals')
        avg_deal_age = cursor.fetchone()[0] or 0
    finally:
        cursor.close()
        conn.close()

    return total_deal_amount, avg_deal_amount, quotes_mtd, quotes_last_month, avg_deal_age
#endregion

#region "Add Pumps to Quote"
@quotes_bp.route('/deals/<int:deal_id>/add_pump', methods=['GET'])
def add_pump_to_deal(deal_id):
    # Extract pump data from the URL parameters
    sku = request.args.get('sku')
    flow = request.args.get('flow')
    head = request.args.get('head')

    # Fetch pump name based on SKU from the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM GeneralPumpDetails WHERE sku = ?", (sku,))
    pump_name = cursor.fetchone()
    cursor.close()
    conn.close()

    if pump_name is None:
        flash('Pump not found.', 'danger')
        return redirect(url_for('quotes.view_deal', deal_id=deal_id))

    # Create a line item for this pump using the flow and head from the form
    pump_data = {
        'deal_id': deal_id,
        'entity_type': 'pump',
        'entity_id': sku,
        'pump_name': pump_name[0],  # Use the fetched pump name
        'flow': flow,  # Use flow from the search form
        'head': head,  # Use head from the search form
        'description': '',
        'amount': 0,
        'created_at': datetime.now().strftime('%Y-%m-%d'),
        'updated_at': datetime.now().strftime('%Y-%m-%d')
    }

    insert_line_item(pump_data)

    # Redirect back to the deal page after adding the pump
    return redirect(url_for('quotes.view_deal', deal_id=deal_id))

#endregion

