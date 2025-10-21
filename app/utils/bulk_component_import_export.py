"""
Comprehensive bulk import/export utilities for all pump components

This module provides CSV-based import/export for:
- Pump Series
- Pumps
- Inertia Bases
- Seismic Springs
- Rubber Mounts
- Crossbars
- Motor Protection
- Drip Trip Trays
- Duty Points
- Generic Components (PumpComponent)
"""
import csv
import io
from typing import Dict, List, Tuple, Optional
from decimal import Decimal
from flask import current_app
from app.extensions import db
from app.models.pumps import (
    PumpSeries, Pump, InertiaBase, SeismicSpring, RubberMount,
    Crossbar, MotorProtection, DripTripTray, PumpDutyPoint, PumpComponent
)
from app.core.core_logging import logger


def _parse_decimal(value: str) -> Optional[Decimal]:
    """Parse decimal value, handling empty strings"""
    if not value or value.strip() == '':
        return None
    try:
        return Decimal(value.strip())
    except (ValueError, TypeError):
        return None


def _parse_bool(value: str) -> bool:
    """Parse boolean value from string"""
    return str(value).strip().lower() in ['yes', 'true', '1', 'y', 'active']


def _parse_int(value: str) -> Optional[int]:
    """Parse integer value, handling empty strings"""
    if not value or value.strip() == '':
        return None
    try:
        return int(float(value.strip()))
    except (ValueError, TypeError):
        return None


# ============================================================================
# PUMP SERIES
# ============================================================================

def export_pump_series_to_csv() -> str:
    """Export all pump series to CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Series Code', 'Series Name', 'Description', 'Active'])
    
    series_list = PumpSeries.query.order_by(PumpSeries.series_code).all()
    for series in series_list:
        writer.writerow([
            series.series_code or '',
            series.series_name or '',
            series.description or '',
            'Yes' if series.is_active else 'No'
        ])
    
    return output.getvalue()


def import_pump_series_from_csv(file_content: str, update_existing: bool = True) -> Tuple[int, int, List[str]]:
    """Import pump series from CSV"""
    successful, failed, errors = 0, 0, []
    
    try:
        csv_file = io.StringIO(file_content)
        reader = csv.DictReader(csv_file)
        
        for row_num, row in enumerate(reader, start=2):
            try:
                series_code = row.get('Series Code', '').strip()
                if not series_code:
                    errors.append(f"Row {row_num}: Missing series code")
                    failed += 1
                    continue
                
                existing = PumpSeries.query.filter_by(series_code=series_code).first()
                
                data = {
                    'series_name': row.get('Series Name', '').strip(),
                    'description': row.get('Description', '').strip(),
                    'is_active': _parse_bool(row.get('Active', 'Yes'))
                }
                
                if existing and update_existing:
                    for key, value in data.items():
                        setattr(existing, key, value)
                elif not existing:
                    series = PumpSeries(series_code=series_code, **data)
                    db.session.add(series)
                else:
                    errors.append(f"Row {row_num}: Series '{series_code}' already exists")
                    failed += 1
                    continue
                
                successful += 1
                
            except Exception as e:
                logger.error(f"Error processing pump series row {row_num}: {e}")
                errors.append(f"Row {row_num}: {str(e)}")
                failed += 1
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Pump series import failed: {e}")
        errors.append(f"Import failed: {str(e)}")
        return 0, 0, errors
    
    return successful, failed, errors


# ============================================================================
# PUMPS
# ============================================================================

def export_pumps_to_csv() -> str:
    """Export all pumps to CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        'Part Number', 'Name', 'Series Code', 'KW Rating', 'Poles',
        'List Price', 'Nett Price', 'Active'
    ])
    
    pumps = Pump.query.order_by(Pump.part_number).all()
    for pump in pumps:
        writer.writerow([
            pump.part_number or '',
            pump.name or '',
            pump.series.series_code if pump.series else '',
            pump.kw_rating or '',
            pump.poles or '',
            pump.list_price or '',
            pump.nett_price or '',
            'Yes' if pump.is_active else 'No'
        ])
    
    return output.getvalue()


