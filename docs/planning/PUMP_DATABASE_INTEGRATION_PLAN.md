# Pump Database Integration Plan

## Overview
This document outlines the comprehensive plan for integrating pump data from multiple BOM (Bill of Materials) files into the RBM Tender App database system.

## 1. Data Structure Analysis

### Current BOM Types Identified:
- **NBG & NK Series**: Complex structure with inertia bases, springs, crossbars
- **CR & TP Series**: Simplified structure with bases and rubber mounts  
- **MAGNA & UPS Series**: Basic pump-only structure
- **Supporting Components**: Seismic springs, rubber mounts, crossbars, inertia bases
- **Duty Point System**: Historical data-driven intelligent pump selection

### Key Components Found:
1. **Main Pumps** (different series: NBG, NK, CR, CRE, CRI, CRIE, CRN, CRNE, TP, UPS, CM, MAGNA)
2. **Inertia Bases** (with dimensions, weights, pricing)
3. **Seismic Springs** (standard and 50mm static variants)
4. **Rubber Mounts** (vibration isolation)
5. **Crossbars** (structural components)
6. **Motor Protection** (description and nett cost)
7. **Drip Trip Trays** (yes/no option, cost dependent on series)
8. **IP Ratings** (IP-56, IP-66 enclosures)

## 2. Proposed Database Schema

### Core Tables:

