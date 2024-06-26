# blueprints/quotes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from utils.db_utils import get_db_connection, insert_into_db, fetch_all_from_table
from blueprints.forms import CustomerForm, QuoteForm, QuoteItemForm

quotes_bp = Blueprint('quotes', __name__)

@quotes_bp.route('/customers/create', methods=['GET', 'POST'])
def create_customer():
    form = CustomerForm()
    if form.validate_on_submit():
        customer_data = {
            'company_name': form.company_name.data,
            'representative_name': form.representative_name.data,
            'representative_email': form.representative_email.data
        }
        insert_into_db('Customers', customer_data)
        flash('Customer created successfully!')
        return redirect(url_for('quotes.create_customer'))
    return render_template('quote_templates/customer_form.html', form=form)

@quotes_bp.route('/quotes/create', methods=['GET', 'POST'])
def create_quote():
    form = QuoteForm()
    customers = fetch_all_from_table('Customers')['rows']
    form.company_id.choices = [(c[0], c[1]) for c in customers]
    if form.validate_on_submit():
        project_data = {
            'project_name': form.project_name.data,
            'company_id': form.company_id.data
        }
        insert_into_db('Projects', project_data)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM Projects ORDER BY id DESC LIMIT 1')
        project_id = cursor.fetchone()[0]
        
        quote_data = {
            'project_id': project_id,
            'deal_location': form.deal_location.data,
            'terms_conditions': form.terms_conditions.data
        }
        insert_into_db('Quotes', quote_data)
        flash('Quote created successfully!')
        return redirect(url_for('quotes.view_quotes'))
    return render_template('quote_templates/quote_form.html', form=form)

@quotes_bp.route('/quotes/<int:quote_id>/add-item', methods=['GET', 'POST'])
def add_item_to_quote(quote_id):
    form = QuoteItemForm()
    pumps = fetch_all_from_table('Pump_Details')['rows']
    form.item_id.choices = [(p[0], p[1]) for p in pumps]
    if form.validate_on_submit():
        item_data = {
            'quote_id': quote_id,
            'item_id': form.item_id.data,
            'item_type': form.item_type.data,
            'quantity': form.quantity.data,
            'price': form.price.data,
            'total_price': form.total_price.data
        }
        insert_into_db('Quote_Items', item_data)
        flash('Item added to quote successfully!')
        return redirect(url_for('quotes.quote_details', quote_id=quote_id))
    return render_template('quote_templates/quote_item_form.html', form=form, quote_id=quote_id)

@quotes_bp.route('/quotes')
def view_quotes():
    quotes = fetch_all_from_table('Quotes')['rows']
    return render_template('quote_templates/quotes.html', quotes=quotes)

@quotes_bp.route('/quotes/<int:quote_id>')
def quote_details(quote_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Quotes WHERE id = ?', (quote_id,))
    quote = cursor.fetchone()
    cursor.execute('SELECT * FROM Quote_Items WHERE quote_id = ?', (quote_id,))
    items = cursor.fetchall()
    conn.close()

    quote_dict = {
        'id': quote[0],
        'project_id': quote[1],
        'date_created': quote[2],
        'total_amount': quote[3],
        'deal_location': quote[4],
        'terms_conditions': quote[5]
    }

    items_list = []
    for item in items:
        cursor.execute('SELECT Name, SKU, Description FROM Pump_Details WHERE SKU = ?', (item[2],))
        pump_details = cursor.fetchone()
        items_list.append({
            'id': item[0],
            'name': pump_details[0],
            'sku': pump_details[1],
            'description': pump_details[2],
            'quantity': item[4],
            'price': item[5],
            'total_price': item[6]
        })

    return render_template('quote_templates/quote_details.html', quote=quote_dict, items=items_list)

@quotes_bp.route('/quotes/<int:quote_id>/edit', methods=['GET', 'POST'])
def edit_quote(quote_id):
    form = QuoteForm()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Quotes WHERE id = ?', (quote_id,))
    quote = cursor.fetchone()
    projects = fetch_all_from_table('Projects')['rows']
    form.project_id.choices = [(p[0], p[1]) for p in projects]
    if request.method == 'GET':
        cursor.execute('SELECT project_id FROM Quotes WHERE id = ?', (quote_id,))
        project_id = cursor.fetchone()[0]
        cursor.execute('SELECT company_id FROM Projects WHERE id = ?', (project_id,))
        company_id = cursor.fetchone()[0]
        cursor.execute('SELECT project_name FROM Projects WHERE id = ?', (project_id,))
        project_name = cursor.fetchone()[0]

        form.company_id.data = company_id
        form.project_name.data = project_name
        form.deal_location.data = quote[4]
        form.terms_conditions.data = quote[5]
    if form.validate_on_submit():
        project_data = {
            'company_id': form.company_id.data,
            'project_name': form.project_name.data
        }
        cursor.execute('UPDATE Projects SET company_id = ?, project_name = ? WHERE id = ?', (form.company_id.data, form.project_name.data, project_id))
        quote_data = {
            'deal_location': form.deal_location.data,
            'terms_conditions': form.terms_conditions.data
        }
        cursor.execute('UPDATE Quotes SET deal_location = ?, terms_conditions = ? WHERE id = ?', (form.deal_location.data, form.terms_conditions.data, quote_id))
        conn.commit()
        conn.close()
        flash('Quote updated successfully!')
        return redirect(url_for('quotes.quote_details', quote_id=quote_id))
    return render_template('quote_templates/quote_form.html', form=form)

@quotes_bp.route('/quotes/<int:quote_id>/delete', methods=['POST'])
def delete_quote(quote_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Quotes WHERE id = ?', (quote_id,))
    conn.commit()
    conn.close()
    flash('Quote deleted successfully!')
    return redirect(url_for('quotes.view_quotes'))

@quotes_bp.route('/quotes/<int:quote_id>/delete_item/<int:item_id>', methods=['POST'])
def delete_quote_item(quote_id, item_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Quote_Items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@quotes_bp.route('/quotes/<int:quote_id>/update_items', methods=['POST'])
def update_quote_items(quote_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    for item_id, quantity in request.form.items():
        if item_id.startswith('quantity_'):
            id = int(item_id.split('_')[1])
            cursor.execute('UPDATE Quote_Items SET quantity = ? WHERE id = ?', (quantity, id))
    conn.commit()
    conn.close()
    flash('Quote items updated successfully!')
    return redirect(url_for('quotes.quote_details', quote_id=quote_id))