def import_pumps_from_csv(file_content: str, update_existing: bool = True) -> Tuple[int, int, List[str]]:
    """Import pumps from CSV"""
    successful, failed, errors = 0, 0, []
    
    try:
        csv_file = io.StringIO(file_content)
        reader = csv.DictReader(csv_file)
        
        for row_num, row in enumerate(reader, start=2):
            try:
                part_number = row.get('Part Number', '').strip()
                if not part_number:
                    errors.append(f"Row {row_num}: Missing part number")
                    failed += 1
                    continue
                
                # Find series
                series_code = row.get('Series Code', '').strip()
                series = PumpSeries.query.filter_by(series_code=series_code).first() if series_code else None
                
                existing = Pump.query.filter_by(part_number=part_number).first()
                
                data = {
                    'name': row.get('Name', '').strip(),
                    'series_id': series.id if series else None,
                    'kw_rating': _parse_decimal(row.get('KW Rating', '')),
                    'poles': _parse_int(row.get('Poles', '')),
                    'list_price': _parse_decimal(row.get('List Price', '')),
                    'nett_price': _parse_decimal(row.get('Nett Price', '')),
                    'is_active': _parse_bool(row.get('Active', 'Yes'))
                }
                
                if existing and update_existing:
                    for key, value in data.items():
                        setattr(existing, key, value)
                elif not existing:
                    pump = Pump(part_number=part_number, **data)
                    db.session.add(pump)
                else:
                    errors.append(f"Row {row_num}: Pump '{part_number}' already exists")
                    failed += 1
                    continue
                
                successful += 1
                
            except Exception as e:
                logger.error(f"Error processing pump row {row_num}: {e}")
                errors.append(f"Row {row_num}: {str(e)}")
                failed += 1
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Pump import failed: {e}")
        errors.append(f"Import failed: {str(e)}")
        return 0, 0, errors
    
    return successful, failed, errors


# ============================================================================
# INERTIA BASES
# ============================================================================

def export_inertia_bases_to_csv() -> str:
    """Export all inertia bases to CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        'Part Number', 'Description', 'Length (mm)', 'Width (mm)', 'Depth (mm)',
        'Weight (kg)', 'List Price', 'Nett Cost', 'Active'
    ])
    
    bases = InertiaBase.query.order_by(InertiaBase.part_number).all()
    for base in bases:
        writer.writerow([
            base.part_number or '',
            base.description or '',
            base.length_mm or '',
            base.width_mm or '',
            base.depth_mm or '',
            base.weight_kg or '',
            base.list_price or '',
            base.nett_cost or '',
            'Yes' if base.is_active else 'No'
        ])
    
    return output.getvalue()


def import_inertia_bases_from_csv(file_content: str, update_existing: bool = True) -> Tuple[int, int, List[str]]:
    """Import inertia bases from CSV"""
    successful, failed, errors = 0, 0, []
    
    try:
        csv_file = io.StringIO(file_content)
        reader = csv.DictReader(csv_file)
        
        for row_num, row in enumerate(reader, start=2):
            try:
                part_number = row.get('Part Number', '').strip()
                if not part_number:
                    errors.append(f"Row {row_num}: Missing part number")
                    failed += 1
                    continue
                
                existing = InertiaBase.query.filter_by(part_number=part_number).first()
                
                data = {
                    'description': row.get('Description', '').strip(),
                    'length_mm': _parse_int(row.get('Length (mm)', '')),
                    'width_mm': _parse_int(row.get('Width (mm)', '')),
                    'depth_mm': _parse_int(row.get('Depth (mm)', '')),
                    'weight_kg': _parse_decimal(row.get('Weight (kg)', '')),
                    'list_price': _parse_decimal(row.get('List Price', '')),
                    'nett_cost': _parse_decimal(row.get('Nett Cost', '')),
                    'is_active': _parse_bool(row.get('Active', 'Yes'))
                }
                
                if existing and update_existing:
                    for key, value in data.items():
                        setattr(existing, key, value)
                elif not existing:
                    base = InertiaBase(part_number=part_number, **data)
                    db.session.add(base)
                else:
                    errors.append(f"Row {row_num}: Inertia base '{part_number}' already exists")
                    failed += 1
                    continue
                
                successful += 1
                
            except Exception as e:
                logger.error(f"Error processing inertia base row {row_num}: {e}")
                errors.append(f"Row {row_num}: {str(e)}")
                failed += 1
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Inertia base import failed: {e}")
        errors.append(f"Import failed: {str(e)}")
        return 0, 0, errors
    
    return successful, failed, errors


# ============================================================================
# RUBBER MOUNTS
# ============================================================================

def export_rubber_mounts_to_csv() -> str:
    """Export all rubber mounts to CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['SKU', 'Description', 'List Price', 'Nett Price', 'Active'])
    
    mounts = RubberMount.query.order_by(RubberMount.sku).all()
    for mount in mounts:
        writer.writerow([
            mount.sku or '',
            mount.item_description or '',
            mount.list_price or '',
            mount.nett_price or '',
            'Yes' if mount.is_active else 'No'
        ])
    
    return output.getvalue()