#### A. `pump_series` Table
```sql
CREATE TABLE pump_series (
    id SERIAL PRIMARY KEY,
    series_code VARCHAR(20) NOT NULL UNIQUE,  -- NBG, NK, CR, etc.
    series_name VARCHAR(100) NOT NULL,        -- Full name
    description TEXT,
    
    -- Pump curve link configuration
    curve_url_pattern VARCHAR(500),           -- Base URL pattern for this series
    -- Example: 'https://product-selection.grundfos.com/au/products/{series_path}/{model_slug}/{part_number}'
    series_path VARCHAR(100),                 -- Path segment for series (e.g., 'cr-cre-cri-crie-crn-crne-crt-crte/cr')
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### B. `pumps` Table (Main pump products)
```sql
CREATE TABLE pumps (
    id SERIAL PRIMARY KEY,
    series_id INTEGER REFERENCES pump_series(id),
    item_number VARCHAR(100) NOT NULL,
    part_number VARCHAR(100),                -- Manufacturer part number (e.g., 96501699)
    name VARCHAR(200) NOT NULL,
    description TEXT,
    kw_rating DECIMAL(8,2),                  -- Power rating in kW
    poles INTEGER,                           -- Motor poles (2, 4, 6, etc.)
    
    -- Performance characteristics (duty point ranges)
    min_flow_rate_lps DECIMAL(8,2),          -- Minimum flow rate (L/s)
    max_flow_rate_lps DECIMAL(8,2),          -- Maximum flow rate (L/s)
    optimal_flow_rate_lps DECIMAL(8,2),      -- Optimal operating flow rate (L/s)
    min_head_pressure_kpa DECIMAL(8,2),      -- Minimum head pressure (kPa)
    max_head_pressure_kpa DECIMAL(8,2),      -- Maximum head pressure (kPa)
    optimal_head_pressure_kpa DECIMAL(8,2),  -- Optimal operating head pressure (kPa)
    
    -- Pump curve link
    model_slug VARCHAR(100),                 -- URL-friendly model name (e.g., 'cr-15-3')
    pump_curve_url VARCHAR(500),             -- Full URL to pump curve (can be auto-generated)
    
    -- Pricing
    list_price DECIMAL(10,2),
    nett_price DECIMAL(10,2),
    ip56_list_price DECIMAL(10,2),           -- IP-56 enclosure pricing
    ip56_nett_price DECIMAL(10,2),
    ip66_list_price DECIMAL(10,2),           -- IP-66 enclosure pricing
    ip66_nett_price DECIMAL(10,2),
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### C. `pump_components` Table (Accessories)
```sql
CREATE TABLE pump_components (
    id SERIAL PRIMARY KEY,
    component_type VARCHAR(50) NOT NULL,     -- inertia_base, spring, rubber_mount, crossbar
    part_number VARCHAR(100),
    description TEXT,
    specifications JSONB,                    -- Flexible JSON field for varying data
    list_price DECIMAL(10,2),
    nett_price DECIMAL(10,2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### D. `pump_bom` Table (Bill of Materials relationships)
```sql
CREATE TABLE pump_bom (
    id SERIAL PRIMARY KEY,
    pump_id INTEGER REFERENCES pumps(id),
    component_id INTEGER REFERENCES pump_components(id),
    component_type VARCHAR(50) NOT NULL,
    quantity INTEGER DEFAULT 1,
    is_optional BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### E. `inertia_bases` Table (Specialized for inertia base data)
```sql
CREATE TABLE inertia_bases (
    id SERIAL PRIMARY KEY,
    part_number VARCHAR(100) NOT NULL,
    weight_kg DECIMAL(8,3),
    length_mm INTEGER,
    width_mm INTEGER,
    depth_mm INTEGER,
    mount_height_mm INTEGER,
    list_price DECIMAL(10,2),
    nett_cost DECIMAL(10,2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### F. `seismic_springs` Table
```sql
CREATE TABLE seismic_springs (
    id SERIAL PRIMARY KEY,
    part_number VARCHAR(100) NOT NULL,
    description TEXT,
    max_load_kg DECIMAL(8,2),
    static_deflection_mm DECIMAL(8,2),
    spring_constant DECIMAL(10,4),
    stripe_1_color VARCHAR(50),              -- Color coding
    stripe_2_color VARCHAR(50),
    list_price DECIMAL(10,2),
    nett_price DECIMAL(10,2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### G. `rubber_mounts` Table
```sql
CREATE TABLE rubber_mounts (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(100) NOT NULL,
    item_description TEXT,
    static_deflection_mm DECIMAL(8,2),
    list_price DECIMAL(10,2),
    nett_price DECIMAL(10,2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### H. `crossbars` Table
```sql
CREATE TABLE crossbars (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(100) NOT NULL,
    description TEXT,
    list_price DECIMAL(10,2),
    nett_price DECIMAL(10,2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### I. `motor_protection` Table
```sql
CREATE TABLE motor_protection (
    id SERIAL PRIMARY KEY,
    description TEXT NOT NULL,
    nett_cost DECIMAL(10,2) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### J. `drip_trip_trays` Table
```sql
CREATE TABLE drip_trip_trays (
    id SERIAL PRIMARY KEY,
    series_id INTEGER REFERENCES pump_series(id),
    description VARCHAR(200) NOT NULL,
    nett_cost DECIMAL(10,2) NOT NULL,
    is_standard BOOLEAN DEFAULT TRUE,  -- Whether this is standard for the series
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### K. `pump_duty_points` Table (Historical duty point tracking)
```sql
CREATE TABLE pump_duty_points (
    id SERIAL PRIMARY KEY,
    flow_rate_lps DECIMAL(8,2) NOT NULL,     -- Flow rate in L/s
    head_pressure_kpa DECIMAL(8,2) NOT NULL, -- Head pressure in kPa
    series_id INTEGER REFERENCES pump_series(id),
    tolerance_percentage DECIMAL(5,2) DEFAULT 5.0, -- Match tolerance (±5%)
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### L. `pump_selection_history` Table (Track pump selections for duty points)
```sql
CREATE TABLE pump_selection_history (
    id SERIAL PRIMARY KEY,
    duty_point_id INTEGER REFERENCES pump_duty_points(id),
    pump_id INTEGER REFERENCES pumps(id),
    quote_id INTEGER REFERENCES quotes(id),          -- Link to actual quote
    option_id INTEGER REFERENCES quote_options(id),  -- Link to quote option
    
    -- Duty point details at time of selection
    flow_rate_lps DECIMAL(8,2) NOT NULL,
    head_pressure_kpa DECIMAL(8,2) NOT NULL,
    
    -- Pump specs at time of selection
    pump_kw_rating DECIMAL(8,2),
    pump_poles INTEGER,
    
    -- Selection metadata
    selected_by_user_id INTEGER REFERENCES users(id),
    selection_reason TEXT,                           -- Why this pump was chosen
    was_successful BOOLEAN DEFAULT TRUE,             -- Did it work out?
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### M. `pump_confidence_scores` Table (Calculated confidence for pump/duty point matches)
```sql
CREATE TABLE pump_confidence_scores (
    id SERIAL PRIMARY KEY,
    pump_id INTEGER REFERENCES pumps(id),
    duty_point_id INTEGER REFERENCES pump_duty_points(id),
    
    -- Matching statistics
    selection_count INTEGER DEFAULT 0,               -- Times selected for this duty point
    success_count INTEGER DEFAULT 0,                 -- Successful selections
    total_duty_point_selections INTEGER DEFAULT 0,   -- Total selections for this duty point
    
    -- Confidence metrics
    confidence_score DECIMAL(5,2),                   -- 0-100 percentage
    confidence_stars INTEGER,                        -- 1-5 star rating
    
    -- Match quality
    flow_rate_match_percentage DECIMAL(5,2),         -- How close to optimal flow
    head_pressure_match_percentage DECIMAL(5,2),     -- How close to optimal head
    overall_match_quality DECIMAL(5,2),              -- Combined match quality
    
    last_calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(pump_id, duty_point_id)
);
```

## 3. Pump Curve URL System

### Overview:
Links to manufacturer pump curves on Grundfos website using a consistent URL pattern.

### URL Pattern Structure:
```
Base: https://product-selection.grundfos.com/au/products/
Pattern: {base}/{series_path}/{model_slug}/{part_number}

Example:
https://product-selection.grundfos.com/au/products/cr-cre-cri-crie-crn-crne-crt-crte/cr/cr-15-3-96501699

Components:
- Base URL: https://product-selection.grundfos.com/au/products/
- Series Path: cr-cre-cri-crie-crn-crne-crt-crte/cr
- Model Slug: cr-15-3 (lowercase, hyphenated)
- Part Number: 96501699
```

### Series Path Configuration:
Each pump series has its own path pattern:

| Series | Series Path | Example |
|--------|------------|---------|
| CR/CRE/CRI/CRIE/CRN/CRNE | cr-cre-cri-crie-crn-crne-crt-crte/cr | CR 15-3 |
| NBG | nbg/nbg | NBG 100-65-200 |
| MAGNA | magna3/magna3 | MAGNA3 32-120 |
| TP | tp-tpe/tp | TP 32-120 |
| UPS | ups/ups | UPS 32-120 |

### URL Generation Logic:
```python
def generate_pump_curve_url(pump):
    """
    Generate Grundfos pump curve URL based on series configuration
    """
    # Get series configuration
    series = pump.series
    
    if not series.curve_url_pattern or not series.series_path:
        return None
    
    # Generate model slug from pump name
    # Example: "CR 15-3" → "cr-15-3"
    model_slug = pump.name.lower().replace(' ', '-').replace('/', '-')
    
    # Build full URL
    base_url = "https://product-selection.grundfos.com/au/products"
    full_url = f"{base_url}/{series.series_path}/{model_slug}-{pump.part_number}"
    
    return full_url

# Example usage:
pump = Pump(
    name="CR 15-3",
    part_number="96501699",
    series=PumpSeries(series_path="cr-cre-cri-crie-crn-crne-crt-crte/cr")
)

url = generate_pump_curve_url(pump)
# Returns: https://product-selection.grundfos.com/au/products/cr-cre-cri-crie-crn-crne-crt-crte/cr/cr-15-3-96501699
```

### Storing URLs:
Two options:

**Option 1: Store Generated URL (Recommended)**
```python
# Generate and store URL during pump creation/import
pump.pump_curve_url = generate_pump_curve_url(pump)
pump.save()
```

**Option 2: Generate On-The-Fly**
```python
# Generate URL when needed (saves storage, always uses latest pattern)
@property
def pump_curve_url(self):
    return generate_pump_curve_url(self)
```

### UI Display:
```html
<!-- In pump details modal -->
<div class="pump-curve-link">
    <a href="{{ pump.pump_curve_url }}" 
       target="_blank" 
       class="btn btn-info">
        📊 View Pump Curve
    </a>
</div>
```

### Data Requirements:
For each pump, we need:
1. **Part Number** - Manufacturer's part number (e.g., 96501699)
2. **Model Slug** - Generated from pump name (e.g., cr-15-3)
3. **Series Path** - Configured per series in pump_series table

### Future Enhancements:
- Embed pump curves directly in the app (if API available)
- Cache pump curve images locally
- Display curve overlays with duty points
- Support multiple manufacturers beyond Grundfos

## 4. Data Mapping Strategy

### BOM Structure Mapping:

#### NBG & NK Series Fields:
- Item No → `pumps.item_number`
- Name → `pumps.name`
- kW → `pumps.kw_rating`
- Poles → `pumps.poles`
- Pump List → `pumps.list_price`
- Pump Nett → `pumps.nett_price`
- IP-56 List → `pumps.ip56_list_price`
- IP-56 Nett → `pumps.ip56_nett_price`
- IP-66 List → `pumps.ip66_list_price`
- IP-66 Nett → `pumps.ip66_nett_price`
- Inertia PN → Links to `inertia_bases.part_number`
- Inertia Size → Stored in `inertia_bases` dimensions
- Standard Spring PN → Links to `seismic_springs.part_number`
- 50mm Static Spring PN → Links to `seismic_springs.part_number`
- Crossbar Nett → Links to `crossbars.nett_price`
- Motor Protection → Links to `motor_protection` (if applicable)
- Drip Trip Tray → Links to `drip_trip_trays` (series-specific pricing)

#### CR & TP Series Fields:
- Item No → `pumps.item_number`
- Name → `pumps.name`
- Pump List → `pumps.list_price`
- Pump Nett → `pumps.nett_price`
- IP-56 Nett → `pumps.ip56_nett_price`
- IP-66 Nett → `pumps.ip66_nett_price`
- Base Nett → Links to `inertia_bases.nett_cost`
- Inertia SKU → Links to `inertia_bases.part_number`
- Inertia Size → Stored in `inertia_bases` dimensions
- Inertia Nett → Links to `inertia_bases.nett_cost`
- RM Nett → Links to `rubber_mounts.nett_price`
- Mount Qty → Stored in `pump_bom.quantity`
- Seismic SKU → Links to `seismic_springs.part_number`
- Seismic Name → Links to `seismic_springs.description`
- Motor Protection → Links to `motor_protection` (if applicable)
- Drip Trip Tray → Links to `drip_trip_trays` (series-specific pricing)

#### MAGNA & UPS Series Fields:
- Item No → `pumps.item_number`
- Pump List → `pumps.list_price`
- Pump Nett → `pumps.nett_price`
- Motor Protection → Links to `motor_protection` (if applicable)
- Drip Trip Tray → Links to `drip_trip_trays` (series-specific pricing)

## 4. Implementation Phases

### Phase 1: Database Schema Creation
1. Create new pump-related models in `app/models/pumps/`
2. Create database migration script
3. Update existing product model relationships
4. Add indexes for performance

### Phase 2: Data Import Scripts
1. Create import script for NBG/NK BOM
2. Create import script for CR/TP BOM
3. Create import script for MAGNA/UPS BOM
4. Create import script for supporting components
5. Handle data validation and error reporting

### Phase 3: Admin Interface Development
1. Create pump series management interface
2. Create pump catalog management interface
3. Create component management interface
4. Add search and filtering capabilities
5. Integrate with existing product system

### Phase 4: Quote System Integration
1. Update quote system to handle pump BOMs
2. Add pump selection interface in quotes
3. Implement automatic component selection based on pump choice
4. Add pricing calculation for complete pump assemblies

### Phase 5: Testing & Validation
1. Test all import scripts with sample data
2. Validate data integrity and relationships
3. Test quote generation with pump assemblies
4. Performance testing with large datasets

## 5. File Structure

```
app/models/pumps/
├── __init__.py
├── pump_series.py
├── pump_model.py
├── pump_component.py
├── pump_bom.py
├── inertia_base.py
├── seismic_spring.py
├── rubber_mount.py
├── crossbar.py
├── motor_protection.py
├── drip_trip_tray.py
├── pump_duty_point.py
├── pump_selection_history.py
└── pump_confidence_score.py

scripts/import/
├── __init__.py
├── import_pump_series.py
├── import_nbg_pumps.py
├── import_cr_pumps.py
├── import_magna_pumps.py
├── import_components.py
├── import_pump_performance_data.py
└── validate_pump_data.py

app/utils/pumps/
├── __init__.py
├── duty_point_matcher.py
├── confidence_calculator.py
├── pump_selector.py
└── selection_tracker.py

app/features/pumps/
├── __init__.py
├── routes.py
├── forms.py
└── templates/
    ├── pumps/
    │   ├── index.html
    │   ├── series.html
    │   └── components.html
    └── admin/
        ├── pump_management.html
        └── component_management.html
```

## 6. Data Import Order

1. **Pump Series** - Create all series first (NBG, NK, CR, etc.)
   - Include series_path for pump curve URLs
   - Configure curve_url_pattern for each series
2. **Supporting Components** - Import springs, mounts, crossbars, inertia bases
3. **Main Pumps** - Import pump data with basic information
   - Include part_number for each pump
   - Generate model_slug from pump name
   - Generate pump_curve_url if part_number exists
4. **BOM Relationships** - Link pumps to their required components

### Pump Curve URL Import Example:
```python
def import_pump_with_curve_url(row, series):
    """
    Import pump and generate curve URL
    """
    # Extract pump data
    pump = Pump(
        series_id=series.id,
        item_number=row['Item No'],
        part_number=row.get('Part Number'),  # Get from data if available
        name=row['Name'],
        kw_rating=row['kW'],
        poles=row['Poles'],
        # ... other fields
    )
    
    # Generate pump curve URL if part number exists
    if pump.part_number and series.series_path:
        pump.pump_curve_url = generate_pump_curve_url(pump)
    
    return pump

# Series configuration examples:
series_configs = {
    'CR': {
        'series_path': 'cr-cre-cri-crie-crn-crne-crt-crte/cr',
        'curve_url_pattern': 'https://product-selection.grundfos.com/au/products/{series_path}/{model_slug}-{part_number}'
    },
    'NBG': {
        'series_path': 'nbg/nbg',
        'curve_url_pattern': 'https://product-selection.grundfos.com/au/products/{series_path}/{model_slug}-{part_number}'
    },
    'MAGNA': {
        'series_path': 'magna3/magna3',
        'curve_url_pattern': 'https://product-selection.grundfos.com/au/products/{series_path}/{model_slug}-{part_number}'
    }
}
```

## 7. Component-Specific Business Logic

### Motor Protection:
- **Description**: Text description of the motor protection type/level
- **Nett Cost**: Fixed cost per protection unit
- **Usage**: Optional component that can be added to any pump series
- **Selection**: Based on motor specifications or customer requirements

### Drip Trip Trays:
- **Series Dependency**: Cost varies by pump series (NBG, CR, MAGNA, etc.)
- **Binary Selection**: Either included (yes) or not included (no)
- **Pricing Logic**: 
  - Each series has its own drip trip tray cost
  - Cost is applied as a flat rate when selected
  - Can be marked as "standard" for certain series (included by default)

## 8. Validation Rules

### Data Integrity Checks:
- All pumps must have valid series_id
- All BOM relationships must reference existing components
- Pricing data must be non-negative
- Required fields must not be null
- Part numbers must be unique within component types
- Drip trip tray series_id must reference existing pump_series

### Business Logic Validation:
- kW ratings must be positive
- Pole counts must be valid (2, 4, 6, etc.)
- Component quantities must be positive integers
- Price relationships (list > nett) must be logical
- Motor protection descriptions cannot be empty
- Drip trip tray costs must be positive for each series

## 9. Quote System Integration

### Motor Protection in Quotes:
- **Selection Interface**: Dropdown or checkbox to add motor protection
- **Pricing**: Fixed cost added to total when selected
- **Display**: Show description and cost in quote line items
- **Optional**: Can be added/removed from any pump quote

### Drip Trip Trays in Quotes:
- **Selection Interface**: Yes/No toggle for each pump series
- **Dynamic Pricing**: Cost changes based on selected pump series
- **Default Behavior**: Can be set as standard for certain series
- **Display**: Show as separate line item when selected
- **Series Logic**: Automatically suggest based on pump series selection

## 10. Benefits of This Structure

1. **Flexibility**: Can handle different BOM structures from various series
2. **Scalability**: Easy to add new pump series and components
3. **Maintainability**: Clear separation of concerns and normalized data
4. **Integration**: Works seamlessly with existing product system
5. **Reporting**: Easy to generate pump-specific reports and analytics
6. **Performance**: Optimized indexes for fast queries
7. **Data Integrity**: Comprehensive validation and relationship constraints

## 11. Migration Considerations

### Existing Product Integration:
- Maintain compatibility with current product model
- Add pump-specific fields without breaking existing functionality
- Ensure backward compatibility with current quote system

### Data Migration Strategy:
- Import pump data into new tables
- Create mapping between old product IDs and new pump IDs
- Gradually migrate quote system to use new pump structure
- Maintain audit trail of all changes

## 12. Intelligent Pump Selection System

### Overview:
The system uses historical duty point data to provide intelligent pump recommendations with confidence scoring based on past successful selections.

### Duty Point Selection Process:

#### Step 1: Customer Provides Duty Point
```
User Input:
- Flow Rate: 20 L/s
- Head Pressure: 200 kPa

System searches for matching pumps within tolerance (±5%)
```

#### Step 2: Filtering Options
```
User can narrow down by:
- Series (NBG, CR, MAGNA, etc.)
- Poles (2, 4, 6)
- kW Rating (minimum/maximum)
- Other specifications
```

#### Step 3: Intelligent Matching Algorithm
```python
def find_matching_pumps(flow_rate, head_pressure, tolerance=5.0, filters=None):
    """
    Find pumps that match the duty point within tolerance
    
    Matching Logic:
    1. Flow Rate Match: flow_rate ± (flow_rate × tolerance/100)
    2. Head Pressure Match: head_pressure ± (head_pressure × tolerance/100)
    3. Apply user filters (series, poles, kW)
    4. Rank by confidence score from historical data
    """
    
    # Calculate tolerance ranges
    flow_min = flow_rate * (1 - tolerance/100)
    flow_max = flow_rate * (1 + tolerance/100)
    head_min = head_pressure * (1 - tolerance/100)
    head_max = head_pressure * (1 + tolerance/100)
    
    # Find matching pumps
    matching_pumps = Pump.query.filter(
        Pump.min_flow_rate_lps <= flow_max,
        Pump.max_flow_rate_lps >= flow_min,
        Pump.min_head_pressure_kpa <= head_max,
        Pump.max_head_pressure_kpa >= head_min
    )
    
    # Apply filters
    if filters.series_id:
        matching_pumps = matching_pumps.filter(Pump.series_id == filters.series_id)
    if filters.poles:
        matching_pumps = matching_pumps.filter(Pump.poles == filters.poles)
    if filters.min_kw:
        matching_pumps = matching_pumps.filter(Pump.kw_rating >= filters.min_kw)
    
    # Get confidence scores for each pump
    for pump in matching_pumps:
        pump.confidence = get_confidence_score(pump.id, flow_rate, head_pressure)
    
    # Sort by confidence score (highest first)
    return sorted(matching_pumps, key=lambda p: p.confidence, reverse=True)
```

#### Step 4: Confidence Score Calculation
```python
def calculate_confidence_score(pump_id, duty_point_id):
    """
    Calculate confidence score based on historical selections
    
    Scoring Factors:
    1. Selection Frequency: How often this pump was selected
    2. Success Rate: Percentage of successful implementations
    3. Match Quality: How close to optimal operating point
    4. Relative Popularity: Compared to other pumps for same duty point
    """
    
    history = PumpSelectionHistory.query.filter_by(
        pump_id=pump_id,
        duty_point_id=duty_point_id
    ).all()
    
    # Calculate metrics
    selection_count = len(history)
    success_count = sum(1 for h in history if h.was_successful)
    success_rate = (success_count / selection_count) if selection_count > 0 else 0
    
    # Get total selections for this duty point (all pumps)
    total_selections = PumpSelectionHistory.query.filter_by(
        duty_point_id=duty_point_id
    ).count()
    
    # Calculate relative frequency (how often THIS pump vs others)
    relative_frequency = (selection_count / total_selections) if total_selections > 0 else 0
    
    # Calculate match quality (how close to pump's optimal operating point)
    match_quality = calculate_match_quality(pump_id, duty_point)
    
    # Weighted confidence score (0-100)
    confidence = (
        (relative_frequency * 40) +  # 40% weight on frequency
        (success_rate * 30) +         # 30% weight on success rate
        (match_quality * 30)          # 30% weight on technical match
    ) * 100
    
    # Convert to star rating (1-5 stars)
    stars = calculate_star_rating(confidence)
    
    return {
        'confidence_score': confidence,
        'confidence_stars': stars,
        'selection_count': selection_count,
        'success_rate': success_rate * 100,
        'relative_frequency': relative_frequency * 100
    }
```

#### Step 5: Star Rating System
```python
def calculate_star_rating(confidence_score):
    """
    Convert confidence score to star rating (1-5)
    
    Rating Thresholds:
    - 5 stars: 90-100% confidence (always or almost always selected)
    - 4 stars: 75-89% confidence (usually selected)
    - 3 stars: 50-74% confidence (often selected)
    - 2 stars: 25-49% confidence (sometimes selected)
    - 1 star: 0-24% confidence (rarely selected)
    """
    if confidence_score >= 90:
        return 5
    elif confidence_score >= 75:
        return 4
    elif confidence_score >= 50:
        return 3
    elif confidence_score >= 25:
        return 2
    else:
        return 1
```

### Example Scenario:

#### Duty Point: 21 L/s @ 200 kPa

```
Search Results (within ±5% tolerance):

┌─────────────────────────────────────────────────────────────┐
│ Pump Model              │ kW  │ Poles │ Confidence │ Stars  │
├─────────────────────────────────────────────────────────────┤
│ NBG 100-65-200/219     │ 37  │  4    │    95%     │ ★★★★★ │
│ - Selected 18 times out of 19 total selections              │
│ - Success rate: 100%                                         │
│ - Optimal match: Flow 98%, Head 99%                         │
│                                                              │
│ NBG 125-80-200/188     │ 30  │  2    │    72%     │ ★★★★  │
│ - Selected 1 time out of 19 total selections                │
│ - Success rate: 100%                                         │
│ - Optimal match: Flow 95%, Head 97%                         │
└─────────────────────────────────────────────────────────────┘
```

### Historical Data Tracking:

#### When User Selects a Pump:
```python
def track_pump_selection(pump_id, flow_rate, head_pressure, quote_id, user_id):
    """
    Record the pump selection for future confidence scoring
    """
    # Find or create duty point
    duty_point = find_or_create_duty_point(flow_rate, head_pressure)
    
    # Record selection
    selection = PumpSelectionHistory(
        duty_point_id=duty_point.id,
        pump_id=pump_id,
        quote_id=quote_id,
        flow_rate_lps=flow_rate,
        head_pressure_kpa=head_pressure,
        selected_by_user_id=user_id,
        was_successful=True  # Default, can be updated later
    )
    
    db.session.add(selection)
    db.session.commit()
    
    # Recalculate confidence scores
    recalculate_confidence_scores(duty_point.id)
```

#### Updating Success Status:
```python
def mark_selection_success(selection_id, was_successful, reason=None):
    """
    Update whether a pump selection was successful
    Useful for learning from installations
    """
    selection = PumpSelectionHistory.query.get(selection_id)
    selection.was_successful = was_successful
    selection.selection_reason = reason
    
    db.session.commit()
    
    # Recalculate confidence scores
    recalculate_confidence_scores(selection.duty_point_id)
```

### Handling New Duty Points (No Historical Data):

#### When No Historical Data Exists:
```python
def search_pumps_by_duty_point(flow_rate, head_pressure, tolerance=5.0):
    """
    Search for pumps matching duty point
    Returns either:
    - List of pumps with confidence scores (if historical data exists)
    - Empty list (if no historical data exists)
    """
    # Find matching duty points within tolerance
    matching_duty_points = find_duty_points_within_tolerance(
        flow_rate, head_pressure, tolerance
    )
    
    if not matching_duty_points:
        # NO HISTORICAL DATA FOUND
        return {
            'has_historical_data': False,
            'pumps': [],
            'message': 'No historical selections found for this duty point'
        }
    
    # Historical data found - get confidence scores
    pumps_with_confidence = []
    for duty_point in matching_duty_points:
        pumps = get_pumps_for_duty_point(duty_point.id)
        pumps_with_confidence.extend(pumps)
    
    # Sort by confidence score
    pumps_with_confidence.sort(key=lambda p: p.confidence_score, reverse=True)
    
    return {
        'has_historical_data': True,
        'pumps': pumps_with_confidence,
        'duty_points_found': len(matching_duty_points)
    }
```

#### Creating New Duty Point from Manual Selection:
```python
def create_new_duty_point_selection(flow_rate, head_pressure, pump_id, 
                                   quote_id, user_id, series_id=None):
    """
    Records a NEW duty point when user manually selects a pump
    This becomes the first historical data point for this duty
    """
    # Create new duty point
    duty_point = PumpDutyPoint(
        flow_rate_lps=flow_rate,
        head_pressure_kpa=head_pressure,
        series_id=series_id,
        tolerance_percentage=5.0,
        notes=f"First selection for {flow_rate}L/s @ {head_pressure}kPa"
    )
    db.session.add(duty_point)
    db.session.flush()
    
    # Record the selection
    selection = PumpSelectionHistory(
        duty_point_id=duty_point.id,
        pump_id=pump_id,
        quote_id=quote_id,
        flow_rate_lps=flow_rate,
        head_pressure_kpa=head_pressure,
        selected_by_user_id=user_id,
        was_successful=True,  # Assumed successful initially
        selection_reason="First selection for this duty point"
    )
    db.session.add(selection)
    db.session.commit()
    
    # Initialize confidence score (100% since it's the only selection)
    initialize_confidence_score(pump_id, duty_point.id)
    
    return duty_point
```

#### Building Historical Data Over Time:
```
Initial State (No Data):
  21 L/s @ 200 kPa → No results → User selects NBG 100-65-200/219
  
After 1st Selection:
  21 L/s @ 200 kPa → Shows: NBG 100-65-200/219 (★★★★★ 100%)
  
After 5th Selection (4x NBG 100-65, 1x NBG 125-80):
  21 L/s @ 200 kPa → Shows:
    - NBG 100-65-200/219 (★★★★★ 95%)
    - NBG 125-80-200/188 (★★★☆☆ 55%)
    
After 20th Selection (18x NBG 100-65, 2x NBG 125-80):
  21 L/s @ 200 kPa → Shows:
    - NBG 100-65-200/219 (★★★★★ 95%)
    - NBG 125-80-200/188 (★★★☆☆ 60%)
```

## 13. Complete Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ User opens Quote Revision                                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ Click "Add Pump Assembly"                                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ Choose Search Method:                                       │
│ ○ Search by Duty Point (Intelligent)                       │
│ ○ Search Manually (Direct)                                  │
│ ○ Browse All Pumps (Catalog)                               │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┼───────────┐
         │           │           │
         ▼           ▼           ▼
┌────────────┐ ┌────────────┐ ┌──────────────┐
│Path A:     │ │Path B:     │ │Path C:       │
│Duty Point  │ │Manual      │ │Browse All    │
│Search      │ │Search      │ │Pumps         │
└─────┬──────┘ └─────┬──────┘ └──────┬───────┘
      │              │                │
      ▼              ▼                │
┌────────────┐ ┌────────────────┐    │
│Enter Duty  │ │Search Field:   │    │
│Point       │ │"NBG 100-65"    │    │
│21L/s       │ │                │    │
│200kPa      │ │Live results as │    │
└─────┬──────┘ │you type        │    │
      │        └─────┬──────────┘    │
      ▼              │                │
┌────────────┐       │                │
│Search      │       │                │
│Historical  │       │                │
│Data        │       │                │
└─────┬──────┘       │                │
      │              │                │
  ┌───┴───┐          │                │
  ▼       ▼          │                │
┌────┐ ┌─────┐       │                │
│Found││No   │       │                │
│Data ││Data │       │                │
└──┬──┘└──┬──┘       │                │
   │      │          │                │
   │      ▼          │                │
   │   ┌──────────┐  │                │
   │   │Browse    │  │                │
   │   │Manually  │  │                │
   │   └────┬─────┘  │                │
   │        │        │                │
   └────────┴────────┴────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ User Selects Pump                                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ System Records Selection (if from duty point search)        │
│ • Creates duty_point record (if new)                        │
│ • Creates selection_history record                          │
│ • Initializes confidence_score                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ Configure Pump Assembly                                     │
│ • Mounting: Inertia Base / Base Only / Crossbar / None     │
│ • Springs: Standard / 50mm Static / None                    │
│ • Rubber Mounts: Yes/No + Quantity                          │
│ • Motor Protection: Yes/No                                  │
│ • Drip Trip Tray: Yes/No                                    │
│ • IP Rating: Standard / IP-56 / IP-66                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ Create Line Items for Selected Components                   │
│ • Pump (always)                                             │
│ • Selected mounting component                               │
│ • Selected springs                                          │
│ • Selected accessories                                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ Pump Assembly Added to Quote                                │
│ If selected via duty point: future searches will show       │
│ this pump with confidence score                             │
└─────────────────────────────────────────────────────────────┘
```

## 14. Adding Pumps to Deals - Business Logic Walkthrough

### Current System Overview:
The existing system follows this hierarchy:
- **Deal** → **Quote Recipients** → **Quotes** → **Quote Options** → **Line Items**

### Pump Integration Business Logic:

#### Step 1: Pump Selection Interface (Enhanced with Duty Points)
```
User Journey:
1. User opens a quote revision
2. User clicks "Add Pump Assembly" button in quote option
3. Modal opens with THREE options:
   
   Option 1: Search by Duty Point (Intelligent)
   Option 2: Search Manually (Direct)
   Option 3: Skip to Browse All Pumps

Initial Modal:
┌──────────────────────────────────────────────────┐
│ How would you like to find a pump?               │
├──────────────────────────────────────────────────┤
│ ○ Search by Duty Point (Recommended)             │
│   Use historical data to find best matches       │
│                                                   │
│ ○ Search Manually                                 │
│   Search by pump name, part number, or specs     │
│                                                   │
│ ○ Browse All Pumps                                │
│   Browse the complete pump catalog               │
└──────────────────────────────────────────────────┘

Path A) DUTY POINT SEARCH:
   - User enters flow rate and head pressure
   - System searches historical data
   - Shows results with confidence OR no data message
   
Path B) MANUAL SEARCH:
   - Direct search field appears
   - Search by: Name, Part Number, Series, SKU
   - Instant results as user types
   - NO duty point required
   - NO historical data involved
   - User selects pump → proceeds to configuration
   
Path C) BROWSE ALL:
   - Shows complete pump catalog
   - Filter by Series, Poles, kW, etc.
   - Paginated results
   - User selects pump → proceeds to configuration
```

#### Step 2: Pump Configuration
```
After pump selection:
1. System loads pump details (kW, poles, base pricing)
2. Shows mandatory components (inertia base, springs, mounts)
3. Shows optional components (motor protection, drip trip tray)
4. User can modify quantities and select accessories
```

#### Step 3: Component Selection Logic

##### Default Components (Pre-Selected, but User Can Change):
- **Inertia Base**: ✓ Checked by default (can be unchecked or swapped for base only)
- **Seismic Springs (Standard)**: ✓ Checked by default (can swap for 50mm Static Springs or uncheck)
- **Rubber Mounts**: Quantity based on pump size (can be modified)
- **Crossbars**: Available as alternative to inertia base

##### Optional Components (User Choice):
- **Motor Protection**: ☐ Unchecked by default
- **Drip Trip Tray**: ☐ Unchecked by default
- **IP Rating Upgrade**: Standard (default) → IP-56 → IP-66

##### Component Flexibility:
Users can create different configurations:
- **Full Setup**: Inertia Base + Seismic Springs + Mounts + Crossbars
- **Base Only**: Just the base without inertia or springs
- **Crossbar Alternative**: Crossbar instead of Inertia Base
- **Spring Options**: Switch between Standard Seismic or 50mm Static Springs
- **Minimal Setup**: Pump only, no accessories

#### Step 4: Pricing Calculation (Dynamic Based on Selection)
```
Total Pump Assembly Cost = 
  Pump Base Price +
  Inertia Base Cost (if selected) +
  OR Base Only Cost (if selected instead of inertia) +
  (Spring Cost × Quantity) (if selected - Standard OR 50mm Static) +
  (Rubber Mount Cost × Quantity) (if selected) +
  Crossbar Cost (if selected) +
  Motor Protection Cost (if selected) +
  Drip Trip Tray Cost (if selected) +
  IP Rating Upgrade Cost (if selected)

Example Configurations:

1. Full Setup (Default):
   = Pump + Inertia Base + Seismic Springs (4x) + Rubber Mounts (4x)
   
2. Base Only:
   = Pump + Base (no inertia, no springs)
   
3. Crossbar Setup:
   = Pump + Crossbar + Seismic Springs (4x)
   
4. Minimal:
   = Pump only
```

#### Step 5: Line Item Creation (Dynamic Based on User Selection)
```
Create individual line items ONLY for selected components:

Required:
- Main Pump (quantity: 1) - always included

Optional (based on user selection):
- Inertia Base (quantity: 1) - if checked
- Base Only (quantity: 1) - if checked (alternative to inertia)
- Crossbar (quantity: Z) - if checked (alternative to inertia)
- Seismic Springs - Standard (quantity: X) - if checked
- Seismic Springs - 50mm Static (quantity: X) - if checked (alternative)
- Rubber Mounts (quantity: Y) - if checked
- Motor Protection (quantity: 1) - if checked
- Drip Trip Tray (quantity: 1) - if checked
- IP Rating Upgrade - if selected

Example Line Items for Default Configuration:
1. NBG 100-65-200/219 Pump (1x) - $4,211.50
2. Inertia Base 1500x800x225 (1x) - $741.99
3. Seismic Springs CLM-98 (4x) - $153.30
4. Rubber Mounts (4x) - $668.94
Total: $5,775.73
```

### Technical Implementation:

#### New Database Tables for Pump Quotes:
```sql
-- Track pump assemblies within quotes
CREATE TABLE quote_pump_assemblies (
    id SERIAL PRIMARY KEY,
    option_id INTEGER REFERENCES quote_options(id),
    pump_id INTEGER REFERENCES pumps(id),
    motor_protection_id INTEGER REFERENCES motor_protection(id),
    drip_trip_tray_selected BOOLEAN DEFAULT FALSE,
    ip_rating VARCHAR(10) DEFAULT 'standard', -- standard, ip56, ip66
    total_cost DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Track individual pump components in quotes
CREATE TABLE quote_pump_components (
    id SERIAL PRIMARY KEY,
    assembly_id INTEGER REFERENCES quote_pump_assemblies(id),
    component_type VARCHAR(50), -- pump, inertia_base, spring, mount, etc.
    component_id INTEGER, -- References appropriate component table
    quantity INTEGER DEFAULT 1,
    unit_cost DECIMAL(10,2),
    total_cost DECIMAL(10,2),
    line_item_id INTEGER REFERENCES quote_line_items(id)
);
```

#### API Endpoints for Pump Selection:
```
GET /api/pumps/series/{series_id}/models
POST /api/quotes/{option_id}/pump-assembly
GET /api/pumps/{pump_id}/components
POST /api/quotes/{option_id}/pump-assembly/configure
```

#### Frontend Components:
```
1. PumpSeriesSelector.vue
2. PumpModelSelector.vue
3. PumpConfigurationModal.vue
4. ComponentSelector.vue
5. PricingCalculator.vue
```

### User Interface Flow:

#### 0. Initial Selection Modal:
```
┌─────────────────────────────────────────────────────┐
│ Add Pump Assembly                                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│ How would you like to find a pump?                 │
│                                                     │
│ ┌─────────────────────────────────────────────┐   │
│ │ ● Search by Duty Point (Recommended)         │   │
│ │                                               │   │
│ │   📊 Use historical data to find pumps that  │   │
│ │   work best for your specific flow rate and  │   │
│ │   head pressure requirements.                 │   │
│ │                                               │   │
│ │ [Continue with Duty Point Search]             │   │
│ └─────────────────────────────────────────────┘   │
│                                                     │
│ ┌─────────────────────────────────────────────┐   │
│ │ ○ Search Manually                             │   │
│ │                                               │   │
│ │   🔍 Quick search by pump name, part number, │   │
│ │   or model. Perfect when you already know    │   │
│ │   which pump you need.                        │   │
│ │                                               │   │
│ │ [Search by Name/Part Number]                  │   │
│ └─────────────────────────────────────────────┘   │
│                                                     │
│ ┌─────────────────────────────────────────────┐   │
│ │ ○ Browse All Pumps                            │   │
│ │                                               │   │
│ │   📚 Browse the complete catalog with         │   │
│ │   filters for series, kW, poles, etc.        │   │
│ │                                               │   │
│ │ [Browse Pump Catalog]                         │   │
│ └─────────────────────────────────────────────┘   │
│                                                     │
│ [Cancel]                                            │
└─────────────────────────────────────────────────────┘
```

#### 1. Duty Point Entry Modal:
```
┌─────────────────────────────────────────────────────┐
│ Add Pump Assembly - Enter Duty Point               │
├─────────────────────────────────────────────────────┤
│ Required Specifications:                            │
│                                                     │
│ Flow Rate (L/s):     [____21____]                  │
│ Head Pressure (kPa): [___200____]                  │
│                                                     │
│ Tolerance: [±5%▼] [±10%] [±15%]                    │
│                                                     │
│ Optional Filters:                                   │
│ ☐ Series:  [NBG ▼] [CR ▼] [MAGNA▼] [All]          │
│ ☐ Poles:   [2] [4] [6] [All]                       │
│ ☐ kW Min:  [____] kW Max: [____]                   │
│                                                     │
│ [Cancel] [Find Matching Pumps]                      │
└─────────────────────────────────────────────────────┘
```

#### 1b. Manual Search Modal (Direct Search):
```
┌──────────────────────────────────────────────────────────────┐
│ Search for Pump                                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ Search by name, part number, or model:                      │
│ [_NBG 100-65-200_________________] 🔍                        │
│                                                              │
│ Quick Filters:                                               │
│ Series: [All ▼] [NBG] [CR] [MAGNA] [TP] [UPS]              │
│                                                              │
│ Search Results (5 found):                                    │
│                                                              │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ NBG 100-65-200/219                                    │   │
│ │ Part #: 99817787 | 37 kW | 4 Poles                   │   │
│ │ $5,319.00 nett                                        │   │
│ │ [📊 View Curve] [Select This Pump]                    │   │
│ └──────────────────────────────────────────────────────┘   │
│                                                              │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ NBG 100-65-200/217                                    │   │
│ │ Part #: 99817788 | 30 kW | 2 Poles                   │   │
│ │ $4,899.00 nett                                        │   │
│ │ [📊 View Curve] [Select This Pump]                    │   │
│ └──────────────────────────────────────────────────────┘   │
│                                                              │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ NBG 100-80-160/176                                    │   │
│ │ Part #: 99801137 | 30 kW | 4 Poles                   │   │
│ │ $7,036.50 nett                                        │   │
│ │ [📊 View Curve] [Select This Pump]                    │   │
│ └──────────────────────────────────────────────────────┘   │
│                                                              │
│ [Back] [Show More Results]                                   │
└──────────────────────────────────────────────────────────────┘

Features:
- Live search as you type
- Search across: Name, Part Number, Item No, SKU, Series
- Results appear instantly (no duty point needed)
- Shows pricing immediately
- Quick series filters for faster narrowing
- 📊 View Curve button opens Grundfos pump curve in new tab
```

#### 2a. Intelligent Pump Results Modal (Historical Data Found):
```
┌──────────────────────────────────────────────────────────────┐
│ Matching Pumps for 21 L/s @ 200 kPa (±5%)                   │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ ★★★★★ 95% Confidence                                  │   │
│ │ NBG 100-65-200/219                                    │   │
│ │ 37 kW | 4 Poles | $5,319.00                          │   │
│ │                                                        │   │
│ │ Historical Performance:                                │   │
│ │ • Selected 18 times out of 19 for this duty point     │   │
│ │ • 100% success rate                                    │   │
│ │ • Flow match: 98% | Head match: 99%                   │   │
│ │                                                        │   │
│ │ [Select This Pump]                                     │   │
│ └──────────────────────────────────────────────────────┘   │
│                                                              │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ ★★★★☆ 72% Confidence                                  │   │
│ │ NBG 125-80-200/188                                    │   │
│ │ 30 kW | 2 Poles | $5,230.00                          │   │
│ │                                                        │   │
│ │ Historical Performance:                                │   │
│ │ • Selected 1 time out of 19 for this duty point       │   │
│ │ • 100% success rate                                    │   │
│ │ • Flow match: 95% | Head match: 97%                   │   │
│ │                                                        │   │
│ │ [Select This Pump]                                     │   │
│ └──────────────────────────────────────────────────────┘   │
│                                                              │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ ★★☆☆☆ No Historical Data                              │   │
│ │ NBG 80-50-250/254                                     │   │
│ │ 30 kW | 2 Poles | $5,328.50                          │   │
│ │                                                        │   │
│ │ Performance:                                           │   │
│ │ • Never selected for this duty point                  │   │
│ │ • Flow match: 92% | Head match: 94%                   │   │
│ │                                                        │   │
│ │ [Select This Pump]                                     │   │
│ └──────────────────────────────────────────────────────┘   │
│                                                              │
│ [Back] [Show More Results]                                   │
└──────────────────────────────────────────────────────────────┘
```

#### 2b. No Historical Data Modal:
```
┌──────────────────────────────────────────────────────────────┐
│ No Historical Data for 21 L/s @ 200 kPa (±5%)               │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│         ⚠️  No Selection History Available                   │
│                                                              │
│  We couldn't find any historical pump selections            │
│  for this duty point within the specified tolerance.        │
│                                                              │
│  Would you like to:                                          │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ 📋 Browse Available Pumps                           │    │
│  │                                                      │    │
│  │ Manually select a pump from the catalog.            │    │
│  │ Your selection will be recorded for future use.     │    │
│  │                                                      │    │
│  │ [Browse Pumps Manually]                              │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ 🔧 Adjust Search Tolerance                          │    │
│  │                                                      │    │
│  │ Increase tolerance to ±10% or ±15%                  │    │
│  │ to find more potential matches.                     │    │
│  │                                                      │    │
│  │ [Adjust Tolerance]                                   │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│ [Back to Search]                                             │
└──────────────────────────────────────────────────────────────┘
```

#### 2c. Manual Pump Selection Modal (When No Historical Data):
```
┌──────────────────────────────────────────────────────────────┐
│ Select Pump for 21 L/s @ 200 kPa                            │
├──────────────────────────────────────────────────────────────┤
│ ℹ️  This will be the FIRST selection for this duty point    │
│                                                              │
│ Filter by Series:                                            │
│ [All ▼] [NBG] [CR] [MAGNA] [TP] [UPS]                      │
│                                                              │
│ Filter by Specifications:                                    │
│ Poles: [All ▼] [2] [4] [6]                                  │
│ kW: Min [___] Max [___]                                      │
│                                                              │
│ Search: [___________________________] 🔍                      │
│                                                              │
│ Available Pumps:                                             │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ NBG 100-65-200/219                                    │   │
│ │ 37 kW | 4 Poles | $5,319.00                          │   │
│ │ Flow Range: 18-25 L/s | Head: 180-220 kPa           │   │
│ │ [Select This Pump]                                     │   │
│ └──────────────────────────────────────────────────────┘   │
│                                                              │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ NBG 125-80-200/188                                    │   │
│ │ 30 kW | 2 Poles | $5,230.00                          │   │
│ │ Flow Range: 19-24 L/s | Head: 190-210 kPa           │   │
│ │ [Select This Pump]                                     │   │
│ └──────────────────────────────────────────────────────┘   │
│                                                              │
│ [Back] [Load More]                                           │
└──────────────────────────────────────────────────────────────┘
```

#### 3. Configuration Modal:
```
┌──────────────────────────────────────────────────────┐
│ Configure Pump Assembly                              │
├──────────────────────────────────────────────────────┤
│ Pump: NBG 125-100-200/219                            │
│ Part #: 99801352 | 11 kW | 4 Poles                  │
│ Base Price: $4,211.50                                │
│                                                      │
│ [📊 View Pump Curve on Grundfos Website]            │
│                                                      │
│ Mounting Components (Select One):                    │
│ ● Inertia Base 1500x800x225 - $741.99               │
│ ○ Base Only - $450.00                                │
│ ○ Crossbar Alternative - $284.76                     │
│ ○ None (Pump Only)                                   │
│                                                      │
│ Vibration Isolation:                                 │
│ Spring Type:                                         │
│ ● Standard Seismic Springs (CLM-98)                  │
│ ○ 50mm Static Springs (CDM-53)                       │
│ ○ None                                               │
│ Quantity: [4▼] @ $153.30 each = $613.20             │
│                                                      │
│ ☑ Rubber Mounts                                      │
│ Quantity: [4▼] @ $11.83 each = $47.32               │
│                                                      │
│ Additional Options:                                  │
│ ☐ Motor Protection - $125.00                         │
│ ☐ Drip Trip Tray - $85.00                            │
│                                                      │
│ IP Rating: [Standard ▼] [IP-56] [IP-66]             │
│                                                      │
│ ─────────────────────────────────────────────        │
│ Subtotal: $5,517.01                                  │
│ Total: $5,517.01                                     │
│                                                      │
│ [Reset to Defaults] [Cancel] [Add to Quote]         │
└──────────────────────────────────────────────────────┘
```

### Business Rules:

#### 1. Component Selection Rules:
- **Mounting Options**: User can select ONE of: Inertia Base, Base Only, Crossbar, or None
- **Spring Options**: User can select ONE of: Standard Seismic, 50mm Static, or None
- **Default Configuration**: Inertia Base + Standard Seismic Springs (both checked by default)
- **Spring Quantity**: Adjustable based on pump requirements (typically 4, but can vary)
- **Rubber Mounts**: Independent checkbox, quantity adjustable
- **Mutually Exclusive**: Cannot select both Inertia Base AND Base Only simultaneously

#### 2. Pricing Rules:
- **Motor Protection**: Fixed cost regardless of pump
- **Drip Trip Tray**: Cost varies by pump series
- **IP Rating**: Upgrade costs are additive to base pump price
- **Component Pricing**: Each component priced individually
- **Dynamic Total**: Recalculates as user changes selections

#### 3. Validation Rules:
- **Pump Required**: At minimum, must include the pump itself
- **Quantity Limits**: Spring/mount quantities must be reasonable (1-12 typically)
- **Compatibility**: Components must be compatible with selected pump series
- **Pricing**: All costs must be positive and valid
- **Spring Type**: Can only select ONE spring type at a time (not both)

#### 4. Default Behavior:
- **On Modal Open**: Inertia Base and Standard Seismic Springs pre-checked
- **Reset Button**: Returns to default configuration (Inertia + Standard Springs)
- **Suggested Quantities**: System suggests optimal quantities based on pump model
- **User Override**: All defaults can be changed or unchecked by user

### Integration with Existing Quote System:

#### 1. Line Item Generation (Dynamic Based on User Selection):
```python
def create_pump_assembly_line_items(option_id, pump_assembly_config):
    """
    Creates individual line items ONLY for selected components
    """
    line_items = []
    
    # Main pump (always included)
    line_items.append(create_line_item(
        option_id=option_id,
        product_id=pump_assembly_config.pump_id,
        quantity=1,
        unit_price=pump_assembly_config.pump_price
    ))
    
    # Mounting component (only if selected)
    if pump_assembly_config.mounting_type == 'inertia_base':
        line_items.append(create_line_item(
            option_id=option_id,
            product_id=pump_assembly_config.inertia_base_id,
            quantity=1,
            unit_price=pump_assembly_config.inertia_base_price
        ))
    elif pump_assembly_config.mounting_type == 'base_only':
        line_items.append(create_line_item(
            option_id=option_id,
            product_id=pump_assembly_config.base_id,
            quantity=1,
            unit_price=pump_assembly_config.base_price
        ))
    elif pump_assembly_config.mounting_type == 'crossbar':
        line_items.append(create_line_item(
            option_id=option_id,
            product_id=pump_assembly_config.crossbar_id,
            quantity=pump_assembly_config.crossbar_quantity,
            unit_price=pump_assembly_config.crossbar_price
        ))
    
    # Springs (only if selected, and based on type)
    if pump_assembly_config.spring_type == 'standard_seismic':
        line_items.append(create_line_item(
            option_id=option_id,
            product_id=pump_assembly_config.standard_spring_id,
            quantity=pump_assembly_config.spring_quantity,
            unit_price=pump_assembly_config.standard_spring_price
        ))
    elif pump_assembly_config.spring_type == '50mm_static':
        line_items.append(create_line_item(
            option_id=option_id,
            product_id=pump_assembly_config.static_spring_id,
            quantity=pump_assembly_config.spring_quantity,
            unit_price=pump_assembly_config.static_spring_price
        ))
    
    # Rubber mounts (only if selected)
    if pump_assembly_config.include_rubber_mounts:
        line_items.append(create_line_item(
            option_id=option_id,
            product_id=pump_assembly_config.rubber_mount_id,
            quantity=pump_assembly_config.mount_quantity,
            unit_price=pump_assembly_config.mount_price
        ))
    
    # Optional components
    if pump_assembly_config.include_motor_protection:
        line_items.append(create_line_item(
            option_id=option_id,
            product_id=pump_assembly_config.motor_protection_id,
            quantity=1,
            unit_price=pump_assembly_config.motor_protection_price
        ))
    
    if pump_assembly_config.include_drip_trip_tray:
        line_items.append(create_line_item(
            option_id=option_id,
            product_id=pump_assembly_config.drip_trip_tray_id,
            quantity=1,
            unit_price=pump_assembly_config.drip_trip_tray_price
        ))
    
    return line_items
```

#### 2. Quote Calculation (Dynamic):
```python
def calculate_pump_assembly_total(pump_assembly_config):
    """
    Calculates total cost of pump assembly based on selected components
    """
    total = 0
    
    # Pump base price (always included)
    total += pump_assembly_config.pump_price
    
    # Mounting component (only if selected)
    if pump_assembly_config.mounting_type == 'inertia_base':
        total += pump_assembly_config.inertia_base_price
    elif pump_assembly_config.mounting_type == 'base_only':
        total += pump_assembly_config.base_price
    elif pump_assembly_config.mounting_type == 'crossbar':
        total += (pump_assembly_config.crossbar_price * 
                 pump_assembly_config.crossbar_quantity)
    
    # Springs (only if selected)
    if pump_assembly_config.spring_type == 'standard_seismic':
        total += (pump_assembly_config.standard_spring_price * 
                 pump_assembly_config.spring_quantity)
    elif pump_assembly_config.spring_type == '50mm_static':
        total += (pump_assembly_config.static_spring_price * 
                 pump_assembly_config.spring_quantity)
    
    # Rubber mounts (only if selected)
    if pump_assembly_config.include_rubber_mounts:
        total += (pump_assembly_config.mount_price * 
                 pump_assembly_config.mount_quantity)
    
    # Optional components
    if pump_assembly_config.include_motor_protection:
        total += pump_assembly_config.motor_protection_price
    
    if pump_assembly_config.include_drip_trip_tray:
        total += pump_assembly_config.drip_trip_tray_price
    
    # IP rating upgrade
    if pump_assembly_config.ip_rating == 'ip56':
        total += pump_assembly_config.ip56_upgrade_cost
    elif pump_assembly_config.ip_rating == 'ip66':
        total += pump_assembly_config.ip66_upgrade_cost
    
    return total
```

### Configuration Examples:

#### Example 1: Full Setup (Default)
```
Pump: NBG 100-65-200/219 - $4,211.50
✓ Inertia Base - $741.99
✓ Standard Seismic Springs (4x) - $613.20
✓ Rubber Mounts (4x) - $47.32
Total: $5,614.01
```

#### Example 2: Base Only Setup
```
Pump: NBG 100-65-200/219 - $4,211.50
✓ Base Only - $450.00
Total: $4,661.50
```

#### Example 3: Crossbar Alternative
```
Pump: NBG 100-65-200/219 - $4,211.50
✓ Crossbar - $284.76
✓ 50mm Static Springs (4x) - $668.94
Total: $5,165.20
```

#### Example 4: Minimal (Pump Only)
```
Pump: NBG 100-65-200/219 - $4,211.50
Total: $4,211.50
```

#### Example 5: Custom Configuration
```
Pump: NBG 100-65-200/219 - $4,211.50
✓ Inertia Base - $741.99
✓ 50mm Static Springs (6x) - $1,003.41
✓ Motor Protection - $125.00
✓ Drip Trip Tray - $85.00
Total: $6,166.90
```

### Benefits of This Approach:

1. **Maximum Flexibility**: User controls every component
2. **Granular Control**: Each component is a separate line item
3. **Transparency**: Customer can see exactly what they're paying for
4. **Cost Options**: Different configurations for different budgets
5. **Compatibility**: Works with existing quote system
6. **Reporting**: Detailed component-level reporting
7. **Accurate Pricing**: Dynamic calculation based on actual selection
8. **User-Friendly Defaults**: Smart defaults speed up common configurations

## 15. Key Workflow Points

### The Complete User Experience - THREE PATHS:

#### Path A: Duty Point Search (Intelligent - Recommended)

**When Historical Data Exists:**
1. User chooses "Search by Duty Point"
2. Enters duty point (21 L/s @ 200 kPa)
3. System finds historical selections
4. Displays pumps ranked by confidence (★★★★★)
5. User selects pump → configures components → adds to quote
6. Selection reinforces confidence score for this duty point

**When No Historical Data:**
1. User chooses "Search by Duty Point"
2. Enters duty point (21 L/s @ 200 kPa)
3. System finds NO historical selections
4. Message: "No historical data available"
5. User clicks "Browse Pumps Manually"
6. User selects pump from catalog
7. **System creates NEW duty point record**
8. User configures components → adds to quote
9. **This becomes first historical data point (100% confidence)**
10. Next time someone searches similar duty point → this pump appears!

#### Path B: Manual Search (Direct - Fast)
1. User chooses "Search Manually"
2. Types in search field: "NBG 100-65" or part number "99817787"
3. Live results appear as user types
4. Shows matching pumps with pricing
5. User selects pump → configures components → adds to quote
6. **NO duty point recorded** (direct selection)
7. **NO historical data created** (because no duty point was entered)

#### Path C: Browse All Pumps (Catalog - Exploratory)
1. User chooses "Browse All Pumps"
2. Views complete pump catalog
3. Applies filters (Series, kW, Poles, etc.)
4. Browses through paginated results
5. User selects pump → configures components → adds to quote
6. **NO duty point recorded** (catalog browse)
7. **NO historical data created** (because no duty point was entered)

### Comparison of Three Paths:

| Feature | Path A: Duty Point | Path B: Manual Search | Path C: Browse All |
|---------|-------------------|----------------------|-------------------|
| **Use Case** | Know requirements | Know pump model | Explore options |
| **Input Required** | Flow rate + head | Pump name/part# | Just filters |
| **Speed** | Medium | Fast | Slow |
| **Intelligence** | ✓ Shows confidence | ✗ No intelligence | ✗ No intelligence |
| **Historical Data** | ✓ Creates/uses | ✗ Not recorded | ✗ Not recorded |
| **Best For** | Requirements-based | Quick reorders | Discovery |
| **Learning** | ✓ Improves system | ✗ No learning | ✗ No learning |

### Data Learning Cycle (Path A Only):
```
Path A: Duty Point Search
   ↓
Search → No Data → Manual Selection → Record → Future Searches Find It
   ↑                                                            ↓
   └────────────────── Learning Loop ──────────────────────────┘

Path B & C: Manual/Browse
   ↓
Direct Selection → No Recording → No Future Intelligence
   (Fast but no learning)
```

### Key Benefits:
- **Flexibility**: Three ways to find pumps based on user needs
- **Self-Learning**: Path A builds intelligence over time
- **Speed Options**: Quick manual search when you know the pump
- **Discovery**: Browse mode for exploring options
- **No Upfront Data Required**: Start with zero historical data
- **User Choice**: Users pick the method that suits their workflow
- **Fallback Methods**: Always have alternatives available

## 16. Key Features Summary

### Intelligent Pump Selection System:
1. **Duty Point Matching**: Enter flow rate and head pressure, system finds matching pumps within tolerance
2. **Confidence Scoring**: Historical data shows which pumps work best for specific duty points
3. **Star Rating System**: Visual 1-5 star rating based on historical success
4. **Filtering Options**: Narrow by series, poles, kW rating, and other specs
5. **Learning System**: Gets smarter over time as more selections are tracked

### Confidence Calculation Factors:
- **40% Selection Frequency**: How often this pump is chosen for similar duty points
- **30% Success Rate**: Percentage of successful installations
- **30% Match Quality**: How close to pump's optimal operating point

### Business Benefits:
- **Faster Quoting**: Historical data speeds up pump selection
- **Reduced Errors**: Confidence scores help avoid wrong pump choices
- **Knowledge Capture**: System learns from experienced staff
- **New Staff Training**: New users benefit from historical knowledge
- **Consistency**: Standardized approach to pump selection

## 15. Implementation Phases

### Phase 1: Database Schema ✅ **COMPLETED**
- [x] Create all pump-related database tables
- [x] Add duty point and confidence tracking tables
- [x] Create database migration scripts
- [x] Test schema integrity

**Status**: All models created in `app/models/pumps/`:
- ✅ pump_model.py
- ✅ pump_series.py
- ✅ pump_component.py
- ✅ pump_bom.py
- ✅ inertia_base.py
- ✅ seismic_spring.py
- ✅ rubber_mount.py
- ✅ crossbar.py
- ✅ motor_protection.py
- ✅ drip_trip_tray.py
- ✅ pump_duty_point.py
- ✅ pump_selection_history.py
- ✅ pump_confidence_score.py

### Phase 2: Data Import ⚠️ **PARTIALLY COMPLETED**
- [x] Import pump series data
- [x] Import pump models with performance specs
- [x] Import all components (springs, bases, mounts, etc.)
- [ ] Import historical duty point data (if available)
- [ ] Validate all imported data

**Status**: Import scripts exist in `scripts/import/`:
- ✅ import_pump_data.py (main import script)
- ⚠️ Historical duty point data not yet imported (system will build this over time)

### Phase 3: Core Business Logic ⚠️ **PARTIALLY COMPLETED**
- [x] Build duty point matching algorithm
- [x] Create pump selection tracking
- [x] Build component BOM logic
- [x] Test all calculations
- [ ] Implement confidence score calculation (API exists but not fully integrated)

**Status**: 
- ✅ Duty point search working
- ✅ Manual search working
- ✅ Browse all pumps working
- ✅ Component pricing calculations working
- ⚠️ Confidence scoring needs API integration

### Phase 4: User Interface ⚠️ **IN PROGRESS**
- [x] Create duty point entry modal
- [x] Build intelligent results display
- [x] Implement pump configuration modal
- [x] Add filtering and sorting options
- [ ] **Add plant reference section to configuration modal** ⬅️ CURRENT TASK
- [ ] Complete integration with existing quote system (API endpoint stub exists)
- [ ] Admin interface for component descriptions

**Status**: 
- ✅ Main pump selection modal (`_add_pump_modal.html`)
- ✅ Configuration modal exists with all components
- ✅ JavaScript implementation (`pump_selection.js`)
- ✅ CSS styling (`pump_selection.css`)
- 🚧 Plant reference section (designed, not yet coded)
- 🚧 API endpoint for adding to quote (stub exists, line 757-785 in pump_selection.js)
- ❌ Admin route for managing descriptions

### Phase 5: Testing & Refinement 🔄 **PENDING**
- [ ] Test with real duty points
- [ ] Validate confidence scores
- [ ] User acceptance testing
- [ ] Performance optimization
- [ ] Bug fixes and refinements

**Status**: Waiting for Phase 4 completion

### Phase 6: Training & Rollout 🔄 **PENDING**
- [ ] Create user documentation
- [ ] Train staff on new system
- [ ] Gradual rollout to production
- [ ] Monitor initial usage
- [ ] Collect feedback

**Status**: Not started

## 16. Next Steps - UPDATED PRIORITY ORDER

### 🔥 IMMEDIATE PRIORITIES (Current Sprint)

1. **✅ DONE: Review and Approve Schema** - Schema validated and implemented
2. **✅ DONE: Create Database Models** - All SQLAlchemy models created
3. **✅ DONE: Create Migration Script** - Database migrations complete
4. **✅ DONE: Develop Matching Algorithm** - Duty point matcher implemented
5. **✅ DONE: Implement Pump Selection UI** - Selection and configuration modals created
6. **✅ DONE: Develop Import Scripts** - Import scripts working

### 🚧 IN PROGRESS (This Week)

7. **🚧 Add Plant Reference Section** - Add plant reference field to configuration modal
   - Design complete (CHWP-01, HWP-01 style naming)
   - Need to add HTML section after line 253 in `_add_pump_modal.html`
   - Need to update JavaScript in `pump_selection.js`
   - Need to support quantity (for multiple identical assemblies)
   
8. **🚧 Complete Quote Integration API** - Finish the add-to-quote endpoint
   - JavaScript stub exists (line 757-785 in pump_selection.js)
   - Need to create backend route in `app/features/deals/pump_routes.py`
   - Need to create line items for pump assembly
   - Need to handle plant reference in line items

9. **🚧 PDF Quote Display** - Show pump assemblies properly in customer quotes
   - Update `_pdf_base.html` template to display assemblies
   - Show plant reference (CHWP-01) as header
   - Show pump model below plant reference
   - List all components with individual pricing
   - Add assembly subtotal line

### 📋 NEXT PRIORITIES (Following Week)

10. **❌ Admin Interface for Component Descriptions** - Create management page
    - Route: `/admin/pump-descriptions/`
    - Manage how components display on quotes
    - Edit description templates
    - Configure display options (show/hide pricing, part numbers, etc.)

11. **❌ Build Confidence Calculator** - Complete confidence scoring integration
    - API endpoints exist but not fully connected
    - Need to track selections in `pump_selection_history`
    - Calculate confidence scores on search
    - Display star ratings in results

12. **❌ Test Integration** - Full end-to-end testing
    - Test adding pumps to quotes
    - Test PDF generation with assemblies
    - Test plant reference auto-numbering
    - Test all component configurations

### 🔮 FUTURE ENHANCEMENTS

13. **Gather Historical Data** - Import past pump selections if available
14. **Confirm Duty Point Tolerance** - Verify ±5% tolerance in production
15. **Full Data Import** - Complete all BOM data import and validation
16. **Performance Optimization** - Add caching, indexes, query optimization
17. **User Documentation** - Create training materials and guides

## 17. Technical Considerations

### Performance Optimization:
- **Indexes**: Add indexes on flow_rate, head_pressure, series_id, poles
- **Caching**: Cache confidence scores (recalculate daily/weekly)
- **Query Optimization**: Use database joins efficiently
- **Pagination**: Limit results to top 20 matches initially

### Data Quality:
- **Validation**: Ensure pump performance specs are accurate
- **Tolerance Testing**: Verify ±5% tolerance works for all series
- **Historical Data**: Clean and validate legacy selection data
- **Continuous Improvement**: Regular reviews of confidence accuracy

### Future Enhancements:
- **Pump Curve Integration**: Display actual pump curves
- **Energy Efficiency Scoring**: Add energy consumption calculations
- **Cost Optimization**: Suggest most cost-effective pumps
- **AI/ML Integration**: Advanced prediction models
- **Mobile Support**: Optimize for tablet/phone use in field

---

## 18. Current Implementation Status Summary

### ✅ What's Working NOW (As of October 2025)

1. **Complete Database Schema** - All 13 pump-related tables created and migrated
2. **3-Way Pump Selection** - Duty point search, manual search, and browse all working
3. **Configuration Modal** - Full component selection with:
   - Mounting options (Inertia Base / Base Only / Crossbar / None)
   - Spring types (Standard Seismic / 50mm Static / None)
   - Rubber mounts with quantity control
   - Motor protection and drip tray options
   - IP rating selection (Standard / IP-56 / IP-66)
   - Dynamic pricing calculations with margin control
   - NBG/NK specific logic (no rubber mounts, base included)
4. **BOM Integration** - Components auto-load from database based on pump selection
5. **Pump Curve Links** - Automatic Grundfos website links for all pumps

### 🚧 What's IN PROGRESS

1. **Plant Reference System** (This Week's Task)
   - Design complete: CHWP-01, HWP-02 style naming
   - Modal mockup approved by user
   - Ready to code HTML + JavaScript
   - Will support multiple identical assemblies (auto-increment)
   
2. **Quote Integration API**
   - JavaScript stub exists
   - Backend endpoint needs implementation
   - Line item creation logic ready

3. **PDF Quote Display**
   - Template structure exists
   - Need to add pump assembly formatting
   - Plant reference display designed

### ❌ What's PENDING

1. **Admin Interface** for component descriptions
2. **Confidence Score** full integration
3. **Historical Data** import and tracking
4. **End-to-End Testing** with real quotes
5. **User Documentation** and training

### 🎯 Current Focus: Plant Reference Integration

**User Requirements (Confirmed Oct 2025):**
- Using **Grundfos pumps exclusively**
- Plant reference naming: **CHWP-01, HWP-01, CWP-01** (not PUMP-ASSY-XXX default)
- Customer-facing quote should show:
  ```
  CHWP-01: PUMP ASSEMBLY
  Grundfos TPE 50-120/4
  Complete assembly with mounting
  
  Components listed with individual pricing:
    • Pump: Grundfos TPE 50-120/4 - $6,200.00
    • Inertia Base: Type IB-4 - $1,200.00
    • Seismic Spring Set (4) - $400.00
    • Crossbar Assembly (2) - $350.00
    • Motor Protection IP56 - $350.00
  
  CHWP-01 Assembly Subtotal: $8,500.00
  ```

**Implementation Plan:**
1. Add plant reference card to configuration modal (after line 253)
2. Add JavaScript for real-time preview
3. Create backend endpoint to save assemblies
4. Update PDF template to display assemblies with plant references
5. Create admin route for managing component descriptions

---

*Last Updated: October 8, 2025 - This comprehensive plan provides a foundation for an intelligent pump selection system that learns from historical data and helps users make confident, informed decisions based on duty point requirements.*
