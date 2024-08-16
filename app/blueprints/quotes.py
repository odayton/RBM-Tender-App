from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.utils.db_utils import insert_into_db, fetch_all_from_table, get_db_connection
from app.blueprints.forms import DealForm
from datetime import datetime, timedelta

quotes_bp = Blueprint('quotes', __name__)

@quotes_bp.route('/quotes', methods=['GET', 'POST'])
def view_quotes():
    form = DealForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            deal_name = form.deal_name.data
            deal_stage = form.deal_stage.data
            deal_type = form.deal_type.data
            deal_location = form.deal_location.data
            close_date = form.close_date.data
            deal_owner = form.deal_owner.data
            contact_id = form.contact.data
            company_id = form.company.data

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

            # Insert into the Deals table
            try:
                insert_into_db('Deals', deal_data)
                success_message = "Deal created successfully!"
                flash(success_message, "success")
                print(success_message)
                # Fetch the ID of the newly created deal
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT last_insert_rowid()')
                deal_id = cursor.fetchone()[0]
                conn.close()
                return redirect(url_for('quotes.view_deal', deal_id=deal_id))
            except Exception as e:
                error_message = f"Error creating deal: {str(e)}"
                flash(error_message, "danger")
                print(error_message)
        else:
            error_message = "Please correct the errors in the form."
            flash(error_message, "danger")
            print(error_message)

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
        'avg_deal_age': avg_deal_age
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

    return render_template('quote/individual_deal_page.html', deal=deal, quotes=quotes, line_items=line_items)
