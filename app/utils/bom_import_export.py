"""
Utility functions for importing and exporting Pump BOM (Bill of Materials) data
"""
import csv
import io
from typing import Dict, List, Tuple, Optional
from flask import current_app
from app.extensions import db
from app.models.pumps import (
    Pump, PumpBOM, InertiaBase, SeismicSpring, RubberMount, 
    Crossbar, MotorProtection, DripTripTray
)
from app.core.core_logging import logger


def export_bom_to_csv() -> str:
    """
    Export all BOM entries to CSV format
    
    Returns:
        CSV string with BOM data
    """
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Pump Part Number',
        'Pump Name',
        'Mounting Type',
        'Inertia Base Part Number',
        'Inertia Base Dimensions',
        'Crossbar SKU',
        'Spring Part Number',
        'Spring Quantity',
        'Notes'
    ])
    
    # Get all pumps with BOM entries
    pumps = Pump.query.order_by(Pump.part_number).all()
    
    for pump in pumps:
        if pump.bom_items:
            row_data = {
                'pump_part': pump.part_number,
                'pump_name': pump.name,
                'inertia_base': '',
                'inertia_dims': '',
                'spring': '',
                'spring_qty': '',
                'notes': ''
            }
            
            # Process each BOM item
            for bom_item in pump.bom_items:
                comp_type = bom_item.component_type
                comp_id = bom_item.component_id
                qty = bom_item.quantity
                
                try:
                    if comp_type == 'inertia_base':
                        base = InertiaBase.query.get(comp_id)
                        if base:
                            row_data['inertia_base'] = base.part_number
                            if base.length_mm and base.width_mm and base.depth_mm:
                                row_data['inertia_dims'] = f"{base.length_mm} x {base.width_mm} x {base.depth_mm}"
                    
                    elif comp_type == 'seismic_spring':
                        spring = SeismicSpring.query.get(comp_id)
                        if spring:
                            row_data['spring'] = spring.part_number
                            row_data['spring_qty'] = qty
                
                except Exception as e:
                    logger.warning(f"Error processing BOM item for pump {pump.part_number}: {e}")
            
            # Write row
            writer.writerow([
                row_data['pump_part'],
                row_data['pump_name'],
                row_data['inertia_base'],
                row_data['inertia_dims'],
                row_data['spring'],
                row_data['spring_qty'],
                row_data['notes']
            ])
    
    return output.getvalue()


