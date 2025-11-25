# Hydronic Heating System - Implementation TODO

## Overview
Complete hydronic heating system for RBM Tender App including:
- Underfloor heating board calculator
- Pipe & manifold system designer
- Quote sections infrastructure
- Auto-accessory dependencies

---

## Phase 0: Quote Sections Infrastructure (Foundation)

### Database & Models
- [ ] Create database migration for `QuoteSections` table
  - Fields: name, description, display_order, show_subtotal
  - Relationships to QuoteOption with cascade delete
  
- [ ] Update `QuoteLineItem` model (SINGLE TABLE FOR ALL TYPES)
  - Add `section_id` foreign key to link items to sections
  - Add `unit_of_measure` field (MT, MQ, NR, EA, KG, L, etc.)
  - Add `line_item_type` field (standard, pump_assembly, hydronic_board, hydronic_system, custom)
  - Keep existing `assembly_metadata` JSON field (used for ALL types now, not just pumps)
  - **Note:** We are NOT creating separate tables for different item types
  - **Note:** This extends the proven pump assembly pattern to all product types
  
- [ ] Update `QuoteOption` model
  - Add `sections` relationship with proper ordering
  
- [ ] Create `ProductDependency` table for auto-accessories
  - Fields: parent_product_id, dependent_product_id
  - Calculation rules: per_unit, per_circuit, per_meter, per_m2, fixed_qty
  - Multiplier, minimum_qty, is_optional, auto_add flags

### Backend Routes
- [ ] Add section management routes in deals blueprint
  - Add new section
  - Update section name/description
  - Delete section (with item handling options)
  - Reorder sections (drag & drop support)
  
- [ ] Update line item routes
  - Add section selector to add/edit forms
  - Move items between sections

### Frontend UI
- [ ] Update deal details template
  - Display sections with collapsible UI
  - Show subtotals per section
  - Section management buttons (add, edit, delete)
  - Drag-and-drop reordering
  
- [ ] Add section selector to line item forms
  - Dropdown with existing sections
  - "Create new section" option
  
- [ ] Update PDF generation
  - Render sections with subtotals
  - Match customer quote format from example
  - "All prices excluding GST" footer per section

### Compatibility
- [ ] Implement backward compatibility
  - Handle existing quotes without sections
  - "Organize into sections" migration tool
  - Default section assignment

**Technologies:** PostgreSQL, SQLAlchemy, Flask, Jinja2, Alembic migrations

---

## Phase 1: Underfloor Heating Board Calculator

### Database & Models
- [ ] Create `UnderfloorHeatingProduct` table
  - Product identification: product_name, thickness_mm, part_number
  - Packing specs: waste_safety_percent, pack_m2, sheets_per_pack, packs_per_pallet
  - Weights: pack_weight, sheet_weight, pallet_weight, skid_weight
  - Dimensions: pack and pallet dimensions (length, width, height)
  - Pricing: list_price, nett_price, freight_adder_per_sheet
  - Link to main Products table

### Calculator Logic
- [ ] Build `BoardCalculator` helper class
  - `calculate_from_m2()` method with safety factor application
  - `calculate_from_sheets()` method for direct sheet input
  - Sheet/pack/pallet rounding logic
  - Freight calculation (placeholder for future API)
  - Total cost calculations

### Auto-Accessories
- [ ] Implement auto-accessory logic for boards
  - Edging tape based on perimeter
  - Adhesive based on area
  - Use ProductDependency table for rules

### Routes & API
- [ ] Create board calculator routes
  - Main calculator page at `/hvac/underfloor-heating/boards`
  - Calculate API endpoint (POST) for real-time calculations
  - Add-to-quote API endpoint with section assignment
  - Store calculation in `assembly_metadata` when adding to quote
  - Set `line_item_type` = 'hydronic_board'

### Frontend UI
- [ ] Build calculator interface
  - Product selector (Super-Strong, Klima-Futura, thickness variants)
  - Dual input mode toggle (m² or sheets)
  - Waste/safety factor adjustment
  - Real-time calculation display
  - Results table: sheets, packs, pallets, total m², costs
  - Add-to-quote modal with section selection

