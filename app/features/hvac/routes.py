# app/features/hvac/routes.py

from flask import Blueprint, render_template, request, jsonify
from app.extensions import db
from sqlalchemy import or_

# This form is correctly imported from the local hvac forms file
from .forms import PumpSearchForm
from app.models import QuoteOption, Product, QuoteLineItem

# Import the existing blueprint from the __init__.py file in this folder
from . import hvac_bp


def convert_to_base_units(flow, flow_units, head, head_units):
    """Converts flow and head to the database's base units (L/s, kPa)."""
    base_flow = flow
    if flow_units == 'm3_per_h' and flow is not None:
        base_flow = flow / 3.6

    base_head = head
    if head_units == 'm' and head is not None:
        base_head = head * 9.807
        
    return base_flow, base_head


def get_or_create_product_for_assembly(assembly_name, pump_model):
    """
    Creates a new Product for a pump assembly.
    """
    new_product = Product(
        sku=f"PUMP-{assembly_name}",
        name=f"Pump Assembly: {pump_model}",
        description=f"Assembly for {pump_model}.",
        unit_price=0.00, # Placeholder price
        category="Pump Assembly"
    )
    db.session.add(new_product)
    db.session.commit()
    return new_product


@hvac_bp.route('/search_pumps', methods=['GET', 'POST'])
def search_pumps():
    """
    Provides a form to search for pump assemblies and displays the results.
    """
    option_id = request.args.get('option_id', type=int)
    deal_id = None

    if option_id:
        option = QuoteOption.query.get_or_404(option_id)
        deal_id = option.quote.recipient.deal_id

    form = PumpSearchForm(request.form)
    
    # Simplified pump models - you can update this with actual data
    models = [("Grundfos CR", "Grundfos CR"), ("Grundfos NBG", "Grundfos NBG")]
    form.pump_models.choices = models

    search_results = []
    if request.method == 'POST' and form.validate_on_submit():
        # Simplified search - returns mock data
        search_results = [
            {"name": "Grundfos CR 10-3", "model": "Grundfos CR", "flow": "10 L/s", "head": "30 kPa"},
            {"name": "Grundfos NBG 15-5", "model": "Grundfos NBG", "flow": "15 L/s", "head": "50 kPa"}
        ]

    return render_template('hvac/search_pumps.html', 
                           form=form, 
                           option_id=option_id, 
                           deal_id=deal_id,
                           results=search_results)


@hvac_bp.route('/api/add-assembly-to-option', methods=['POST'])
def add_assembly_to_option():
    """API endpoint to add a pump assembly to a quote option."""
    data = request.get_json()
    if not data or 'assembly_name' not in data or 'option_id' not in data or 'pump_model' not in data:
        return jsonify({'success': False, 'message': 'Invalid request.'}), 400

    option = QuoteOption.query.get(data['option_id'])

    if not option:
        return jsonify({'success': False, 'message': 'Option not found.'}), 404

    try:
        product = get_or_create_product_for_assembly(data['assembly_name'], data['pump_model'])

        # Apply discount logic
        discount_percentage = 0.0
        if product and product.discount:
            discount_percentage = product.discount.percentage

        new_line_item = QuoteLineItem(
            option_id=option.id,
            product_id=product.id,
            quantity=1,
            unit_price=product.unit_price,
            discount=discount_percentage
        )
        db.session.add(new_line_item)
        db.session.commit()
        
        # Update the deal's total amount
        deal = option.quote.recipient.deal
        deal.update_total_amount()
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Successfully added {data["assembly_name"]} to option.'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred.'}), 500