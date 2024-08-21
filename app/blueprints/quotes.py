from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.utils.db_utils import insert_into_db, fetch_all_from_table, get_db_connection
from app.blueprints.forms import DealForm
from datetime import datetime, timedelta


quotes_bp = Blueprint('quotes', __name__)

@quotes_bp.route('/quotes', methods=['GET', 'POST'])
def view_quotes():
    form = DealForm()

    # Populate the dropdowns dynamically
    conn = get_db_connection()
    cursor = conn.cursor()

    # Correct field name in SQL query to match the DealOwnerForm
    cursor.execute('SELECT id, owner_name FROM DealOwners')
    deal_owners = cursor.fetchall()
    form.deal_owner.choices = [(owner['id'], owner['owner_name']) for owner in deal_owners]

    cursor.execute('SELECT id, representative_name FROM Contacts')
    contacts = cursor.fetchall()
    form.contact_id.choices = [(contact['id'], contact['representative_name']) for contact in contacts]

    cursor.execute('SELECT id, company_name FROM Companies')
    companies = cursor.fetchall()
    form.company_id.choices = [(company['id'], company['company_name']) for company in companies]

    # Fetch all deals and convert created_at to formatted string
    cursor.execute('SELECT * FROM Deals')
    deals = cursor.fetchall()

    # Convert `sqlite3.Row` objects to dict and format `created_at`
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
        else:
            print(f"Unknown stage: {stage}") 

    cursor.close()
    conn.close()

    if request.method == 'POST':
        if form.validate_on_submit():
            deal_name = form.deal_name.data
            deal_stage = form.deal_stage.data
            deal_type = form.deal_type.data
            deal_location = form.deal_location.data
            close_date = form.close_date.data
            deal_owner = form.deal_owner.data
            contact_id = form.contact_id.data
            company_id = form.company_id.data

            # Prepare data for insertion
            deal_data = {
                'name': deal_name,
                'stage': deal_stage or 'Sales Lead',  # Default stage if none selected
                'type': deal_type,
                'location': deal_location,
                'close_date': close_date,
                'owner': deal_owner,
                'contact_id': contact_id,
                'company_id': company_id,
                'created_at': datetime.now().strftime('%Y-%m-%d'),
                'updated_at': datetime.now().strftime('%Y-%m-%d')
            }

            # Insert into the Deals table and retrieve the new deal ID
            deal_id = insert_into_db('Deals', deal_data)

            if deal_id:
                return redirect(url_for('quotes.view_deal', deal_id=deal_id))
            else:
                flash("Error creating deal.", "danger")
        else:
            flash("Please correct the errors in the form.", "danger")

    # Fetch data for rendering quotes page (e.g., summary stats)
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

    data = {
        'total_deal_amount': total_deal_amount,
        'avg_deal_amount': avg_deal_amount,
        'quotes_mtd': quotes_mtd,
        'quotes_last_month': quotes_last_month,
        'avg_deal_age': avg_deal_age,
        'deals_by_stage': deals_by_stage  # Pass deals_by_stage to the template
    }

    return render_template('quote/quotes.html', form=form, **data, timedelta=timedelta, current_date=datetime.now())

# Route to display a specific deal
@quotes_bp.route('/deals/<int:deal_id>')
def view_deal(deal_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch deal details
    cursor.execute('SELECT * FROM Deals WHERE id = ?', (deal_id,))
    deal = cursor.fetchone()

    # Fetch associated contact
    cursor.execute('SELECT * FROM Contacts WHERE id = ?', (deal['contact_id'],))
    contact = cursor.fetchone()

    # Fetch associated company
    cursor.execute('SELECT * FROM Companies WHERE id = ?', (deal['company_id'],))
    company = cursor.fetchone()

    # Fetch associated quotes (if any)
    cursor.execute('SELECT * FROM Quotes WHERE deal_id = ?', (deal_id,))
    quotes = cursor.fetchall()

    # Fetch associated line items (if any)
    cursor.execute('''
    SELECT li.*, q.quote_number FROM LineItems li
    JOIN Quotes q ON li.quote_id = q.id
    WHERE q.deal_id = ?
    ''', (deal_id,))
    line_items = cursor.fetchall()

    cursor.close()
    conn.close()

    if not deal:
        flash("Deal not found.", "danger")
        return redirect(url_for('quotes.view_quotes'))

    return render_template('quote/individual_deal_page.html', deal=deal, quotes=quotes, line_items=line_items, contact=contact, company=company)

@quotes_bp.route('/update_deal_stage', methods=['POST'])
def update_deal_stage():
    data = request.get_json()
    deal_id = data.get('deal_id')
    new_stage = data.get('new_stage')

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE Deals SET stage = ?, updated_at = ? WHERE id = ?', (new_stage, datetime.now(), deal_id))
        conn.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