### Admin Interface
- [ ] Create admin pages for product management
  - View/edit underfloor heating products
  - Manage product dependencies
  - Bulk import from spreadsheet

### Data Import
- [ ] Import initial product data
  - Super-Strong 10mm with all specifications
  - Klima-Futura variants
  - Configure product dependencies for accessories

**Technologies:** Python, Flask routes, JavaScript for real-time calculations, Jinja2 templates

---

## Phase 2: Piping & Manifold System Designer

### Database & Models
- [ ] Create `HydronicSystemDesign` table
  - Project metadata: name, building_type, total_area_m2
  - System config: max_loop_length_m, default_pipe_spacing_mm
  - Floor plan data: file_path, scale
  - Design data: zones_data, manifolds_data, pipe_routing_data (JSON)
  - Calculated totals: total_pipe_length_m, total_manifolds, total_circuits
  - Link to user and deal
  
- [ ] Create `HydronicZone` table
  - Zone identification: zone_name, zone_number
  - Geometry: area_m2, perimeter_m, geometry_data (JSON)
  - Layout config: pipe_spacing_mm, layout_pattern (serpentine/spiral), floor_covering
  - Calculated values: pipe_length_m
  - Manifold assignment: manifold_id, circuit_number
  
- [ ] Create `HydronicManifold` table
  - Manifold details: manifold_number, location_name
  - Position: position_x, position_y (for floor plans)
  - Product specs: product_id, circuit_count (2-14 ways)
  
- [ ] Create `ManifoldProduct` catalog table
  - Specifications: circuit_count, manifold_type
  - Performance: max_flow_rate_lpm, max_pressure_bar
  - Features: has_flow_meters, has_actuators, has_drain_valves
  - Pricing and dimensions
  
- [ ] Create `PipeProduct` catalog table
  - Specifications: diameter_mm, material (PEX, PE-RT)
  - Ratings: max_temperature_c, max_pressure_bar
  - Packaging: coil_length_m
  - Pricing: price_per_meter

### Calculator Logic
- [ ] Build `HydronicSystemCalculator` helper class
  - `calculate_pipe_length_rectangular()` for standard rooms
  - Serpentine pattern calculation (back-and-forth)
  - Spiral pattern calculation (outside-to-center)
  - Manifold connection distance estimation
  
- [ ] Implement zone assignment algorithm
  - `assign_zones_to_manifolds()` with max loop length constraint
  - Automatic manifold count determination
  - Flag zones that exceed max length (need splitting)
  
- [ ] Build manifold selector
  - `select_manifold_size()` from available sizes (2, 3, 4...14 way)
  - Round up to next available size
  
- [ ] Create material list generator
  - `calculate_total_materials()` for complete BOM
  - Pipe quantities with waste factor
  - Manifold specifications
  - Fittings and accessories

### Auto-Accessories
- [ ] Implement auto-accessory logic for piping
  - Pipe fittings: circuits × 2 (flow + return)
  - Curve holders based on pipe length
  - Clips/holders based on spacing requirements
  - Use ProductDependency table

### Routes & API
- [ ] Create piping designer routes
  - Dashboard: `/hvac/hydronic-design` (list saved designs)
  - New design: `/hvac/hydronic-design/new`
  - Edit design: `/hvac/hydronic-design/<id>`
  - Save design API endpoint
  - Calculate API endpoint
  - Add-to-quote API endpoint
  - Store design reference in `assembly_metadata` when adding to quote
  - Set `line_item_type` = 'hydronic_system' for system items, 'standard' for individual components

### Frontend UI - Basic (Phase 2)
- [ ] Build room-by-room input form
  - Add room button with modal
  - Room fields: name, length, width
  - Pipe spacing selector (100mm, 150mm, 200mm)
  - Layout pattern selector (serpentine, spiral)
  - Floor covering type
  
- [ ] Create zone summary table
  - Display all zones with calculated pipe lengths
  - Show manifold assignments
  - Color-code by manifold
  - Edit/delete zone actions
  
