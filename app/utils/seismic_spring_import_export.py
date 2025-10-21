"""
Utility functions for importing and exporting Seismic Spring data
"""
import csv
import io
from typing import Dict, List, Tuple, Optional
from flask import current_app
from app.extensions import db
from app.models.pumps import SeismicSpring
from app.core.core_logging import logger


def export_seismic_springs_to_csv() -> str:
    """
    Export all seismic springs to CSV format
    
    Returns:
        CSV string with seismic spring data
    """
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Part Number',
        'Description',
        'Max Load (kg)',
        'Static Deflection (mm)',
        'Spring Constant',
        'Stripe 1 Color',
        'Stripe 2 Color',
        'List Price',
        'Nett Price',
        'Active'
    ])
    
    # Get all seismic springs
    springs = SeismicSpring.query.order_by(SeismicSpring.part_number).all()
    
    for spring in springs:
        writer.writerow([
            spring.part_number or '',
            spring.description or '',
            spring.max_load_kg or '',
            spring.static_deflection_mm or '',
            spring.spring_constant or '',
            spring.stripe_1_color or '',
            spring.stripe_2_color or '',
            spring.list_price or '',
            spring.nett_price or '',
            'Yes' if spring.is_active else 'No'
        ])
    
    return output.getvalue()


def import_seismic_springs_from_csv(
    file_content: str, 
    overwrite_existing: bool = False,
    update_existing: bool = True
) -> Tuple[int, int, List[str]]:
    """
    Import seismic springs from CSV
    
    Args:
        file_content: CSV file content as string
        overwrite_existing: If True, delete existing springs with same part numbers
        update_existing: If True, update existing springs with new data
    
    Returns:
        Tuple of (successful_imports, failed_imports, error_messages)
    """
    successful = 0
    failed = 0
    errors = []
    
    try:
        csv_file = io.StringIO(file_content)
        reader = csv.DictReader(csv_file)
        
        # Validate required headers
        required_headers = ['Part Number']
        if not all(header in reader.fieldnames for header in required_headers):
            errors.append(f"Missing required headers: {required_headers}")
            return 0, 0, errors
        
        for row_num, row in enumerate(reader, start=2):  # Start at 2 to account for header
            try:
                part_number = row.get('Part Number', '').strip()
                
                if not part_number:
                    errors.append(f"Row {row_num}: Missing part number")
                    failed += 1
                    continue
                
                # Check if spring already exists
                existing_spring = SeismicSpring.query.filter_by(part_number=part_number).first()
                
                if existing_spring and overwrite_existing:
                    # Delete existing spring
                    db.session.delete(existing_spring)
                    db.session.flush()
                    existing_spring = None
                elif existing_spring and not update_existing:
                    errors.append(f"Row {row_num}: Spring '{part_number}' already exists")
                    failed += 1
                    continue
                
                # Parse data
                description = row.get('Description', '').strip()
                max_load_kg = _parse_decimal(row.get('Max Load (kg)', '').strip())
                static_deflection_mm = _parse_decimal(row.get('Static Deflection (mm)', '').strip())
                spring_constant = _parse_decimal(row.get('Spring Constant', '').strip())
                stripe_1_color = row.get('Stripe 1 Color', '').strip()
                stripe_2_color = row.get('Stripe 2 Color', '').strip()
                list_price = _parse_decimal(row.get('List Price', '').strip())
                nett_price = _parse_decimal(row.get('Nett Price', '').strip())
                
                # Parse active status
                active_str = row.get('Active', 'Yes').strip().lower()
                is_active = active_str in ['yes', 'true', '1', 'y', 'active']
                
                if existing_spring:
                    # Update existing spring
                    existing_spring.description = description
                    existing_spring.max_load_kg = max_load_kg
                    existing_spring.static_deflection_mm = static_deflection_mm
                    existing_spring.spring_constant = spring_constant
                    existing_spring.stripe_1_color = stripe_1_color
                    existing_spring.stripe_2_color = stripe_2_color
                    existing_spring.list_price = list_price
                    existing_spring.nett_price = nett_price
                    existing_spring.is_active = is_active
                else:
                    # Create new spring
                    spring = SeismicSpring(
                        part_number=part_number,
                        description=description,
                        max_load_kg=max_load_kg,
                        static_deflection_mm=static_deflection_mm,
                        spring_constant=spring_constant,
                        stripe_1_color=stripe_1_color,
                        stripe_2_color=stripe_2_color,
                        list_price=list_price,
                        nett_price=nett_price,
                        is_active=is_active
                    )
                    db.session.add(spring)
                
                successful += 1
                
            except Exception as e:
                logger.error(f"Error processing seismic spring row {row_num}: {e}", exc_info=True)
                errors.append(f"Row {row_num}: {str(e)}")
                failed += 1
        
        # Commit all changes
        db.session.commit()
        logger.info(f"Seismic spring import completed: {successful} successful, {failed} failed")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Seismic spring import failed: {e}", exc_info=True)
        errors.append(f"Import failed: {str(e)}")
        return 0, 0, errors
    
    return successful, failed, errors


def generate_seismic_spring_sample_csv() -> str:
    """
    Generate a sample CSV template with example seismic spring data
    
    Returns:
        CSV string with sample data
    """
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Part Number',
        'Description',
        'Max Load (kg)',
        'Static Deflection (mm)',
        'Spring Constant',
        'Stripe 1 Color',
        'Stripe 2 Color',
        'List Price',
        'Nett Price',
        'Active'
    ])
    
    # Write sample rows
    writer.writerow([
        '91338018',
        'Seismic Spring - Heavy Duty - 50mm Static Deflection',
        '500.0',
        '50.0',
        '10.0',
        'Brown',
        'Yellow',
        '150.00',
        '120.00',
        'Yes'
    ])
    
    writer.writerow([
        '92932672',
        'Seismic Spring - Medium Duty - 25mm Static Deflection',
        '250.0',
        '25.0',
        '10.0',
        'Blue',
        'White',
        '95.00',
        '76.00',
        'Yes'
    ])
    
    writer.writerow([
        '91338157',
        'Seismic Spring - Extra Heavy Duty - 75mm Static Deflection',
        '750.0',
        '75.0',
        '10.0',
        'Red',
        'Green',
        '225.00',
        '180.00',
        'Yes'
    ])
    
    writer.writerow([
        '92958833',
        'Seismic Spring - Light Duty - 12.5mm Static Deflection',
        '125.0',
        '12.5',
        '10.0',
        'Orange',
        'Black',
        '65.00',
        '52.00',
        'Yes'
    ])
    
    writer.writerow([
        '91338019',
        'Seismic Spring - Ultra Heavy Duty - 100mm Static Deflection',
        '1000.0',
        '100.0',
        '10.0',
        'Purple',
        'Silver',
        '300.00',
        '240.00',
        'No'
    ])
    
    return output.getvalue()


def _parse_decimal(value: str) -> Optional[float]:
    """
    Parse a decimal value from string, handling empty values
    
    Args:
        value: String value to parse
        
    Returns:
        Float value or None if empty/invalid
    """
    if not value or value.strip() == '':
        return None
    
    try:
        return float(value.strip())
    except ValueError:
        return None



