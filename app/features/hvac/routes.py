# app/features/hvac/routes.py

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app.extensions import db
from sqlalchemy import or_, func, desc
from flask_login import login_required

# This form is correctly imported from the local hvac forms file
from .forms import PumpSearchForm
from app.models import QuoteOption, Product, QuoteLineItem
# TODO: Uncomment when pump models are implemented
# from app.models.pumps import (
#     Pump, PumpSeries, PumpDutyPoint, PumpSelectionHistory,
#     InertiaBase, SeismicSpring, RubberMount, Crossbar,
#     MotorProtection, DripTripTray, PumpBOM
# )

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


@hvac_bp.route('/dashboard')
@login_required
def pump_dashboard():
    """
    Pump Management Dashboard
    Central hub for viewing all pump-related data
    """
    # Get statistics
    stats = {
        'total_pumps': Pump.query.filter_by(is_active=True).count(),
        'total_series': PumpSeries.query.filter_by(is_active=True).count(),
        'total_duty_points': PumpDutyPoint.query.count(),
        'total_selections': PumpSelectionHistory.query.count(),
        'total_inertia_bases': InertiaBase.query.filter_by(is_active=True).count(),
        'total_springs': SeismicSpring.query.filter_by(is_active=True).count(),
        'total_rubber_mounts': RubberMount.query.filter_by(is_active=True).count(),
        'total_crossbars': Crossbar.query.filter_by(is_active=True).count(),
    }
    
    # Get series breakdown
    series_breakdown = db.session.query(
        PumpSeries.series_code,
        PumpSeries.series_name,
        func.count(Pump.id).label('pump_count')
    ).outerjoin(Pump).group_by(PumpSeries.id, PumpSeries.series_code, PumpSeries.series_name).all()
    
    # Get recent duty points
    recent_duty_points = PumpDutyPoint.query.order_by(desc(PumpDutyPoint.created_at)).limit(10).all()
    
    # Get top selected pumps
    top_pumps = db.session.query(
        Pump,
        func.count(PumpSelectionHistory.id).label('selection_count')
    ).join(PumpSelectionHistory).group_by(Pump.id).order_by(desc('selection_count')).limit(10).all()
    
    return render_template('hvac/pump_dashboard.html',
                         stats=stats,
                         series_breakdown=series_breakdown,
                         recent_duty_points=recent_duty_points,
                         top_pumps=top_pumps)


@hvac_bp.route('/pumps')
@login_required
def view_all_pumps():
    """View all pumps with filtering and pagination"""
    page = request.args.get('page', 1, type=int)
    series_filter = request.args.get('series', type=int)
    search_query = request.args.get('q', '').strip()
    
    pump_query = Pump.query.filter_by(is_active=True)
    
    # Apply filters
    if series_filter:
        pump_query = pump_query.filter(Pump.series_id == series_filter)
    
    if search_query:
        search_filter = or_(
            Pump.name.ilike(f'%{search_query}%'),
            Pump.part_number.ilike(f'%{search_query}%'),
            Pump.item_number.ilike(f'%{search_query}%')
        )
        pump_query = pump_query.filter(search_filter)
    
    # Paginate
    pagination = pump_query.order_by(Pump.name).paginate(page=page, per_page=50, error_out=False)
    
    # Get all series for filter dropdown
    all_series = PumpSeries.query.filter_by(is_active=True).order_by(PumpSeries.series_code).all()
    
    return render_template('hvac/view_pumps.html',
                         pumps=pagination.items,
                         pagination=pagination,
                         all_series=all_series,
                         current_series=series_filter,
                         search_query=search_query)


@hvac_bp.route('/duty-points')
@login_required
def view_duty_points():
    """View all duty points with selection history"""
    page = request.args.get('page', 1, type=int)
    
    # Get duty points with selection counts
    duty_points = db.session.query(
        PumpDutyPoint,
        func.count(PumpSelectionHistory.id).label('selection_count')
    ).outerjoin(PumpSelectionHistory).group_by(PumpDutyPoint.id).order_by(
        desc('selection_count')
    ).paginate(page=page, per_page=30, error_out=False)
    
    return render_template('hvac/view_duty_points.html',
                         duty_points=duty_points.items,
                         pagination=duty_points)


@hvac_bp.route('/accessories')
@login_required
def view_accessories():
    """View all pump accessories and components"""
    # Get all accessories
    inertia_bases = InertiaBase.query.filter_by(is_active=True).order_by(InertiaBase.part_number).all()
    seismic_springs = SeismicSpring.query.filter_by(is_active=True).order_by(SeismicSpring.part_number).all()
    rubber_mounts = RubberMount.query.filter_by(is_active=True).order_by(RubberMount.sku).all()
    crossbars = Crossbar.query.filter_by(is_active=True).order_by(Crossbar.sku).all()
    
    return render_template('hvac/view_accessories.html',
                         inertia_bases=inertia_bases,
                         seismic_springs=seismic_springs,
                         rubber_mounts=rubber_mounts,
                         crossbars=crossbars)


@hvac_bp.route('/boms')
@login_required
def view_boms():
    """View pump BOMs and component relationships"""
    # Aggregate BOM data by pump (one row per pump)
    pump_bom_data = []
    pumps_with_bom = Pump.query.filter(Pump.is_active == True).join(PumpBOM).distinct().order_by(Pump.part_number).all()
    
    for pump in pumps_with_bom:
        pump_data = {
            'pump_id': pump.id,
            'pump_part': pump.part_number,
            'pump_name': pump.name,
            'series_code': pump.series.series_code if pump.series else '',
            'inertia_pn': None,
            'inertia_size': None,
            'spring_pn': None,
            'spring_qty': None
        }
        
        # Get BOM items for this pump
        for bom_item in pump.bom_items:
            if bom_item.component_type == 'inertia_base':
                base = InertiaBase.query.get(bom_item.component_id)
                if base:
                    pump_data['inertia_pn'] = base.part_number
                    if base.length_mm and base.width_mm and base.depth_mm:
                        pump_data['inertia_size'] = f"{base.length_mm} x {base.width_mm} x {base.depth_mm}"
            
            elif bom_item.component_type == 'seismic_spring':
                spring = SeismicSpring.query.get(bom_item.component_id)
                if spring:
                    pump_data['spring_pn'] = spring.part_number
                    pump_data['spring_qty'] = bom_item.quantity
        
        pump_bom_data.append(pump_data)
    
    all_series = PumpSeries.query.filter_by(is_active=True).order_by(PumpSeries.series_code).all()
    
    return render_template('hvac/view_boms.html',
                         pump_bom_data=pump_bom_data,
                         all_series=all_series)


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