- [ ] Build material summary panel
  - Total pipe length
  - Manifolds required (with sizes)
  - Fittings and accessories
  - Cost estimate
  - Export to quote button

**Technologies:** Python, Shapely (geometry calculations), Flask routes, JavaScript for dynamic forms, JSON storage

---

## Phase 3: Complete System Integration

### System Integration
- [ ] Create `CompleteSystemDesigner` class
  - Integrate BoardCalculator and PipingSystemDesigner
  - Auto-calculate board area from zone definitions
  - Combined material list generation
  - Total system cost calculation
  
- [ ] Build multi-section quote generation
  - Section 1: Radiant Heating (main components)
  - Section 2: Gluing Accessories and Radiant Primer
  - Section 3: Optional Accessories
  - Configurable section strategy (single vs multiple)

### Calculation Storage
- [ ] Create `SavedCalculation` table
  - Link calculations to designs and quotes
  - Store inputs and outputs as JSON
  - Track calculation type (boards, piping, complete_system)
  - Enable reuse and reference

### Complete System UI
- [ ] Build unified interface
  - Zone design section (from Phase 2)
  - Auto-populated board requirements
  - Board product selector
  - Complete system summary
  - Flexible add-to-quote options

### Testing & Validation
- [ ] End-to-end workflow testing
  - Board-only: 50 sheets request
  - Board-only: 100m² request
  - Piping-only: House design without boards
  - Complete system: Full underfloor heating
  - Multi-section quote generation
  - PDF export validation

**Technologies:** Python integration classes, Flask API endpoints, comprehensive testing

---

## Phase 4: Visual Designer (Advanced)

### Technology Selection
- [ ] Research and select canvas library
  - Options: Fabric.js or Konva.js
  - Evaluate performance, features, documentation
  - Create proof-of-concept

### Floor Plan Upload
- [ ] Implement PDF upload capability
  - Use PDF.js for rendering PDF as background
  - File upload handling and storage
  - Image format support (PNG, JPG)
  
- [ ] Build scale setting tool
  - Click two points to set known distance
  - Calculate pixels-per-meter ratio
  - Display current scale
  - Recalibration option

### Drawing Tools
- [ ] Create zone drawing tools
  - Rectangle tool (click-and-drag)
  - Polygon tool (click points, close shape)
  - Edit mode (move vertices, resize)
  - Auto-calculate area using Shapely
  - Label zones with names
  
- [ ] Implement manifold placement
  - Drag-and-drop manifold icons
  - Snap-to-grid functionality
  - Visual connection lines to zones
  - Auto-suggest optimal placement

### Pipe Visualization
- [ ] Build pipe pattern generators
  - Serpentine pattern: parallel runs with 180° bends
  - Spiral pattern: concentric loops
  - Render at correct spacing (100mm, 150mm, etc.)
  - Real-time updates on spacing changes
  
- [ ] Add color-coding system
  - Different colors per manifold
  - Highlight selected zone
  - Show circuit assignments
  - Legend/key display

### Export Capabilities
- [ ] Implement annotated plan export
  - Use ReportLab or WeasyPrint for PDF generation
  - Include floor plan with overlays
  - Add zone labels, dimensions, pipe lengths
  - Material list on separate page
  - Professional formatting

### Advanced Features (Future)
- [ ] Add CAD file import
  - DXF-Parser for AutoCAD files
  - Parse layers and dimensions
  - Convert to internal format
  
- [ ] Build auto-routing algorithms
  - Intelligent pipe path generation
  - Avoid obstacles/walls
  - Optimize manifold placement
  - H2X-inspired features

**Technologies:** 
- Frontend: Fabric.js or Konva.js (canvas), PDF.js (viewing)
- Backend: Pillow (image processing), Shapely (geometry), ReportLab/WeasyPrint (PDF export)
- Future: DXF-Parser (CAD import)

---

## Delivery Timeline Estimates