def import_rubber_mounts_from_csv(file_content: str, update_existing: bool = True) -> Tuple[int, int, List[str]]:
    """Import rubber mounts from CSV"""
    successful, failed, errors = 0, 0, []
    
    try:
        csv_file = io.StringIO(file_content)
        reader = csv.DictReader(csv_file)
        
        for row_num, row in enumerate(reader, start=2):
            try:
                sku = row.get('SKU', '').strip()
                if not sku:
                    errors.append(f"Row {row_num}: Missing SKU")
                    failed += 1
                    continue
                
                existing = RubberMount.query.filter_by(sku=sku).first()
                
                data = {
                    'item_description': row.get('Description', '').strip(),
                    'list_price': _parse_decimal(row.get('List Price', '')),
                    'nett_price': _parse_decimal(row.get('Nett Price', '')),
                    'is_active': _parse_bool(row.get('Active', 'Yes'))
                }
                
                if existing and update_existing:
                    for key, value in data.items():
                        setattr(existing, key, value)
                elif not existing:
                    mount = RubberMount(sku=sku, **data)
                    db.session.add(mount)
                else:
                    errors.append(f"Row {row_num}: Rubber mount '{sku}' already exists")
                    failed += 1
                    continue
                
                successful += 1
                
            except Exception as e:
                logger.error(f"Error processing rubber mount row {row_num}: {e}")
                errors.append(f"Row {row_num}: {str(e)}")
                failed += 1
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Rubber mount import failed: {e}")
        errors.append(f"Import failed: {str(e)}")
        return 0, 0, errors
    
    return successful, failed, errors


# ============================================================================
# CROSSBARS
# ============================================================================

