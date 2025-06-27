from flask import Blueprint, render_template, request, abort, jsonify, flash, url_for
from app.extensions import db
from .forms import PumpSearchForm
from app.models import Pump, PumpAssembly, QuoteOption, Deal, Product, QuoteLineItem
# --- THIS IS THE FIX ---
# Import the existing blueprint from the __init__.py file in this folder
from . import hvac_bp
# --- END OF FIX ---


def convert_to_base_units(flow, flow_units, head, head_units):
    """Converts flow and head to the database's base units (L/s, kPa)."""
    base_flow = flow
    if flow_units == 'm3_per_h' and flow is not None:
        # 1 m³/hr = 1/3.6 L/s
        base_flow = flow / 3.6

    base_head = head
    if head_units == 'm' and head is not None:
        # 1 mH2O ≈ 9.807 kPa
        base_head = head * 9.807
        
    return base_flow, base_head

def get_or_create_product_for_assembly(assembly):
    """
    Finds the existing Product for a PumpAssembly or creates a new one.
    This is crucial for making an assembly a quotable item.
    """
    if assembly.product:
        return assembly.product
    
    new_product = Product(
        sku=assembly.assembly_name,
        name=f"Pump Assembly: {assembly.pump.pump_model}",
        description=f"Assembly for {assembly.pump.pump_model}. Includes Inertia Base: {assembly.inertia_base.model if assembly.inertia_base else 'N/A'}.",
        unit_price=0.00, # Placeholder price
        pump_assembly_id=assembly.id
    )
    db.session.add(new_product)
    db.session.commit()
    return new_product


@hvac_bp.route('/search_pumps', methods=['GET', 'POST'])
def search_pumps():
    """
    Provides a form to search for pump assemblies and displays the results.
    The 'option_id' is optional. If provided, the user can add assemblies to the quote.
    """
    option_id = request.args.get('option_id', type=int)
    deal_id = None

    if option_id:
        option = QuoteOption.query.get_or_404(option_id)
        deal_id = option.quote.recipient.deal_id

    form = PumpSearchForm(request.form)
    
    models = db.session.query(Pump.pump_model).distinct().order_by(Pump.pump_model).all()
    form.pump_models.choices = [(model[0], model[0]) for model in models]

    search_results = []
    if request.method == 'POST' and form.validate_on_submit():
        flow = form.flow.data
        head = form.head.data
        selected_models = form.pump_models.data
        
        base_flow, base_head = convert_to_base_units(
            flow, form.flow_units.data, head, form.head_units.data
        )
        
        TOLERANCE = 0.05
        
        query = PumpAssembly.query.join(Pump)

        if base_flow is not None and base_head is not None:
            query = query.filter(
                Pump.nominal_flow >= base_flow * (1 - TOLERANCE),
                Pump.nominal_flow <= base_flow * (1 + TOLERANCE),
                Pump.nominal_head >= base_head * (1 - TOLERANCE),
                Pump.nominal_head <= base_head * (1 + TOLERANCE)
            )

        if selected_models:
            query = query.filter(Pump.pump_model.in_(selected_models))

        search_results = query.order_by(PumpAssembly.assembly_name).all()

    return render_template('hvac/search_pumps.html', 
                           form=form, 
                           option_id=option_id, 
                           deal_id=deal_id,
                           results=search_results)

# --- API Endpoint for Adding Assembly to Quote ---

@hvac_bp.route('/api/add-assembly-to-option', methods=['POST'])
def add_assembly_to_option():
    """API endpoint to add a pump assembly to a quote option."""
    data = request.get_json()
    if not data or 'assembly_id' not in data or 'option_id' not in data:
        return jsonify({'success': False, 'message': 'Invalid request.'}), 400

    assembly = PumpAssembly.query.get(data['assembly_id'])
    option = QuoteOption.query.get(data['option_id'])

    if not assembly or not option:
        return jsonify({'success': False, 'message': 'Assembly or Option not found.'}), 404

    try:
        product = get_or_create_product_for_assembly(assembly)

        new_line_item = QuoteLineItem(
            option_id=option.id,
            product_id=product.id,
            quantity=1,
            unit_price=product.unit_price
        )
        db.session.add(new_line_item)
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Successfully added {assembly.assembly_name} to option.'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred.'}), 500