**Phase 0:** 1-2 weeks (Foundation - Critical)
**Phase 1:** 2-3 weeks (Board Calculator - Immediate value)
**Phase 2:** 3-4 weeks (Piping Designer - Complex logic)
**Phase 3:** 1-2 weeks (Integration - Combines existing)
**Phase 4:** 4-6 weeks (Visual Designer - Advanced features)

**Total MVP (Phases 0-3):** 7-11 weeks
**Complete System (All Phases):** 11-17 weeks

---

## Key Technologies Summary

### Backend
- **Framework:** Flask (Python)
- **Database:** PostgreSQL with SQLAlchemy ORM
- **Migrations:** Alembic
- **Geometry:** Shapely library
- **Image Processing:** Pillow (PIL)
- **PDF Generation:** ReportLab or WeasyPrint

### Frontend
- **Templates:** Jinja2
- **JavaScript:** Vanilla JS + optional libraries
- **Canvas Drawing:** Fabric.js or Konva.js
- **PDF Viewing:** PDF.js
- **File Processing:** DXF-Parser (future)

### Integrations
- **Existing Systems:** Pumps feature, Deals/Quotes system, Products catalog
- **Future:** Freight pricing API, CAD software integration

---

## Dependencies & Prerequisites

### Existing Systems
- Products table and model
- Deals, Quotes, QuoteOptions, QuoteLineItems models
- User authentication and permissions
- PDF quote generation infrastructure
- Admin interface framework

### New Requirements
- Quote sections infrastructure (Phase 0 - builds on existing)
- Product dependency system (Phase 0 - new concept)
- Canvas drawing capabilities (Phase 4)
- Advanced geometric calculations (Phases 2-4)

---

## Architecture Decisions

### Single QuoteLineItem Table (Unified Approach)

**Decision:** Use ONE `QuoteLineItem` table for all item types instead of separate tables.

**Rationale:**
- ✅ **Proven Pattern:** Pump assemblies already work well with this approach
- ✅ **Simple Queries:** All items in one table makes totaling and ordering straightforward
- ✅ **Flexible:** JSON `assembly_metadata` field handles any type-specific configuration
- ✅ **Backward Compatible:** Existing pump assemblies continue to work unchanged
- ✅ **Display Order:** Easy to maintain order across all item types
- ✅ **Sections:** All items can be organized into sections naturally

**Implementation:**
```
QuoteLineItem Fields:
  - line_item_type: 'standard', 'pump_assembly', 'hydronic_board', 'hydronic_system'
  - assembly_metadata: JSON (stores type-specific configurations)
  - section_id: Links to QuoteSection for organization
  - unit_of_measure: MT, MQ, NR, EA, etc.
```

**Metadata Examples:**

*Pump Assembly (existing):*
```json
{
  "type": "pump_assembly",
  "pump_id": 123,
  "margin_percentage": 18.5,
  "components": [...]
}
```

*Hydronic Board (new):*
```json
{
  "type": "hydronic_board",
  "product_name": "Super-Strong",
  "thickness_mm": 10,
  "requested_m2": 100,
  "actual_m2": 109.44,
  "calculation_details": {...}
}
```

*Hydronic System (new):*
```json
{
  "type": "hydronic_system",
  "design_id": 456,
  "zones": [...],
  "manifolds": [...],
  "total_pipe_length": 1200
}
```

### Quote Organization Example

```
Quote Option 1

  Section: Radiant Heating
    ├─ Pipe (type: standard)
    ├─ Panels (type: hydronic_board)
    ├─ Manifold Kit (type: standard)
    └─ Fittings (type: standard)
  Subtotal: $10,581.69

  Section: HVAC Equipment
    ├─ CHWP-01: Grundfos CR (type: pump_assembly)
    │   └─ Sub-items (nested using naming convention)
    └─ Actuators (type: standard)
  Subtotal: $8,425.10

Total: $19,006.79
```

---

## Notes

### Modular Architecture
Each calculator works independently:
- Board calculator can be used standalone
- Piping designer can be used standalone
- Complete system combines both when needed

