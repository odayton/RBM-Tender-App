# app/features/deals/pump_routes.py

"""
Pump selection API routes for deals/quotes
Provides endpoints for intelligent pump selection based on duty points
"""

import re
import math
from flask import jsonify, request, flash, redirect, url_for, render_template
from flask_login import login_required, current_user
from sqlalchemy import or_, and_
from decimal import Decimal
from . import deals_bp
from app import db
from app.models.pumps import (
    Pump, PumpSeries, PumpDutyPoint, PumpSelectionHistory, 
    PumpConfidenceScore, InertiaBase, SeismicSpring, RubberMount, Crossbar
)
from app.core.core_logging import logger


def apply_margin(cost_price, margin_percentage):
    """
    Apply margin and round up to nearest dollar (matching frontend calculation)
    """
    price_with_margin = cost_price * (1 + margin_percentage / 100)
    # Round up to nearest dollar (matching Math.ceil in JavaScript)
    return math.ceil(price_with_margin)


@deals_bp.route('/api/pumps/search/duty-point', methods=['POST'])
def search_pumps_by_duty_point():
    """
    Search for pumps matching a duty point with historical confidence scores
    
    Request JSON:
    {
        "flow_rate": 21.0,
        "head_pressure": 200.0,
        "tolerance": 5.0,
        "series_id": null (optional),
        "poles": null (optional),
        "min_kw": null (optional),
        "max_kw": null (optional)
    }
    
    Returns:
    {
        "has_historical_data": true/false,
        "pumps": [...],
        "message": "..."
    }
    """
    try:
        data = request.get_json()
        flow_rate = float(data.get('flow_rate', 0))
        head_pressure = float(data.get('head_pressure', 0))
        tolerance = float(data.get('tolerance', 5.0))
        
        # Optional filters
        series_id = data.get('series_id')
        poles = data.get('poles')
        min_kw = data.get('min_kw')
        max_kw = data.get('max_kw')
        
        # Find matching duty points within tolerance
        matching_duty_points = find_duty_points_within_tolerance(
            flow_rate, head_pressure, tolerance
        )
        
        if not matching_duty_points:
            # NO HISTORICAL DATA FOUND
            return jsonify({
                'has_historical_data': False,
                'pumps': [],
                'message': f'No historical selections found for {flow_rate}L/s @ {head_pressure}kPa within ±{tolerance}%'
            })
        
        # Get pumps with confidence scores
        pumps_with_confidence = []
        for duty_point in matching_duty_points:
            pumps = get_pumps_for_duty_point(
                duty_point.id, series_id, poles, min_kw, max_kw
            )
            pumps_with_confidence.extend(pumps)
        
        # Remove duplicates and sort by confidence
        unique_pumps = {}
        for pump_data in pumps_with_confidence:
            pump_id = pump_data['id']
            if pump_id not in unique_pumps or pump_data['confidence_score'] > unique_pumps[pump_id]['confidence_score']:
                unique_pumps[pump_id] = pump_data
        
        results = sorted(unique_pumps.values(), key=lambda p: p['confidence_score'], reverse=True)
        
        return jsonify({
            'has_historical_data': True,
            'pumps': results,
            'duty_points_found': len(matching_duty_points)
        })
    
    except Exception as e:
        logger.error(f"Error in duty point search: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@deals_bp.route('/api/pumps/search/manual', methods=['GET'])
def search_pumps_manual():
    """
    Manual pump search by name, part number, or model
    
    Query params:
    - q: search query
    - series_id: optional series filter
    - limit: results limit (default 20)
    """
    try:
        query = request.args.get('q', '').strip()
        series_id = request.args.get('series_id', type=int)
        limit = request.args.get('limit', 20, type=int)
        
        if not query or len(query) < 2:
            return jsonify([])
        
        # Search across multiple fields
        search_filter = or_(
            Pump.name.ilike(f'%{query}%'),
            Pump.part_number.ilike(f'%{query}%'),
            Pump.item_number.ilike(f'%{query}%')
        )
        
        pump_query = Pump.query.filter(
            search_filter,
            Pump.is_active == True
        )
        
        # Apply series filter if provided
        if series_id:
            pump_query = pump_query.filter(Pump.series_id == series_id)
        
        pumps = pump_query.limit(limit).all()
        
        results = []
        for pump in pumps:
            results.append({
                'id': pump.id,
                'part_number': pump.part_number,
                'item_number': pump.item_number,
                'name': pump.name,
                'kw_rating': float(pump.kw_rating) if pump.kw_rating else None,
                'poles': pump.poles,
                'nett_price': float(pump.nett_price) if pump.nett_price else None,
                'series_code': pump.series.series_code if pump.series else None,
                'pump_curve_url': pump.get_pump_curve_url()
            })
        
        return jsonify(results)
    
    except Exception as e:
        logger.error(f"Error in manual search: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@deals_bp.route('/api/pumps/browse', methods=['GET'])
def browse_all_pumps():
    """
    Browse all pumps with filtering
    
    Query params:
    - series_id: filter by series
    - poles: filter by poles
    - min_kw, max_kw: filter by kW range
    - page: page number (default 1)
    - per_page: results per page (default 20)
    """
    try:
        series_id = request.args.get('series_id', type=int)
        poles = request.args.get('poles', type=int)
        min_kw = request.args.get('min_kw', type=float)
        max_kw = request.args.get('max_kw', type=float)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        pump_query = Pump.query.filter(Pump.is_active == True)
        
        # Apply filters
        if series_id:
            pump_query = pump_query.filter(Pump.series_id == series_id)
        if poles:
            pump_query = pump_query.filter(Pump.poles == poles)
        if min_kw:
            pump_query = pump_query.filter(Pump.kw_rating >= min_kw)
        if max_kw:
            pump_query = pump_query.filter(Pump.kw_rating <= max_kw)
        
        # Paginate
        pagination = pump_query.paginate(page=page, per_page=per_page, error_out=False)
        
        results = []
        for pump in pagination.items:
            results.append({
                'id': pump.id,
                'part_number': pump.part_number,
                'item_number': pump.item_number,
                'name': pump.name,
                'kw_rating': float(pump.kw_rating) if pump.kw_rating else None,
                'poles': pump.poles,
                'nett_price': float(pump.nett_price) if pump.nett_price else None,
                'series_code': pump.series.series_code if pump.series else None,
                'pump_curve_url': pump.get_pump_curve_url()
            })
        
        return jsonify({
            'pumps': results,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        })
    
    except Exception as e:
        logger.error(f"Error browsing pumps: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


def _get_pump_components_data(pump_id):
    """
    Get BOM components for a specific pump
    Returns default configuration with all available components
    """
    try:
        pump = Pump.query.get_or_404(pump_id)
        
        # Build component configuration
        components = {
            'pump': {
                'id': pump.id,
                'name': pump.name,
                'part_number': pump.part_number,
                'item_number': pump.item_number,
                'kw_rating': float(pump.kw_rating) if pump.kw_rating else None,
                'poles': pump.poles,
                'nett_price': float(pump.nett_price) if pump.nett_price else 0,
                'pump_curve_url': pump.get_pump_curve_url()
            },
            'inertia_base': None,
            'spring_standard': None,
            'spring_50mm': None,
            'mounting_options': [],
            'spring_options': [],
            'accessories': []
        }
        
        # Try to get BOM data from new PumpBOM model first
        bom_items = pump.bom_items if hasattr(pump, 'bom_items') else []
        
        if bom_items:
            # Process new BOM structure
            for bom_item in bom_items:
                if bom_item.component_type == 'inertia_base':
                    inertia_base = InertiaBase.query.get(bom_item.component_id)
                    if inertia_base:
                        components['inertia_base'] = {
                            'id': inertia_base.id,
                            'part_number': inertia_base.part_number,
                            'description': inertia_base.description,
                            'dimensions': inertia_base.dimensions_display,
                            'length_mm': inertia_base.length_mm,
                            'width_mm': inertia_base.width_mm,
                            'depth_mm': inertia_base.depth_mm,
                            'nett_cost': float(inertia_base.nett_cost) if inertia_base.nett_cost else 741.99,
                            'list_price': float(inertia_base.list_price) if inertia_base.list_price else None,
                            'quantity': bom_item.quantity
                        }
                elif bom_item.component_type == 'seismic_spring':
                    spring = SeismicSpring.query.get(bom_item.component_id)
                    if spring:
                        spring_data = {
                            'id': spring.id,
                            'part_number': spring.part_number,
                            'description': spring.description,
                            'max_load_kg': float(spring.max_load_kg) if spring.max_load_kg else None,
                            'static_deflection_mm': float(spring.static_deflection_mm) if spring.static_deflection_mm else None,
                            'nett_price': float(spring.nett_price) if spring.nett_price else 153.30,
                            'list_price': float(spring.list_price) if spring.list_price else None,
                            'quantity': bom_item.quantity
                        }
                        # Determine spring type based on static deflection or description
                        if spring.static_deflection_mm and spring.static_deflection_mm >= 50:
                            components['spring_50mm'] = spring_data
                        else:
                            components['spring_standard'] = spring_data
        else:
            # Fallback to old BOM table structure using raw SQL
            try:
                from app.core.core_database import db
                
                # Query old BOM table using pump's item_number/part_number as pump_sku
                pump_sku = pump.item_number or pump.part_number
                logger.info(f"Querying old BOM table for pump_sku: {pump_sku}")
                
                result = db.session.execute(
                    db.text("""
                        SELECT 
                            b.inertia_base_part_number,
                            b.seismic_spring_part_number,
                            b.spring_quantity
                        FROM bom b
                        WHERE b.pump_sku = :pump_sku
                    """),
                    {'pump_sku': pump_sku}
                ).fetchone()
                
                logger.info(f"BOM query result: {result}")
                
                if result:
                    # Get inertia base - access by index since we're using text() query
                    inertia_part_number = result[0] if len(result) > 0 else None
                    
                    if inertia_part_number:
                        inertia_base = InertiaBase.query.filter_by(
                            part_number=str(inertia_part_number).strip()
                        ).first()
                        if inertia_base:
                            components['inertia_base'] = {
                                'id': inertia_base.id,
                                'part_number': inertia_base.part_number,
                                'description': inertia_base.description,
                                'dimensions': inertia_base.dimensions_display,
                                'length_mm': inertia_base.length_mm,
                                'width_mm': inertia_base.width_mm,
                                'depth_mm': inertia_base.depth_mm,
                                'nett_cost': float(inertia_base.nett_cost) if inertia_base.nett_cost else 741.99,
                                'list_price': float(inertia_base.list_price) if inertia_base.list_price else None,
                                'quantity': 1
                            }
                    
                    # Get seismic spring
                    spring_part_number = result[1] if len(result) > 1 else None  # Access by index
                    spring_qty = result[2] if len(result) > 2 else 4  # Access by index
                    
                    logger.info(f"Spring part number from BOM: {spring_part_number}, qty: {spring_qty}")
                    
                    if spring_part_number:
                        spring = SeismicSpring.query.filter_by(
                            part_number=str(spring_part_number).strip()
                        ).first()
                        
                        logger.info(f"Spring found: {spring}")
                        
                        if spring:
                            spring_data = {
                                'id': spring.id,
                                'part_number': spring.part_number,
                                'description': spring.description,
                                'max_load_kg': float(spring.max_load_kg) if spring.max_load_kg else None,
                                'static_deflection_mm': float(spring.static_deflection_mm) if spring.static_deflection_mm else None,
                                'nett_price': float(spring.nett_price) if spring.nett_price else 153.30,
                                'list_price': float(spring.list_price) if spring.list_price else None,
                                'quantity': spring_qty
                            }
                            # Determine spring type based on static deflection or description
                            if spring.static_deflection_mm and spring.static_deflection_mm >= 50:
                                components['spring_50mm'] = spring_data
                            else:
                                components['spring_standard'] = spring_data
            except Exception as e:
                logger.warning(f"Could not query old BOM table: {e}")
        
        return components
    
    except Exception as e:
        logger.error(f"Error getting pump components: {e}", exc_info=True)
        return None


@deals_bp.route('/api/pumps/<int:pump_id>/components', methods=['GET'])
def get_pump_components(pump_id):
    """
    API endpoint to get BOM components for a specific pump
    """
    components = _get_pump_components_data(pump_id)
    if components:
        return jsonify(components)
    else:
        return jsonify({'error': 'Failed to get pump components'}), 500


@deals_bp.route('/api/pump-series', methods=['GET'])
def get_pump_series():
    """Get all active pump series for filters"""
    try:
        series = PumpSeries.query.filter_by(is_active=True).order_by(PumpSeries.series_code).all()
        
        results = []
        for s in series:
            results.append({
                'id': s.id,
                'code': s.series_code,
                'name': s.series_name
            })
        
        return jsonify(results)
    
    except Exception as e:
        logger.error(f"Error getting pump series: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


# Helper functions

def find_duty_points_within_tolerance(flow_rate, head_pressure, tolerance):
    """Find duty points within tolerance range"""
    flow_min = flow_rate * (1 - tolerance / 100)
    flow_max = flow_rate * (1 + tolerance / 100)
    head_min = head_pressure * (1 - tolerance / 100)
    head_max = head_pressure * (1 + tolerance / 100)
    
    duty_points = PumpDutyPoint.query.filter(
        and_(
            PumpDutyPoint.flow_rate_lps >= flow_min,
            PumpDutyPoint.flow_rate_lps <= flow_max,
            PumpDutyPoint.head_pressure_kpa >= head_min,
            PumpDutyPoint.head_pressure_kpa <= head_max
        )
    ).all()
    
    return duty_points


def get_pumps_for_duty_point(duty_point_id, series_id=None, poles=None, min_kw=None, max_kw=None):
    """Get pumps with confidence scores for a duty point"""
    # Get confidence scores for this duty point
    scores = PumpConfidenceScore.query.filter_by(
        duty_point_id=duty_point_id
    ).join(Pump).filter(Pump.is_active == True)
    
    # Apply filters
    if series_id:
        scores = scores.filter(Pump.series_id == series_id)
    if poles:
        scores = scores.filter(Pump.poles == poles)
    if min_kw:
        scores = scores.filter(Pump.kw_rating >= min_kw)
    if max_kw:
        scores = scores.filter(Pump.kw_rating <= max_kw)
    
    scores = scores.all()
    
    results = []
    for score in scores:
        pump = score.pump
        results.append({
            'id': pump.id,
            'part_number': pump.part_number,
            'item_number': pump.item_number,
            'name': pump.name,
            'kw_rating': float(pump.kw_rating) if pump.kw_rating else None,
            'poles': pump.poles,
            'nett_price': float(pump.nett_price) if pump.nett_price else None,
            'series_code': pump.series.series_code if pump.series else None,
            'pump_curve_url': pump.get_pump_curve_url(),
            'confidence_score': float(score.confidence_score) if score.confidence_score else 0,
            'confidence_stars': score.confidence_stars or 0,
            'selection_count': score.selection_count,
            'success_rate': float(score.success_count / score.selection_count * 100) if score.selection_count > 0 else 0,
            'flow_match': float(score.flow_rate_match_percentage) if score.flow_rate_match_percentage else 0,
            'head_match': float(score.head_pressure_match_percentage) if score.head_pressure_match_percentage else 0
        })
    
    return results


@deals_bp.route('/api/pump-assembly/<int:line_item_id>/view', methods=['GET'])
@login_required
def view_pump_assembly(line_item_id):
    """
    View/Edit pump assembly configuration for an existing line item
    Returns JSON data about the pump to populate the configuration modal
    """
    try:
        from app.models import QuoteLineItem
        
        # Get the line item
        line_item = QuoteLineItem.query.get_or_404(line_item_id)
        
        # Get the option and deal for context
        option = line_item.option
        quote = option.quote
        recipient = quote.recipient
        deal = recipient.deal
        
        # Get the pump from the line item's custom_name
        pump = None
        
        # Extract pump name from "  • Pump: [name]" format
        if line_item.custom_name and line_item.custom_name.startswith('  • Pump: '):
            pump_name = line_item.custom_name.replace('  • Pump: ', '').strip()
            pump = Pump.query.filter_by(name=pump_name).first()
        
        # If still not found, try to get from custom_sku
        if not pump and line_item.custom_sku and line_item.custom_sku != 'PUMP':
            # Try as pump ID first
            try:
                pump_id = int(line_item.custom_sku)
                pump = Pump.query.get(pump_id)
            except (ValueError, TypeError):
                pass
            
            # If that fails, try as part_number or item_number
            if not pump:
                pump = Pump.query.filter(
                    (Pump.part_number == line_item.custom_sku) | 
                    (Pump.item_number == line_item.custom_sku)
                ).first()
        
        if not pump:
            return jsonify({
                'success': False, 
                'error': f'Could not find pump for line item. Name: {line_item.custom_name}, SKU: {line_item.custom_sku}'
            }), 404
        
        # Get pump components for the modal
        pump_components = _get_pump_components_data(pump.id)
        
        # Find the assembly header to get stored configuration
        assembly_header = None
        for item in sorted(option.line_items, key=lambda x: x.display_order):
            if item.display_order < line_item.display_order:
                if item.custom_name and ':' in item.custom_name and not item.custom_name.startswith('  •'):
                    assembly_header = item
            elif item.display_order >= line_item.display_order:
                break
        
        # Try to load configuration from assembly header
        import json
        config = {}
        if assembly_header:
            # First try assembly_metadata (new location)
            if hasattr(assembly_header, 'assembly_metadata') and assembly_header.assembly_metadata:
                try:
                    config = json.loads(assembly_header.assembly_metadata)
                    logger.info(f"Loaded saved configuration from assembly_metadata: {config}")
                except (json.JSONDecodeError, TypeError) as e:
                    logger.warning(f"Could not parse configuration from assembly_metadata: {e}")
            # Fall back to notes (legacy location) if assembly_metadata is empty
            elif assembly_header.notes:
                try:
                    config = json.loads(assembly_header.notes)
                    logger.info(f"Loaded saved configuration from notes (legacy): {config}")
                except (json.JSONDecodeError, TypeError) as e:
                    logger.warning(f"Could not parse configuration from notes: {e}")
                    config = {}
        
        # Return pump data as JSON with saved configuration
        return jsonify({
            'success': True,
            'pump_id': pump.id,
            'option_id': option.id,
            'line_item_id': line_item_id,
            'is_update': True,
            'pump': {
                'id': pump.id,
                'name': pump.name,
                'part_number': pump.part_number,
                'sell_price': float(pump.list_price) if pump.list_price else float(pump.nett_price) if pump.nett_price else 0,
                'cost_price': float(pump.nett_price) if pump.nett_price else 0,
                'kw': float(pump.kw_rating) if pump.kw_rating else None,
                'poles': pump.poles,
                'curve_link': pump.get_pump_curve_url() if hasattr(pump, 'get_pump_curve_url') else None
            },
            'components': pump_components,
            'config': config  # Include the saved configuration
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Error viewing pump assembly {line_item_id}: {e}")
        logger.error(f"Full traceback: {error_details}")
        return jsonify({
            'success': False, 
            'error': str(e),
            'details': error_details
        }), 500


@deals_bp.route('/api/pump-assembly/<int:line_item_id>/update', methods=['POST'])
@login_required
def update_pump_assembly(line_item_id):
    """
    Update existing pump assembly configuration
    Deletes old components and creates new ones based on updated configuration
    """
    try:
        from app.models import QuoteLineItem, QuoteOption
        from flask_login import current_user
        
        logger.info("="*100)
        logger.info(f"DEBUG UPDATE PUMP ASSEMBLY: Starting update for line_item_id={line_item_id}")
        
        # Get the existing pump detail line item
        pump_line_item = QuoteLineItem.query.get_or_404(line_item_id)
        option = pump_line_item.option
        quote = option.quote
        recipient = quote.recipient
        deal = recipient.deal
        
        logger.info(f"DEBUG: Received line_item - id={pump_line_item.id}, name='{pump_line_item.custom_name}', sku='{pump_line_item.custom_sku}', price=${pump_line_item.unit_price}, order={pump_line_item.display_order}")
        
        # Get the new configuration data
        data = request.get_json()
        
        # Extract pump ID from the data
        pump_id = data.get('pump_id')
        if not pump_id:
            return jsonify({'success': False, 'error': 'Pump ID is required'}), 400
        
        # Get the pump
        pump = Pump.query.get_or_404(pump_id)
        logger.info(f"DEBUG: Pump - id={pump.id}, name='{pump.name}', item_number={pump.item_number} (type={type(pump.item_number).__name__})")
        
        # Get configuration
        plant_reference = data.get('plant_reference', '').strip()
        assembly_description = data.get('assembly_description', '').strip()
        margin_percentage = float(data.get('margin_percentage', 18.5))
        mounting_type = data.get('mounting_type', 'inertia_base')
        crossbar_quantity = int(data.get('crossbar_quantity', 2))
        spring_type = data.get('spring_type', 'standard')
        spring_quantity = int(data.get('spring_quantity', 4))
        include_rubber_mounts = data.get('include_rubber_mounts', True)
        rubber_mount_quantity = int(data.get('rubber_mount_quantity', 4))
        include_motor_protection = data.get('include_motor_protection', False)
        include_drip_tray = data.get('include_drip_tray', False)
        
        logger.info(f"DEBUG: Configuration - plant_ref='{plant_reference}', margin={margin_percentage}%, mounting={mounting_type}")
        
        # Find the assembly header (the parent line item)
        assembly_header = None
        assembly_start_order = pump_line_item.display_order
        
        logger.info(f"DEBUG: Looking for assembly header before order {pump_line_item.display_order}")
        logger.info(f"DEBUG: All line items in option:")
        for item in sorted(option.line_items, key=lambda x: x.display_order):
            logger.info(f"  Order {item.display_order}: id={item.id}, name='{item.custom_name}', sku='{item.custom_sku}', price=${item.unit_price}")
        
        # Look backwards to find the assembly header
        for item in sorted(option.line_items, key=lambda x: x.display_order):
            if item.display_order < pump_line_item.display_order:
                if item.custom_name and ':' in item.custom_name and not item.custom_name.startswith('  •'):
                    assembly_header = item
                    logger.info(f"DEBUG: Found potential assembly header: id={item.id}, name='{item.custom_name}'")
            elif item.display_order > pump_line_item.display_order:
                # Found items after pump_line_item, stop searching for header
                break
        
        if assembly_header:
            logger.info(f"DEBUG: Assembly header confirmed: id={assembly_header.id}, name='{assembly_header.custom_name}', sku='{assembly_header.custom_sku}', price=${assembly_header.unit_price}, order={assembly_header.display_order}")
        else:
            logger.warning(f"DEBUG: NO ASSEMBLY HEADER FOUND!")
        
        # Find all components that belong to this assembly
        components_to_delete = []
        if assembly_header:
            assembly_start_order = assembly_header.display_order
            # Find all sub-items after the header until we hit another header or end
            logger.info(f"DEBUG: Looking for components to delete after order {assembly_header.display_order}")
            for item in sorted(option.line_items, key=lambda x: x.display_order):
                if item.display_order > assembly_header.display_order:
                    if item.custom_name and item.custom_name.startswith('  •'):
                        components_to_delete.append(item)
                        logger.info(f"DEBUG: Marked for deletion: id={item.id}, name='{item.custom_name}', price=${item.unit_price}")
                    elif item.custom_name and ':' in item.custom_name and not item.custom_name.startswith('  •'):
                        # Hit another assembly header, stop
                        logger.info(f"DEBUG: Stopped at next assembly header: '{item.custom_name}'")
                        break
        
        logger.info(f"DEBUG: Total components marked for deletion: {len(components_to_delete)}")
        
        # Delete old component line items
        for comp in components_to_delete:
            logger.info(f"DEBUG: Deleting component: id={comp.id}, name='{comp.custom_name}'")
            db.session.delete(comp)
        db.session.flush()
        logger.info(f"DEBUG: All old components deleted and flushed")
        
        # Calculate new prices
        # Use nett_price (cost price) as the base, not list_price
        pump_price = float(pump.nett_price) if pump.nett_price else float(pump.list_price) if pump.list_price else 0
        pump_sell_price = apply_margin(pump_price, margin_percentage)
        
        logger.info(f"DEBUG: Price calculation - pump_price=${pump_price} (from nett_price), margin={margin_percentage}%, pump_sell_price=${pump_sell_price}")
        
        # Track total assembly price
        total_assembly_price = Decimal(str(pump_sell_price))
        logger.info(f"DEBUG: Starting total_assembly_price=${total_assembly_price}")
        
        # Start creating new components at the order after assembly header
        current_order = assembly_start_order + 1
        line_items_created = []
        
        # 1. Add the pump detail line
        # Format item number properly (remove .0 if present)
        if pump.item_number:
            # Handle both numeric types and string types
            try:
                # Try to convert to int first (handles both numeric and string types)
                item_sku = str(int(float(pump.item_number)))
            except (ValueError, TypeError):
                # Fall back to string representation
                item_sku = str(pump.item_number)
        else:
            item_sku = str(pump.part_number) if pump.part_number else "PUMP"
        
        logger.info(f"DEBUG: Formatted item_sku='{item_sku}' from pump.item_number={pump.item_number}")
        
        pump_detail_line = QuoteLineItem(
            option_id=option.id,
            product_id=None,
            custom_sku=item_sku,
            custom_name=f"  • Pump: {pump.name}",
            custom_description=f"Pump Model: {pump.name}",
            quantity=1,
            unit_price=Decimal(str(pump_sell_price)),
            discount=Decimal('0'),
            display_order=current_order,
            notes=""
        )
        db.session.add(pump_detail_line)
        line_items_created.append(pump_detail_line)
        logger.info(f"DEBUG: Created new pump detail line: id=PENDING, name='{pump_detail_line.custom_name}', sku='{pump_detail_line.custom_sku}', price=${pump_detail_line.unit_price}, order={current_order}")
        current_order += 1
        
        # 2. Add mounting component
        if mounting_type == 'inertia_base':
            # Get inertia base from BOM
            bom_items = pump.bom_items if hasattr(pump, 'bom_items') else []
            inertia_base_item = next((item for item in bom_items if item.component_type == 'inertia_base'), None)
            
            if inertia_base_item:
                inertia_base = InertiaBase.query.get(inertia_base_item.component_id)
                if inertia_base:
                    base_cost = float(inertia_base.nett_cost) if inertia_base.nett_cost else 741.99
                    base_sell_price = apply_margin(base_cost, margin_percentage)
                    total_assembly_price += Decimal(str(base_sell_price))
                    
                    base_line = QuoteLineItem(
                        option_id=option.id,
                        product_id=None,
                        custom_sku=inertia_base.part_number,
                        custom_name=f"  • Inertia Base: {inertia_base.description or 'Type IB-4'}",
                        quantity=1,
                        unit_price=Decimal(str(base_sell_price)),
                        discount=Decimal('0'),
                        display_order=current_order
                    )
                    db.session.add(base_line)
                    line_items_created.append(base_line)
                    current_order += 1
        
        elif mounting_type == 'crossbar':
            # Get crossbar from BOM
            bom_items = pump.bom_items if hasattr(pump, 'bom_items') else []
            crossbar_item = next((item for item in bom_items if item.component_type == 'crossbar'), None)
            
            if crossbar_item:
                crossbar = Crossbar.query.get(crossbar_item.component_id)
                if crossbar:
                    crossbar_cost = float(crossbar.nett_price) if crossbar.nett_price else 142.38
                    crossbar_sell_price = apply_margin(crossbar_cost, margin_percentage)
                    total_crossbar_price = Decimal(str(crossbar_sell_price)) * crossbar_quantity
                    total_assembly_price += total_crossbar_price
                    
                    crossbar_line = QuoteLineItem(
                        option_id=option.id,
                        product_id=None,
                        custom_sku=crossbar.part_number,
                        custom_name=f"  • Crossbar: {crossbar.description or 'Crossbar Alternative'}",
                        quantity=crossbar_quantity,
                        unit_price=Decimal(str(crossbar_sell_price)),
                        discount=Decimal('0'),
                        display_order=current_order
                    )
                    db.session.add(crossbar_line)
                    line_items_created.append(crossbar_line)
                    current_order += 1
        
        # 3. Add seismic springs
        if spring_type != 'none' and spring_quantity > 0:
            # Get spring from BOM
            bom_items = pump.bom_items if hasattr(pump, 'bom_items') else []
            spring_item = next((item for item in bom_items if item.component_type == 'seismic_spring'), None)
            
            if spring_item:
                spring = SeismicSpring.query.get(spring_item.component_id)
                if spring:
                    spring_cost = float(spring.nett_price) if spring.nett_price else 76.00
                    spring_sell_price = apply_margin(spring_cost, margin_percentage)
                    total_spring_price = Decimal(str(spring_sell_price)) * spring_quantity
                    total_assembly_price += total_spring_price
                    
                    spring_line = QuoteLineItem(
                        option_id=option.id,
                        product_id=None,
                        custom_sku=spring.part_number,
                        custom_name=f"  • Seismic Springs: {spring.description or 'Standard'}",
                        quantity=spring_quantity,
                        unit_price=Decimal(str(spring_sell_price)),
                        discount=Decimal('0'),
                        display_order=current_order
                    )
                    db.session.add(spring_line)
                    line_items_created.append(spring_line)
                    current_order += 1
        
        # 4. Add rubber mounts
        if include_rubber_mounts and rubber_mount_quantity > 0:
            # Get rubber mount from BOM
            bom_items = pump.bom_items if hasattr(pump, 'bom_items') else []
            mount_item = next((item for item in bom_items if item.component_type == 'rubber_mount'), None)
            
            if mount_item:
                mount = RubberMount.query.get(mount_item.component_id)
                if mount:
                    mount_cost = float(mount.nett_price) if mount.nett_price else 11.83
                    mount_sell_price = apply_margin(mount_cost, margin_percentage)
                    total_mount_price = Decimal(str(mount_sell_price)) * rubber_mount_quantity
                    total_assembly_price += total_mount_price
                    
                    mount_line = QuoteLineItem(
                        option_id=option.id,
                        product_id=None,
                        custom_sku=mount.part_number,
                        custom_name=f"  • Rubber Mounts: {mount.description or 'Vibration Isolators'}",
                        quantity=rubber_mount_quantity,
                        unit_price=Decimal(str(mount_sell_price)),
                        discount=Decimal('0'),
                        display_order=current_order
                    )
                    db.session.add(mount_line)
                    line_items_created.append(mount_line)
                    current_order += 1
        
        # 5. Add motor protection if requested
        if include_motor_protection:
            motor_protection_cost = 125.00
            motor_protection_sell = apply_margin(motor_protection_cost, margin_percentage)
            total_assembly_price += Decimal(str(motor_protection_sell))
            
            mp_line = QuoteLineItem(
                option_id=option.id,
                product_id=None,
                custom_sku='MP-STD',
                custom_name=f"  • Motor Protection: Standard",
                quantity=1,
                unit_price=Decimal(str(motor_protection_sell)),
                discount=Decimal('0'),
                display_order=current_order
            )
            db.session.add(mp_line)
            line_items_created.append(mp_line)
            current_order += 1
        
        # 6. Add drip tray if requested
        if include_drip_tray:
            drip_tray_cost = 85.00
            drip_tray_sell = apply_margin(drip_tray_cost, margin_percentage)
            total_assembly_price += Decimal(str(drip_tray_sell))
            
            dt_line = QuoteLineItem(
                option_id=option.id,
                product_id=None,
                custom_sku='DT-STD',
                custom_name=f"  • Drip Trip Tray: Standard",
                quantity=1,
                unit_price=Decimal(str(drip_tray_sell)),
                discount=Decimal('0'),
                display_order=current_order
            )
            db.session.add(dt_line)
            line_items_created.append(dt_line)
            current_order += 1
        
        # 7. Update the assembly header with new total price and plant reference
        logger.info(f"DEBUG: Before header update - total_assembly_price=${total_assembly_price}")
        logger.info(f"DEBUG: Created {len(line_items_created)} new components")
        
        if assembly_header:
            logger.info(f"DEBUG: Updating assembly header id={assembly_header.id}")
            logger.info(f"DEBUG: Old header price=${assembly_header.unit_price}, new price=${total_assembly_price}")
            assembly_header.unit_price = total_assembly_price
            
            # Update plant reference if provided
            if plant_reference:
                # Assembly header format: "Pump Name: Plant Ref"
                old_name = assembly_header.custom_name
                old_sku = assembly_header.custom_sku
                assembly_header.custom_name = f"{pump.name}: {plant_reference}"
                # Format item number properly (remove .0 if present)
                if pump.item_number:
                    try:
                        item_no = str(int(float(pump.item_number)))
                    except (ValueError, TypeError):
                        item_no = str(pump.item_number)
                else:
                    item_no = str(pump.part_number) if pump.part_number else "PUMP"
                assembly_header.custom_sku = item_no
                logger.info(f"DEBUG: Updated header name: '{old_name}' -> '{assembly_header.custom_name}'")
                logger.info(f"DEBUG: Updated header SKU: '{old_sku}' -> '{assembly_header.custom_sku}'")
            
            # Store the updated configuration in the assembly_metadata field as JSON
            import json
            config_data = {
                'pump_id': pump_id,
                'margin_percentage': margin_percentage,
                'mounting_type': mounting_type,
                'crossbar_quantity': crossbar_quantity,
                'spring_type': spring_type,
                'spring_quantity': spring_quantity,
                'include_rubber_mounts': include_rubber_mounts,
                'rubber_mount_quantity': rubber_mount_quantity,
                'include_motor_protection': include_motor_protection,
                'include_drip_tray': include_drip_tray,
                'assembly_description': assembly_description
            }
            assembly_header.assembly_metadata = json.dumps(config_data)
            logger.info(f"DEBUG: Stored config in assembly_metadata")
        
        # Commit all changes
        logger.info(f"DEBUG: Committing changes to database...")
        db.session.commit()
        logger.info(f"DEBUG: Commit successful!")
        logger.info("="*100)
        
        logger.info(f"User {current_user.email} updated pump assembly (header: {assembly_header.id if assembly_header else 'N/A'}, created {len(line_items_created)} components)")
        
        return jsonify({
            'success': True,
            'message': 'Pump assembly updated successfully',
            'components_updated': len(line_items_created)
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating pump assembly {line_item_id}: {e}", exc_info=True)
        import traceback
        return jsonify({
            'success': False, 
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@deals_bp.route('/api/pump-assembly/add', methods=['POST'])
def add_pump_assembly_to_quote():
    """
    Add pump assembly with plant reference to quote
    
    Request JSON:
    {
        "pump_id": 1,
        "option_id": 5,
        "plant_reference": "CHWP-01",
        "assembly_description": "Complete assembly with mounting",
        "quantity": 1,
        "margin_percentage": 18.5,
        "mounting_type": "inertia_base",
        "crossbar_quantity": 2,
        "spring_type": "standard",
        "spring_quantity": 4,
        "include_rubber_mounts": true,
        "rubber_mount_quantity": 4,
        "include_motor_protection": false,
        "include_drip_tray": false,
        "ip_rating": "standard"
    }
    """
    try:
        from app.models import QuoteOption, QuoteLineItem, Product
        from flask_login import current_user
        
        data = request.get_json()
        
        # Validate required fields
        pump_id = data.get('pump_id')
        option_id = data.get('option_id')
        plant_reference = data.get('plant_reference', '').strip()
        
        if not pump_id or not option_id:
            return jsonify({'success': False, 'error': 'Missing pump_id or option_id'}), 400
        
        if not plant_reference:
            return jsonify({'success': False, 'error': 'Plant reference is required'}), 400
        
        # Get the pump and quote option
        pump = Pump.query.get_or_404(pump_id)
        option = QuoteOption.query.get_or_404(option_id)
        
        # Get configuration
        quantity = int(data.get('quantity', 1))
        assembly_description = data.get('assembly_description', '').strip()
        margin_percentage = float(data.get('margin_percentage', 18.5))
        
        # Component configuration
        mounting_type = data.get('mounting_type', 'inertia_base')
        crossbar_quantity = int(data.get('crossbar_quantity', 2))
        spring_type = data.get('spring_type', 'standard')
        spring_quantity = int(data.get('spring_quantity', 4))
        include_rubber_mounts = data.get('include_rubber_mounts', False)
        rubber_mount_quantity = int(data.get('rubber_mount_quantity', 4))
        include_motor_protection = data.get('include_motor_protection', False)
        include_drip_tray = data.get('include_drip_tray', False)
        ip_rating = data.get('ip_rating', 'standard')
        
        # Get the next display order for line items
        max_order = db.session.query(db.func.max(QuoteLineItem.display_order)).filter_by(
            option_id=option_id
        ).scalar() or 0
        
        assemblies_added = []
        
        # Use the plant reference exactly as provided by user
        current_ref = plant_reference
        
        # Calculate prices with margin (matching frontend calculation)
        pump_cost = float(pump.nett_price) if pump.nett_price else 0
        pump_sell_price = apply_margin(pump_cost, margin_percentage)
        
        logger.info(f"Pump pricing: Cost=${pump_cost:.2f}, Margin={margin_percentage}%, Sell=${pump_sell_price}")
        
        # Create line items for this assembly
        line_items_created = []
        current_order = max_order + 1
        total_assembly_price = Decimal('0')  # Track total price for assembly header
        
        # 1. Add pump with new format: Item No + Pump Name: Plant Ref
        # Format item number properly (remove .0 if present)
        if pump.item_number:
            try:
                item_sku = str(int(float(pump.item_number)))
            except (ValueError, TypeError):
                item_sku = str(pump.item_number)
        elif pump.part_number:
            item_sku = str(pump.part_number)
        else:
            item_sku = "PUMP"
        
        # Create the new format: Pump Name: Plant Ref (without part number)
        # Add a hidden marker to identify this as a pump assembly
        assembly_name = f"{pump.name}: {current_ref}"
        
        # Add pump price to total
        total_assembly_price += Decimal(str(pump_sell_price))
        
        pump_line = QuoteLineItem(
            option_id=option_id,
            product_id=None,  # Custom item
            custom_sku=item_sku,  # Already formatted as string
            custom_name=assembly_name,  # New format: Item No + Pump Name: Plant Ref (shown when collapsed)
            custom_description="",  # Blank description - will be hidden when expanded
            quantity=quantity,  # Use the quantity specified by user
            unit_price=Decimal('0'),  # Will be updated after all components are calculated
            discount=Decimal('0'),
            display_order=current_order,
            notes=""  # Blank notes as requested
        )
        db.session.add(pump_line)
        line_items_created.append(('Pump Assembly Header', pump_line))
        current_order += 1
        
        # Add the actual pump as a sub-item (first item when expanded) - this gets the price
        pump_detail_line = QuoteLineItem(
            option_id=option_id,
            product_id=None,
            custom_sku=item_sku,  # Already formatted as string
            custom_name=f"  • Pump: {pump.name}",
            custom_description=f"Pump Model: {pump.name}",
            quantity=1,
            unit_price=Decimal(str(pump_sell_price)),  # Price moved here from header
            discount=Decimal('0'),
            display_order=current_order,
            notes=""
        )
        db.session.add(pump_detail_line)
        line_items_created.append(('Pump Detail', pump_detail_line))
        current_order += 1
        
        # 2. Add mounting component
        if mounting_type == 'inertia_base':
            # Get inertia base from BOM
            inertia_base = get_component_for_pump(pump, 'inertia_base')
            if inertia_base:
                base_cost = float(inertia_base.get('nett_cost', 741.99))
                base_sell_price = apply_margin(base_cost, margin_percentage)
                
                # Add to total assembly price
                total_assembly_price += Decimal(str(base_sell_price))
                
                base_line = QuoteLineItem(
                    option_id=option_id,
                    product_id=None,
                    custom_sku=inertia_base.get('part_number', 'IB-BASE'),
                    custom_name=f"  • Inertia Base: {inertia_base.get('description', 'Type IB-4')}",
                    quantity=1,
                    unit_price=Decimal(str(base_sell_price)),
                    discount=Decimal('0'),
                    display_order=current_order
                )
                db.session.add(base_line)
                line_items_created.append(('Inertia Base', base_line))
                current_order += 1
        elif mounting_type == 'base_only':
            # Base only mounting
            base_cost = 450.00
            base_sell_price = apply_margin(base_cost, margin_percentage)
            
            # Add to total assembly price
            total_assembly_price += Decimal(str(base_sell_price))
            
            base_line = QuoteLineItem(
                option_id=option_id,
                product_id=None,
                custom_sku='BASE-001',
                custom_name="  • Base Only",
                quantity=1,
                unit_price=Decimal(str(base_sell_price)),
                discount=Decimal('0'),
                display_order=current_order
            )
            db.session.add(base_line)
            line_items_created.append(('Base Only', base_line))
            current_order += 1
        elif mounting_type == 'crossbar':
            # Crossbar mounting
            crossbar_cost = 284.76
            crossbar_sell_price = apply_margin(crossbar_cost, margin_percentage)
            
            # Add to total assembly price (multiply by quantity)
            total_assembly_price += Decimal(str(crossbar_sell_price)) * crossbar_quantity
            
            crossbar_line = QuoteLineItem(
                option_id=option_id,
                product_id=None,
                custom_sku='CROSSBAR-001',
                custom_name=f"  • Crossbar Alternative (Qty: {crossbar_quantity})",
                quantity=crossbar_quantity,
                unit_price=Decimal(str(crossbar_sell_price)),
                discount=Decimal('0'),
                display_order=current_order
            )
            db.session.add(crossbar_line)
            line_items_created.append(('Crossbar', crossbar_line))
            current_order += 1
        # Note: 'none' mounting type doesn't add any components
        
        # 3. Add springs
        if spring_type in ['standard', '50mm']:
            spring_key = 'spring_standard' if spring_type == 'standard' else 'spring_50mm'
            spring = get_component_for_pump(pump, spring_key)
            if spring and spring_quantity > 0:
                spring_cost = float(spring.get('nett_price', 153.30))
                spring_sell_price = apply_margin(spring_cost, margin_percentage)
                
                # Add to total assembly price (multiply by quantity)
                total_assembly_price += Decimal(str(spring_sell_price)) * spring_quantity
                
                spring_line = QuoteLineItem(
                    option_id=option_id,
                    product_id=None,
                    custom_sku=spring.get('part_number', 'SPRING'),
                    custom_name=f"  • Seismic Springs: {spring.get('description', 'Standard')}",
                    quantity=spring_quantity,
                    unit_price=Decimal(str(spring_sell_price)),
                    discount=Decimal('0'),
                    display_order=current_order
                )
                db.session.add(spring_line)
                line_items_created.append(('Springs', spring_line))
                current_order += 1
        
        # 4. Add rubber mounts
        if include_rubber_mounts and rubber_mount_quantity > 0:
            mount_cost = 11.83  # Default cost
            mount_sell_price = apply_margin(mount_cost, margin_percentage)
            
            # Add to total assembly price (multiply by quantity)
            total_assembly_price += Decimal(str(mount_sell_price)) * rubber_mount_quantity
            
            mount_line = QuoteLineItem(
                option_id=option_id,
                product_id=None,
                custom_sku='RM-001',
                custom_name="  • Rubber Mounts",
                quantity=rubber_mount_quantity,
                unit_price=Decimal(str(mount_sell_price)),
                discount=Decimal('0'),
                display_order=current_order
            )
            db.session.add(mount_line)
            line_items_created.append(('Rubber Mounts', mount_line))
            current_order += 1
        
        # 5. Add motor protection
        if include_motor_protection:
            motor_cost = 125.00
            motor_sell_price = apply_margin(motor_cost, margin_percentage)
            
            # Add to total assembly price
            total_assembly_price += Decimal(str(motor_sell_price))
            
            motor_line = QuoteLineItem(
                option_id=option_id,
                product_id=None,
                custom_sku='MP-001',
                custom_name="  • Motor Protection",
                quantity=1,
                unit_price=Decimal(str(motor_sell_price)),
                discount=Decimal('0'),
                display_order=current_order
            )
            db.session.add(motor_line)
            line_items_created.append(('Motor Protection', motor_line))
            current_order += 1
        
        # 6. Add drip tray
        if include_drip_tray:
            drip_cost = 85.00
            drip_sell_price = apply_margin(drip_cost, margin_percentage)
            
            # Add to total assembly price
            total_assembly_price += Decimal(str(drip_sell_price))
            
            drip_line = QuoteLineItem(
                option_id=option_id,
                product_id=None,
                custom_sku='DT-001',
                custom_name="  • Drip Trip Tray",
                quantity=1,
                unit_price=Decimal(str(drip_sell_price)),
                discount=Decimal('0'),
                display_order=current_order
            )
            db.session.add(drip_line)
            line_items_created.append(('Drip Tray', drip_line))
            current_order += 1
        
        # Update the assembly header with the total price
        pump_line.unit_price = total_assembly_price
        
        # Store the configuration in the notes field as JSON for future editing
        import json
        config_data = {
            'pump_id': pump_id,
            'margin_percentage': margin_percentage,
            'mounting_type': mounting_type,
            'crossbar_quantity': crossbar_quantity,
            'spring_type': spring_type,
            'spring_quantity': spring_quantity,
            'include_rubber_mounts': include_rubber_mounts,
            'rubber_mount_quantity': rubber_mount_quantity,
            'include_motor_protection': include_motor_protection,
            'include_drip_tray': include_drip_tray,
            'ip_rating': ip_rating,
            'assembly_description': assembly_description
        }
        pump_line.assembly_metadata = json.dumps(config_data)
        
        assemblies_added.append({
            'plant_reference': current_ref,
            'line_items': len(line_items_created)
        })
        
        # Commit all changes
        db.session.commit()
        
        # Update the deal's total amount
        deal = option.quote.recipient.deal
        deal.update_total_amount()
        db.session.commit()
        
        logger.info(f"Added pump assembly '{current_ref}' (qty: {quantity}) to quote option {option_id}")
        
        return jsonify({
            'success': True,
            'message': f'Successfully added pump assembly "{current_ref}" (Qty: {quantity})',
            'assemblies': assemblies_added
        })
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding pump assembly to quote: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


def get_component_for_pump(pump, component_type):
    """Helper function to get component data for a pump"""
    try:
        # Try to get from BOM
        bom_items = pump.bom_items if hasattr(pump, 'bom_items') else []
        
        for bom_item in bom_items:
            if component_type == 'inertia_base' and bom_item.component_type == 'inertia_base':
                inertia_base = InertiaBase.query.get(bom_item.component_id)
                if inertia_base:
                    return {
                        'id': inertia_base.id,
                        'part_number': inertia_base.part_number,
                        'description': inertia_base.description or f"{inertia_base.dimensions_display}",
                        'nett_cost': float(inertia_base.nett_cost) if inertia_base.nett_cost else 741.99
                    }
            elif 'spring' in component_type and bom_item.component_type == 'seismic_spring':
                spring = SeismicSpring.query.get(bom_item.component_id)
                if spring:
                    # Determine if this is the right spring type
                    is_50mm = spring.static_deflection_mm and spring.static_deflection_mm >= 50
                    if (component_type == 'spring_50mm' and is_50mm) or (component_type == 'spring_standard' and not is_50mm):
                        return {
                            'id': spring.id,
                            'part_number': spring.part_number,
                            'description': spring.description or 'Seismic Spring',
                            'nett_price': float(spring.nett_price) if spring.nett_price else 153.30
                        }
        
        # Return defaults if not found in BOM
        if component_type == 'inertia_base':
            return {'part_number': 'IB-BASE', 'description': 'Inertia Base', 'nett_cost': 741.99}
        elif 'spring' in component_type:
            return {'part_number': 'SPRING', 'description': 'Seismic Spring', 'nett_price': 153.30}
        
        return None
    
    except Exception as e:
        logger.error(f"Error getting component for pump: {e}")
        return None