def export_crossbars_to_csv() -> str:
    """Export all crossbars to CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['SKU', 'Description', 'List Price', 'Nett Price', 'Active'])
    
    crossbars = Crossbar.query.order_by(Crossbar.sku).all()
    for crossbar in crossbars:
        writer.writerow([
            crossbar.sku or '',
            crossbar.description or '',
            crossbar.list_price or '',
            crossbar.nett_price or '',
            'Yes' if crossbar.is_active else 'No'
        ])
    
    return output.getvalue()


def import_crossbars_from_csv(file_content: str, update_existing: bool = True) -> Tuple[int, int, List[str]]:
    """Import crossbars from CSV"""
    successful, failed, errors = 0, 0, []
    
    try:
        csv_file = io.StringIO(file_content)
        reader = csv.DictReader(csv_file)
        
        for row_num, row in enumerate(reader, start=2):
            try:
                sku = row.get('SKU', '').strip()
                if not sku:
                    errors.append(f"Row {row_num}: Missing SKU")
                    failed += 1
                    continue
                
                existing = Crossbar.query.filter_by(sku=sku).first()
                
                data = {
                    'description': row.get('Description', '').strip(),
                    'list_price': _parse_decimal(row.get('List Price', '')),
                    'nett_price': _parse_decimal(row.get('Nett Price', '')),
                    'is_active': _parse_bool(row.get('Active', 'Yes'))
                }
                
                if existing and update_existing:
                    for key, value in data.items():
                        setattr(existing, key, value)
                elif not existing:
                    crossbar = Crossbar(sku=sku, **data)
                    db.session.add(crossbar)
                else:
                    errors.append(f"Row {row_num}: Crossbar '{sku}' already exists")
                    failed += 1
                    continue
                
                successful += 1
                
            except Exception as e:
                logger.error(f"Error processing crossbar row {row_num}: {e}")
                errors.append(f"Row {row_num}: {str(e)}")
                failed += 1
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Crossbar import failed: {e}")
        errors.append(f"Import failed: {str(e)}")
        return 0, 0, errors
    
    return successful, failed, errors


# ============================================================================
# MOTOR PROTECTION
# ============================================================================

def export_motor_protection_to_csv() -> str:
    """Export all motor protection items to CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Description', 'Nett Cost', 'Active'])
    
    items = MotorProtection.query.order_by(MotorProtection.description).all()
    for item in items:
        writer.writerow([
            item.description or '',
            item.nett_cost or '',
            'Yes' if item.is_active else 'No'
        ])
    
    return output.getvalue()


def import_motor_protection_from_csv(file_content: str, update_existing: bool = True) -> Tuple[int, int, List[str]]:
    """Import motor protection items from CSV"""
    successful, failed, errors = 0, 0, []
    
    try:
        csv_file = io.StringIO(file_content)
        reader = csv.DictReader(csv_file)
        
        for row_num, row in enumerate(reader, start=2):
            try:
                description = row.get('Description', '').strip()
                if not description:
                    errors.append(f"Row {row_num}: Missing description")
                    failed += 1
                    continue
                
                existing = MotorProtection.query.filter_by(description=description).first()
                
                data = {
                    'nett_cost': _parse_decimal(row.get('Nett Cost', '')),
                    'is_active': _parse_bool(row.get('Active', 'Yes'))
                }
                
                if existing and update_existing:
                    for key, value in data.items():
                        setattr(existing, key, value)
                elif not existing:
                    item = MotorProtection(description=description, **data)
                    db.session.add(item)
                else:
                    errors.append(f"Row {row_num}: Motor protection '{description}' already exists")
                    failed += 1
                    continue
                
                successful += 1
                
            except Exception as e:
                logger.error(f"Error processing motor protection row {row_num}: {e}")
                errors.append(f"Row {row_num}: {str(e)}")
                failed += 1
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Motor protection import failed: {e}")
        errors.append(f"Import failed: {str(e)}")
        return 0, 0, errors
    
    return successful, failed, errors


# ============================================================================
# DRIP TRIP TRAYS
# ============================================================================