def import_bom_from_csv(
    file_content: str, 
    overwrite_existing: bool = False,
    create_missing_components: bool = True
) -> Tuple[int, int, List[str]]:
    """
    Import BOM entries from CSV
    
    Args:
        file_content: CSV file content as string
        overwrite_existing: If True, delete existing BOM entries for pumps in file
        create_missing_components: If True, create components that don't exist
    
    Returns:
        Tuple of (successful_imports, failed_imports, error_messages)
    """
    successful = 0
    failed = 0
    errors = []
    
    try:
        csv_file = io.StringIO(file_content)
        reader = csv.DictReader(csv_file)
        
        for row_num, row in enumerate(reader, start=2):  # Start at 2 to account for header
            try:
                pump_part = row.get('Pump Part Number', '').strip()
                
                if not pump_part:
                    errors.append(f"Row {row_num}: Missing pump part number")
                    failed += 1
                    continue
                
                # Normalize part number (remove .0 if present from CSV number conversion)
                pump_part = str(pump_part).rstrip('.0') if '.' in str(pump_part) else str(pump_part)
                
                # Find or skip pump - try exact match first, then normalized
                pump = Pump.query.filter_by(part_number=pump_part).first()
                if not pump:
                    # Try with .0 suffix
                    pump = Pump.query.filter_by(part_number=f"{pump_part}.0").first()
                if not pump:
                    # Try stripping .0 from database values
                    all_pumps = Pump.query.all()
                    for p in all_pumps:
                        normalized_db_part = str(p.part_number).rstrip('.0') if '.' in str(p.part_number) else str(p.part_number)
                        if normalized_db_part == pump_part:
                            pump = p
                            break
                if not pump:
                    errors.append(f"Row {row_num}: Pump '{pump_part}' not found. Please create pump first.")
                    failed += 1
                    continue
                
                # Optionally clear existing BOM
                if overwrite_existing:
                    PumpBOM.query.filter_by(pump_id=pump.id).delete()
                
                # Process each component type
                components_added = 0
                
                # Inertia Base (default mounting - can be swapped for crossbar during config)
                inertia_part = row.get('Inertia Base Part Number', '').strip()
                # Normalize part number
                inertia_part = str(inertia_part).rstrip('.0') if inertia_part and '.' in str(inertia_part) else str(inertia_part) if inertia_part else ''
                if inertia_part:
                    base = InertiaBase.query.filter_by(part_number=inertia_part).first()
                    if base:
                        bom = PumpBOM(
                            pump_id=pump.id,
                            component_id=base.id,
                            component_type='inertia_base',
                            quantity=1,
                            is_optional=False
                        )
                        db.session.add(bom)
                        components_added += 1
                    elif create_missing_components:
                        # Create inertia base
                        dims = row.get('Inertia Base Dimensions', '').strip()
                        length, width, depth = None, None, None
                        if dims and 'x' in dims:
                            parts = dims.split('x')
                            if len(parts) == 3:
                                try:
                                    length = int(parts[0].strip())
                                    width = int(parts[1].strip())
                                    depth = int(parts[2].strip())
                                except ValueError:
                                    pass
                        
                        base = InertiaBase(
                            part_number=inertia_part,
                            description=f"Auto-imported for {pump_part}",
                            length_mm=length,
                            width_mm=width,
                            depth_mm=depth,
                            is_active=True
                        )
                        db.session.add(base)
                        db.session.flush()  # Get ID
                        
                        bom = PumpBOM(
                            pump_id=pump.id,
                            component_id=base.id,
                            component_type='inertia_base',
                            quantity=1,
                            is_optional=False
                        )
                        db.session.add(bom)
                        components_added += 1
                    else:
                        errors.append(f"Row {row_num}: Inertia base '{inertia_part}' not found")
                
                # Seismic Springs
                spring_part = row.get('Spring Part Number', '').strip()
                # Normalize part number
                spring_part = str(spring_part).rstrip('.0') if spring_part and '.' in str(spring_part) else str(spring_part) if spring_part else ''
                spring_qty_str = row.get('Spring Quantity', '1').strip()
                if spring_part:
                    try:
                        spring_qty = int(spring_qty_str) if spring_qty_str else 1
                    except ValueError:
                        spring_qty = 1
                    
                    spring = SeismicSpring.query.filter_by(part_number=spring_part).first()
                    if spring:
                        bom = PumpBOM(
                            pump_id=pump.id,
                            component_id=spring.id,
                            component_type='seismic_spring',
                            quantity=spring_qty,
                            is_optional=False
                        )
                        db.session.add(bom)
                        components_added += 1
                    elif create_missing_components:
                        spring = SeismicSpring(
                            part_number=spring_part,
                            description=f"Auto-imported for {pump_part}",
                            is_active=True
                        )
                        db.session.add(spring)
                        db.session.flush()
                        
                        bom = PumpBOM(
                            pump_id=pump.id,
                            component_id=spring.id,
                            component_type='seismic_spring',
                            quantity=spring_qty,
                            is_optional=False
                        )
                        db.session.add(bom)
                        components_added += 1
                    else:
                        errors.append(f"Row {row_num}: Spring '{spring_part}' not found")
                
                if components_added > 0:
                    successful += 1
                else:
                    errors.append(f"Row {row_num}: No components added for pump '{pump_part}'")
                    failed += 1
                
            except Exception as e:
                logger.error(f"Error processing row {row_num}: {e}", exc_info=True)
                errors.append(f"Row {row_num}: {str(e)}")
                failed += 1
        
        # Commit all changes
        db.session.commit()
        logger.info(f"BOM import completed: {successful} successful, {failed} failed")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"BOM import failed: {e}", exc_info=True)
        errors.append(f"Import failed: {str(e)}")
        return 0, 0, errors
    
    return successful, failed, errors


def generate_sample_csv() -> str:
    """
    Generate a sample CSV template with example data
    
    Returns:
        CSV string with sample data
    """
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Pump Part Number',
        'Pump Name',
        'Inertia Base Part Number',
        'Inertia Base Dimensions',
        'Spring Part Number',
        'Spring Quantity',
        'Notes'
    ])
    
    # Write sample rows
    writer.writerow([
        '99801136',
        'NBG 125-100-160/167',
        '98327389',
        '1200 x 800 x 200',
        '91338018',
        '4',
        'Large NBG pump with inertia base and 4 springs'
    ])
    
    writer.writerow([
        '99801135',
        'NBG 125-100-160/160-154',
        '98327389',
        '1200 x 800 x 200',
        '91338018',
        '4',
        'Same inertia base and springs as above'
    ])
    
    writer.writerow([
        '99796408',
        'NBG 50-32-160/163',
        '98336369',
        '800 x 630 x 125',
        '92932672',
        '4',
        'Smaller NBG pump - 50mm static equivalent springs'
    ])
    
    writer.writerow([
        '99801330',
        'NBG 125-80-200/179',
        '98327382',
        '950 x 720 x 150',
        '91338157',
        '4',
        'Medium NBG pump'
    ])
    
    return output.getvalue()