### Customer Workflows
- "I need 50 sheets" → Board calculator only
- "I need boards for 100m²" → Board calculator only
- "Design piping for my house" → Piping designer only (already has boards)
- "Complete underfloor system" → Both calculators integrated

### Quote Flexibility
- Add as single line item
- Add as detailed breakdown
- Add as multi-section package
- Items remain independent (customer can remove boards but keep piping)

### Auto-Accessories
- Manifold → Auto-adds fittings (circuits × 2) and holders
- Boards → Auto-adds edging tape and adhesive
- Configurable via ProductDependency table
- Can be adjusted/removed before adding to quote

### Line Item Types Strategy
- **Standard Items:** Regular products from catalog
- **Pump Assemblies:** Header item with collapsible sub-items (existing pattern)
- **Hydronic Boards:** Board calculations stored in metadata, added as line items
- **Hydronic Systems:** Complete piping system with design reference
- **All types** can have auto-accessories via ProductDependency rules
- **All types** can be organized into sections
- **All types** use the same display_order system

### Template Rendering
- Continue using existing pattern: identify item type and render appropriately
- Pump assemblies: Header row with collapsible sub-items (using "  •" prefix)
- Hydronic items: Can follow same pattern if detailed breakdown needed
- Sections: Wrap groups of items with subtotals
- Single query fetches all items, simple to total and organize

---

## Future Enhancements (Beyond Phase 4)

- Heat load calculations integration
- Flow rate and balancing calculations
- Energy efficiency analysis
- 3D visualization of systems
- Mobile app for on-site measurements
- Real-time freight pricing API
- Supplier catalog integration
- Installation time estimation
- Labor cost calculation
- System optimization recommendations

---

---

## Database Schema Reference

### QuoteLineItem (Extended, Single Table)
```sql
CREATE TABLE quote_line_items (
    id SERIAL PRIMARY KEY,
    option_id INTEGER REFERENCES quote_options(id),
    section_id INTEGER REFERENCES quote_sections(id),  -- NEW
    product_id INTEGER REFERENCES products(id),
    
    -- Item type identifier -- NEW
    line_item_type VARCHAR(50) DEFAULT 'standard',
    -- Values: 'standard', 'pump_assembly', 'hydronic_board', 'hydronic_system', 'custom'
    
    -- Quantities and pricing
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_of_measure VARCHAR(20),  -- NEW: MT, MQ, NR, EA, etc.
    list_price NUMERIC(10,2),
    unit_price NUMERIC(10,2) NOT NULL,
    discount NUMERIC(5,2) DEFAULT 0,
    
    -- Display and organization
    display_order INTEGER DEFAULT 0,
    notes TEXT,
    
    -- Custom products (when product_id is null)
    custom_sku VARCHAR(80),
    custom_name VARCHAR(200),
    custom_description TEXT,
    
    -- Configuration storage (JSON) -- EXISTING, now used for ALL types
    assembly_metadata TEXT,
    
    -- Timestamps
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### QuoteSections (New Table)
```sql
CREATE TABLE quote_sections (
    id SERIAL PRIMARY KEY,
    option_id INTEGER REFERENCES quote_options(id),
    
    name VARCHAR(200) NOT NULL,
    description TEXT,
    display_order INTEGER DEFAULT 0,
    show_subtotal BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### ProductDependency (New Table)
```sql
CREATE TABLE product_dependencies (
    id SERIAL PRIMARY KEY,
    parent_product_id INTEGER REFERENCES products(id),
    dependent_product_id INTEGER REFERENCES products(id),
    
    calculation_type VARCHAR(50),
    -- Values: 'per_unit', 'per_circuit', 'per_meter', 'per_m2', 'fixed_qty'
    
    multiplier NUMERIC(10,4),
    minimum_qty INTEGER DEFAULT 1,
    is_optional BOOLEAN DEFAULT FALSE,
    auto_add BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

---

*Last Updated: October 2025*
*Project: RBM Tender App - Hydronic Heating Module*
*Architecture: Unified QuoteLineItem table with type discriminator*