def export_drip_trays_to_csv() -> str:
    """Export all drip trip trays to CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Series Code', 'Description', 'Nett Cost', 'Standard', 'Active'])
    
    trays = DripTripTray.query.order_by(DripTripTray.series_id, DripTripTray.description).all()
    for tray in trays:
        writer.writerow([
            tray.series.series_code if tray.series else '',
            tray.description or '',
            tray.nett_cost or '',
            'Yes' if tray.is_standard else 'No',
            'Yes' if tray.is_active else 'No'
        ])
    
    return output.getvalue()


def import_drip_trays_from_csv(file_content: str, update_existing: bool = True) -> Tuple[int, int, List[str]]:
    """Import drip trip trays from CSV"""
    successful, failed, errors = 0, 0, []
    
    try:
        csv_file = io.StringIO(file_content)
        reader = csv.DictReader(csv_file)
        
        for row_num, row in enumerate(reader, start=2):
            try:
                description = row.get('Description', '').strip()
                if not description:
                    errors.append(f"Row {row_num}: Missing description")
                    failed += 1
                    continue
                
                # Find series
                series_code = row.get('Series Code', '').strip()
                series = PumpSeries.query.filter_by(series_code=series_code).first() if series_code else None
                
                # Check for existing by description and series
                existing = DripTripTray.query.filter_by(
                    description=description,
                    series_id=series.id if series else None
                ).first()
                
                data = {
                    'series_id': series.id if series else None,
                    'nett_cost': _parse_decimal(row.get('Nett Cost', '')),
                    'is_standard': _parse_bool(row.get('Standard', 'No')),
                    'is_active': _parse_bool(row.get('Active', 'Yes'))
                }
                
                if existing and update_existing:
                    for key, value in data.items():
                        setattr(existing, key, value)
                elif not existing:
                    tray = DripTripTray(description=description, **data)
                    db.session.add(tray)
                else:
                    errors.append(f"Row {row_num}: Drip tray '{description}' already exists")
                    failed += 1
                    continue
                
                successful += 1
                
            except Exception as e:
                logger.error(f"Error processing drip tray row {row_num}: {e}")
                errors.append(f"Row {row_num}: {str(e)}")
                failed += 1
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Drip tray import failed: {e}")
        errors.append(f"Import failed: {str(e)}")
        return 0, 0, errors
    
    return successful, failed, errors


# ============================================================================
# DUTY POINTS
# ============================================================================

def export_duty_points_to_csv() -> str:
    """Export all duty points to CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        'Series Code', 'Flow Rate (L/s)', 'Head Pressure (kPa)',
        'Tolerance (%)'
    ])
    
    points = PumpDutyPoint.query.order_by(PumpDutyPoint.series_id, PumpDutyPoint.flow_rate_lps).all()
    for point in points:
        writer.writerow([
            point.series.series_code if point.series else '',
            point.flow_rate_lps or '',
            point.head_pressure_kpa or '',
            point.tolerance_percentage or ''
        ])
    
    return output.getvalue()


def import_duty_points_from_csv(file_content: str, update_existing: bool = True) -> Tuple[int, int, List[str]]:
    """Import duty points from CSV"""
    successful, failed, errors = 0, 0, []
    
    try:
        csv_file = io.StringIO(file_content)
        reader = csv.DictReader(csv_file)
        
        for row_num, row in enumerate(reader, start=2):
            try:
                flow_rate = _parse_decimal(row.get('Flow Rate (L/s)', ''))
                head_pressure = _parse_decimal(row.get('Head Pressure (kPa)', ''))
                
                if flow_rate is None or head_pressure is None:
                    errors.append(f"Row {row_num}: Missing flow rate or head pressure")
                    failed += 1
                    continue
                
                # Find series
                series_code = row.get('Series Code', '').strip()
                series = PumpSeries.query.filter_by(series_code=series_code).first() if series_code else None
                
                # Check for existing by flow rate, head pressure, and series
                existing = PumpDutyPoint.query.filter_by(
                    flow_rate_lps=flow_rate,
                    head_pressure_kpa=head_pressure,
                    series_id=series.id if series else None
                ).first()
                
                data = {
                    'series_id': series.id if series else None,
                    'tolerance_percentage': _parse_decimal(row.get('Tolerance (%)', '')) or Decimal('5.0')
                }
                
                if existing and update_existing:
                    for key, value in data.items():
                        setattr(existing, key, value)
                elif not existing:
                    point = PumpDutyPoint(
                        flow_rate_lps=flow_rate,
                        head_pressure_kpa=head_pressure,
                        **data
                    )
                    db.session.add(point)
                else:
                    errors.append(f"Row {row_num}: Duty point already exists")
                    failed += 1
                    continue
                
                successful += 1
                
            except Exception as e:
                logger.error(f"Error processing duty point row {row_num}: {e}")
                errors.append(f"Row {row_num}: {str(e)}")
                failed += 1
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Duty point import failed: {e}")
        errors.append(f"Import failed: {str(e)}")
        return 0, 0, errors
    
    return successful, failed, errors


