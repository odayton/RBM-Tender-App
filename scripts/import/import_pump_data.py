#!/usr/bin/env python
# scripts/import/import_pump_data.py

"""
Comprehensive pump data import script
Imports all pump-related data from Excel file into database
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
from decimal import Decimal
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config/.env')

from app import create_app, db
from app.models.pumps import (
    PumpSeries, Pump, InertiaBase, SeismicSpring, 
    RubberMount, Crossbar, MotorProtection, DripTripTray, PumpBOM
)
from app.core.core_config import DevelopmentConfig

# Series path configuration for pump curve URLs
SERIES_PATHS = {
    'CR': 'cr-cre-cri-crie-crn-crne-crt-crte/cr',
    'CRE': 'cr-cre-cri-crie-crn-crne-crt-crte/cre',
    'CRI': 'cr-cre-cri-crie-crn-crne-crt-crte/cri',
    'CRIE': 'cr-cre-cri-crie-crn-crne-crt-crte/crie',
    'CRN': 'cr-cre-cri-crie-crn-crne-crt-crte/crn',
    'CRNE': 'cr-cre-cri-crie-crn-crne-crt-crte/crne',
    'NBG': 'nbg/nbg',
    'NK': 'nk/nk',
    'TP': 'tp-tpe/tp',
    'UPS': 'ups/ups',
    'MAGNA': 'magna3/magna3',
    'CM': 'cm/cm'
}

EXCEL_FILE = 'data/Pump Database(1).xlsx'


def clean_numeric(value):
    """Clean and convert numeric values, handle NaN"""
    if pd.isna(value):
        return None
    try:
        # Remove currency symbols and commas
        if isinstance(value, str):
            value = value.replace('$', '').replace(',', '').strip()
            if not value or value == '':
                return None
        return Decimal(str(value))
    except (ValueError, TypeError, Exception):
        return None


def clean_string(value):
    """Clean string values, handle NaN"""
    if pd.isna(value):
        return None
    return str(value).strip() if value else None


def clean_integer(value):
    """Clean integer values, handle NaN"""
    if pd.isna(value):
        return None
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


class PumpDataImporter:
    """Main importer class for pump data"""
    
    def __init__(self, excel_file):
        self.excel_file = excel_file
        self.app = None
        self.stats = {
            'series': 0,
            'pumps': 0,
            'inertia_bases': 0,
            'seismic_springs': 0,
            'rubber_mounts': 0,
            'crossbars': 0,
            'bom_items': 0,
            'errors': []
        }
    
    def setup_app(self):
        """Initialize Flask app and database"""
        print("Initializing application...")
        self.app = create_app(DevelopmentConfig)
        return self.app
    
    def import_pump_series(self):
        """Import pump series data"""
        print("\n" + "="*60)
        print("STEP 1: Importing Pump Series")
        print("="*60)
        
        with self.app.app_context():
            for series_code, series_path in SERIES_PATHS.items():
                existing = PumpSeries.query.filter_by(series_code=series_code).first()
                
                if existing:
                    print(f"  WARNING: Series '{series_code}' already exists, skipping...")
                    continue
                
                series = PumpSeries(
                    series_code=series_code,
                    series_name=series_code,
                    description=f"{series_code} Series Pumps",
                    series_path=series_path,
                    curve_url_pattern="https://product-selection.grundfos.com/au/products/{series_path}/{model_slug}-{part_number}",
                    is_active=True
                )
                db.session.add(series)
                self.stats['series'] += 1
                print(f"  + Added series: {series_code}")
            
            db.session.commit()
            print(f"\nSUCCESS: Imported {self.stats['series']} pump series")
    
    def import_inertia_bases(self):
        """Import inertia base data"""
        print("\n" + "="*60)
        print("STEP 2: Importing Inertia Bases")
        print("="*60)
        
        try:
            df = pd.read_excel(self.excel_file, sheet_name='Inertia Bases 2025')
            print(f"  Found {len(df)} inertia bases in Excel")
            
            with self.app.app_context():
                for idx, row in df.iterrows():
                    part_number = clean_string(row.get('Part number'))
                    
                    if not part_number:
                        print(f"  WARNING: Row {idx+2}: Missing part number, skipping...")
                        continue
                    
                    # Check if exists
                    existing = InertiaBase.query.filter_by(part_number=part_number).first()
                    if existing:
                        print(f"  WARNING: Inertia base '{part_number}' already exists, skipping...")
                        continue
                    
                    # Parse dimensions
                    length = clean_integer(row.get('Length'))
                    width = clean_integer(row.get('Width'))
                    depth = clean_integer(row.get('Depth'))
                    
                    description = None
                    if length and width and depth:
                        description = f"{length} x {width} x {depth}"
                    
                    inertia_base = InertiaBase(
                        part_number=part_number,
                        description=description,
                        weight_kg=clean_numeric(row.get('Correct Weight (kg)')),
                        length_mm=length,
                        width_mm=width,
                        depth_mm=depth,
                        mount_height_mm=clean_integer(row.get('Mount Height')),
                        list_price=clean_numeric(row.get('List Price')),
                        nett_cost=clean_numeric(row.get('Net Cost')),
                        is_active=True
                    )
                    
                    db.session.add(inertia_base)
                    self.stats['inertia_bases'] += 1
                    
                    if (idx + 1) % 10 == 0:
                        db.session.commit()
                        print(f"  + Processed {idx + 1} inertia bases...")
                
                db.session.commit()
                print(f"\nSUCCESS: Imported {self.stats['inertia_bases']} inertia bases")
        
        except Exception as e:
            print(f"  ERROR: Error importing inertia bases: {e}")
            self.stats['errors'].append(f"Inertia bases: {e}")
            with self.app.app_context():
                db.session.rollback()
    
    def import_seismic_springs(self):
        """Import seismic spring data"""
        print("\n" + "="*60)
        print("STEP 3: Importing Seismic Springs")
        print("="*60)
        
        try:
            df = pd.read_excel(self.excel_file, sheet_name='Seismic Springs 2025')
            print(f"  Found {len(df)} springs in Excel")
            
            with self.app.app_context():
                for idx, row in df.iterrows():
                    # Use Type as description, Part Number as part_number
                    spring_type = clean_string(row.get('Type'))
                    part_number = clean_string(row.get('Part Number'))
                    
                    # If no part number, use Type as part number for now
                    if not part_number and spring_type:
                        part_number = spring_type
                    
                    if not part_number:
                        print(f"  WARNING: Row {idx+2}: Missing part number/type, skipping...")
                        continue
                    
                    # Check if exists
                    existing = SeismicSpring.query.filter_by(part_number=part_number).first()
                    if existing:
                        continue
                    
                    spring = SeismicSpring(
                        part_number=part_number,
                        description=spring_type or part_number,
                        max_load_kg=clean_numeric(row.get('Max Load kg')),
                        static_deflection_mm=clean_numeric(row.get('Static Deflection')),
                        spring_constant=clean_numeric(row.get('Spring Constant kg/mm')),
                        stripe_1_color=clean_string(row.get('Stripe 1')),
                        stripe_2_color=clean_string(row.get('Stripe 2')),
                        nett_price=clean_numeric(row.get('Quoted Net Cost')) or clean_numeric(row.get('Net price')),
                        is_active=True
                    )
                    
                    db.session.add(spring)
                    self.stats['seismic_springs'] += 1
                
                db.session.commit()
                print(f"\nSUCCESS: Imported {self.stats['seismic_springs']} seismic springs")
        
        except Exception as e:
            print(f"  ERROR: Error importing seismic springs: {e}")
            self.stats['errors'].append(f"Seismic springs: {e}")
            with self.app.app_context():
                db.session.rollback()
    
    def import_rubber_mounts(self):
        """Import rubber mount data"""
        print("\n" + "="*60)
        print("STEP 4: Importing Rubber Mounts")
        print("="*60)
        
        try:
            df = pd.read_excel(self.excel_file, sheet_name='Rubber Mounts')
            print(f"  Found {len(df)} rubber mounts in Excel")
            
            with self.app.app_context():
                for idx, row in df.iterrows():
                    sku = clean_string(row.get('Sku') or row.get('SKU'))
                    
                    if not sku:
                        continue
                    
                    existing = RubberMount.query.filter_by(sku=sku).first()
                    if existing:
                        continue
                    
                    mount = RubberMount(
                        sku=sku,
                        item_description=clean_string(row.get('Item Descr.') or row.get('Description')),
                        static_deflection_mm=clean_numeric(row.get('Static Deflection')),
                        list_price=clean_numeric(row.get('List') or row.get('List Price')),
                        nett_price=clean_numeric(row.get('Unit Nett') or row.get('Nett Price')),
                        is_active=True
                    )
                    
                    db.session.add(mount)
                    self.stats['rubber_mounts'] += 1
                
                db.session.commit()
                print(f"\nSUCCESS: Imported {self.stats['rubber_mounts']} rubber mounts")
        
        except Exception as e:
            print(f"  ERROR: Error importing rubber mounts: {e}")
            self.stats['errors'].append(f"Rubber mounts: {e}")
            with self.app.app_context():
                db.session.rollback()
    
    def import_crossbars(self):
        """Import crossbar data"""
        print("\n" + "="*60)
        print("STEP 5: Importing Crossbars")
        print("="*60)
        
        try:
            df = pd.read_excel(self.excel_file, sheet_name='Crossbars')
            print(f"  Found {len(df)} crossbars in Excel")
            
            with self.app.app_context():
                for idx, row in df.iterrows():
                    sku = clean_string(row.get('SKU') or row.get('Sku'))
                    
                    if not sku:
                        continue
                    
                    existing = Crossbar.query.filter_by(sku=sku).first()
                    if existing:
                        continue
                    
                    crossbar = Crossbar(
                        sku=sku,
                        description=clean_string(row.get('Description') or row.get('Decription')),
                        list_price=clean_numeric(row.get('List')),
                        nett_price=clean_numeric(row.get('Unit Nett')),
                        is_active=True
                    )
                    
                    db.session.add(crossbar)
                    self.stats['crossbars'] += 1
                
                db.session.commit()
                print(f"\nSUCCESS: Imported {self.stats['crossbars']} crossbars")
        
        except Exception as e:
            print(f"  ERROR: Error importing crossbars: {e}")
            self.stats['errors'].append(f"Crossbars: {e}")
            with self.app.app_context():
                db.session.rollback()
    
    def import_nbg_pumps(self):
        """Import NBG BOM data"""
        print("\n" + "="*60)
        print("STEP 6: Importing NBG Pumps")
        print("="*60)
        
        try:
            df = pd.read_excel(self.excel_file, sheet_name='NBG BOM')
            print(f"  Found {len(df)} NBG pumps in Excel")
            
            with self.app.app_context():
                # Get NBG series
                nbg_series = PumpSeries.query.filter_by(series_code='NBG').first()
                
                if not nbg_series:
                    print("  ERROR: NBG series not found! Run import_pump_series first.")
                    return
                
                for idx, row in df.iterrows():
                    item_number = clean_string(row.get('Item No'))
                    name = clean_string(row.get('Name'))
                    
                    if not item_number or not name:
                        print(f"  WARNING: Row {idx+2}: Missing Item No or Name, skipping...")
                        continue
                    
                    # Use Item No as part_number for now (will update with actual part numbers later)
                    part_number = item_number
                    
                    # Check if exists
                    existing = Pump.query.filter_by(part_number=part_number).first()
                    if existing:
                        continue
                    
                    # Generate model slug for URL
                    model_slug = name.lower().replace(' ', '-').replace('/', '-')
                    
                    pump = Pump(
                        series_id=nbg_series.id,
                        part_number=part_number,
                        item_number=item_number,
                        name=name,
                        description=name,
                        kw_rating=clean_numeric(row.get('kW')),
                        poles=clean_integer(row.get('Poles')),
                        model_slug=model_slug,
                        list_price=clean_numeric(row.get('Pump List') or row.get('24/25 Pump List')),
                        nett_price=clean_numeric(row.get('Pump Nett') or row.get('24/25 Pump Nett')),
                        ip56_list_price=clean_numeric(row.get('IP-56 List')),
                        ip56_nett_price=clean_numeric(row.get('IP-56 Nett')),
                        ip66_list_price=clean_numeric(row.get('IP-66 List')),
                        ip66_nett_price=clean_numeric(row.get('IP-66 Nett')),
                        is_active=True
                    )
                    
                    db.session.add(pump)
                    self.stats['pumps'] += 1
                    
                    if (idx + 1) % 20 == 0:
                        db.session.commit()
                        print(f"  + Processed {idx + 1} NBG pumps...")
                
                db.session.commit()
                print(f"\nSUCCESS: Imported {self.stats['pumps']} NBG pumps")
        
        except Exception as e:
            print(f"  ERROR: Error importing NBG pumps: {e}")
            import traceback
            traceback.print_exc()
            self.stats['errors'].append(f"NBG pumps: {e}")
            with self.app.app_context():
                db.session.rollback()
    
    def import_cr_pumps(self, series_code, sheet_name):
        """Import CR-series pumps (CR, CRE, CRI, etc.)"""
        print(f"\n{'='*60}")
        print(f"Importing {series_code} Pumps from {sheet_name}")
        print("="*60)
        
        try:
            df = pd.read_excel(self.excel_file, sheet_name=sheet_name)
            print(f"  Found {len(df)} {series_code} pumps in Excel")
            
            with self.app.app_context():
                series = PumpSeries.query.filter_by(series_code=series_code).first()
                
                if not series:
                    print(f"  ERROR: {series_code} series not found!")
                    return
                
                imported = 0
                for idx, row in df.iterrows():
                    item_number = clean_string(row.get('Item No'))
                    name = clean_string(row.get('Name'))
                    
                    if not item_number or not name:
                        continue
                    
                    part_number = item_number
                    
                    existing = Pump.query.filter_by(part_number=part_number).first()
                    if existing:
                        continue
                    
                    model_slug = name.lower().replace(' ', '-').replace('/', '-')
                    
                    pump = Pump(
                        series_id=series.id,
                        part_number=part_number,
                        item_number=item_number,
                        name=name,
                        description=name,
                        model_slug=model_slug,
                        list_price=clean_numeric(row.get('Pump List')),
                        nett_price=clean_numeric(row.get('Pump Nett')),
                        ip56_nett_price=clean_numeric(row.get('IP-56 Nett')),
                        ip66_nett_price=clean_numeric(row.get('IP-66 Nett')),
                        is_active=True
                    )
                    
                    db.session.add(pump)
                    imported += 1
                    self.stats['pumps'] += 1
                
                db.session.commit()
                print(f"\nSUCCESS: Imported {imported} {series_code} pumps")
        
        except Exception as e:
            print(f"  ERROR: Error importing {series_code} pumps: {e}")
            self.stats['errors'].append(f"{series_code} pumps: {e}")
            with self.app.app_context():
                db.session.rollback()
    
    def run_full_import(self):
        """Run complete import process"""
        print("\n" + "="*60)
        print("PUMP DATABASE IMPORT STARTING")
        print("="*60)
        
        start_time = datetime.now()
        
        # Step 1: Import pump series
        self.import_pump_series()
        
        # Step 2: Import components
        self.import_inertia_bases()
        self.import_seismic_springs()
        self.import_rubber_mounts()
        self.import_crossbars()
        
        # Step 3: Import pumps from each BOM
        self.import_nbg_pumps()
        
        # Import all CR variants
        cr_series = ['CR', 'CRE', 'CRI', 'CRIE', 'CRN', 'CRNE']
        for series_code in cr_series:
            sheet_name = f'{series_code} BOM'
            try:
                self.import_cr_pumps(series_code, sheet_name)
            except Exception as e:
                print(f"  WARNING: Sheet '{sheet_name}' not found or error: {e}")
        
        # Import TP
        try:
            self.import_cr_pumps('TP', 'TP BOM')
        except Exception as e:
            print(f"  WARNING: TP BOM import error: {e}")
        
        # Import NK
        try:
            self.import_cr_pumps('NK', 'NK BOM')
        except Exception as e:
            print(f"  WARNING: NK BOM import error: {e}")
        
        # Print summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "="*60)
        print("IMPORT SUMMARY")
        print("="*60)
        print(f"Pump Series:      {self.stats['series']}")
        print(f"Pumps:            {self.stats['pumps']}")
        print(f"Inertia Bases:    {self.stats['inertia_bases']}")
        print(f"Seismic Springs:  {self.stats['seismic_springs']}")
        print(f"Rubber Mounts:    {self.stats['rubber_mounts']}")
        print(f"Crossbars:        {self.stats['crossbars']}")
        print(f"\nDuration:         {duration:.2f} seconds")
        
        if self.stats['errors']:
            print(f"\nWARNING: Errors encountered: {len(self.stats['errors'])}")
            for error in self.stats['errors']:
                print(f"  - {error}")
        else:
            print("\nSUCCESS: Import completed successfully with no errors!")
        
        print("="*60)


def main():
    """Main entry point"""
    importer = PumpDataImporter(EXCEL_FILE)
    importer.setup_app()
    importer.run_full_import()


if __name__ == '__main__':
    main()