# ============================================================================
# GENERIC COMPONENTS
# ============================================================================

def export_generic_components_to_csv() -> str:
    """Export all generic pump components to CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        'Component Type', 'Part Number', 'Description',
        'List Price', 'Nett Price', 'Active'
    ])
    
    components = PumpComponent.query.order_by(PumpComponent.component_type, PumpComponent.part_number).all()
    for comp in components:
        writer.writerow([
            comp.component_type or '',
            comp.part_number or '',
            comp.description or '',
            comp.list_price or '',
            comp.nett_price or '',
            'Yes' if comp.is_active else 'No'
        ])
    
    return output.getvalue()


def import_generic_components_from_csv(file_content: str, update_existing: bool = True) -> Tuple[int, int, List[str]]:
    """Import generic pump components from CSV"""
    successful, failed, errors = 0, 0, []
    
    try:
        csv_file = io.StringIO(file_content)
        reader = csv.DictReader(csv_file)
        
        for row_num, row in enumerate(reader, start=2):
            try:
                component_type = row.get('Component Type', '').strip()
                part_number = row.get('Part Number', '').strip()
                
                if not component_type or not part_number:
                    errors.append(f"Row {row_num}: Missing component type or part number")
                    failed += 1
                    continue
                
                existing = PumpComponent.query.filter_by(
                    component_type=component_type,
                    part_number=part_number
                ).first()
                
                data = {
                    'description': row.get('Description', '').strip(),
                    'list_price': _parse_decimal(row.get('List Price', '')),
                    'nett_price': _parse_decimal(row.get('Nett Price', '')),
                    'is_active': _parse_bool(row.get('Active', 'Yes'))
                }
                
                if existing and update_existing:
                    for key, value in data.items():
                        setattr(existing, key, value)
                elif not existing:
                    comp = PumpComponent(
                        component_type=component_type,
                        part_number=part_number,
                        **data
                    )
                    db.session.add(comp)
                else:
                    errors.append(f"Row {row_num}: Component '{component_type}/{part_number}' already exists")
                    failed += 1
                    continue
                
                successful += 1
                
            except Exception as e:
                logger.error(f"Error processing component row {row_num}: {e}")
                errors.append(f"Row {row_num}: {str(e)}")
                failed += 1
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Component import failed: {e}")
        errors.append(f"Import failed: {str(e)}")
        return 0, 0, errors
    
    return successful, failed, errors


# ============================================================================
# MASTER EXPORT/IMPORT
# ============================================================================

def export_all_components() -> Dict[str, str]:
    """
    Export all pump component types to separate CSV strings
    
    Returns:
        Dictionary mapping component type to CSV string
    """
    from app.utils.seismic_spring_import_export import export_seismic_springs_to_csv
    
    return {
        'pump_series': export_pump_series_to_csv(),
        'pumps': export_pumps_to_csv(),
        'inertia_bases': export_inertia_bases_to_csv(),
        'seismic_springs': export_seismic_springs_to_csv(),  # Use existing function
        'rubber_mounts': export_rubber_mounts_to_csv(),
        'crossbars': export_crossbars_to_csv(),
        'motor_protection': export_motor_protection_to_csv(),
        'drip_trays': export_drip_trays_to_csv(),
        'duty_points': export_duty_points_to_csv(),
        'generic_components': export_generic_components_to_csv(),
    }

