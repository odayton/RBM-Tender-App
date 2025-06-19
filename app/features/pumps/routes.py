from flask import render_template, request, redirect, url_for, flash, jsonify

# Import the blueprint object and forms from the local package
from . import pumps_bp
from .forms import PumpSearchForm, TechDataUploadForm, PumpManualUpdateForm

# Import the new manager to handle database logic
from app.managers.pump_manager import PumpManager
from app.core.core_errors import ValidationError


@pumps_bp.route('/pumps')
def index():
    """Renders the main pumps landing page which contains the search form."""
    form = PumpSearchForm()
    return render_template('pumps/pumps.html', form=form)


@pumps_bp.route('/pumps/search', methods=['GET', 'POST'])
def search_pumps():
    """Handles the pump search form and displays results."""
    form = PumpSearchForm()
    pumps = []
    if form.validate_on_submit():
        try:
            # Use the manager to find pumps matching the criteria
            pumps = PumpManager.search_pumps(
                flow_rate=form.flow_rate.data,
                head=form.head.data
            )
            if not pumps:
                flash('No pumps found matching the specified criteria.', 'info')
        except ValidationError as e:
            flash(str(e), 'danger')
    
    # Renders the search page, including the list of found pumps
    return render_template('pumps/search_pumps.html', form=form, pumps=pumps)


@pumps_bp.route('/pumps/tech-data/upload', methods=['GET', 'POST'])
def upload_tech_data():
    """Handles the form for uploading pump technical data sheets."""
    form = TechDataUploadForm()
    if form.validate_on_submit():
        try:
            # In a real implementation, you would get the file from the form:
            # file = form.file.data
            # And process it using a helper/manager class.
            flash('Technical data uploaded successfully (logic to be implemented).', 'success')
            return redirect(url_for('pumps.index'))
        except ValidationError as e:
            flash(str(e), 'danger')
    
    return render_template('pumps/tech_data_upload.html', form=form)


@pumps_bp.route('/pumps/historic')
def view_historic_pumps():
    """Displays a list of all pumps that have been used in past assemblies."""
    # Use the manager to get the list of historic pumps
    historic_pumps = PumpManager.get_historic_pumps()
    return render_template('pumps/view_historic_pumps.html', pumps=historic_pumps)


@pumps_bp.route('/pumps/<int:pump_id>')
def view_pump(pump_id):
    """Displays a detailed page for a single pump."""
    # Use the manager to get a specific pump by its ID
    pump = PumpManager.get_pump_by_id(pump_id)
    if not pump:
        flash('Pump not found.', 'danger')
        return redirect(url_for('pumps.index'))
        
    return render_template('pumps/view_pump.html', pump=pump)


@pumps_bp.route('/pumps/<int:pump_id>/tech-data')
def view_pump_tech_data(pump_id):
    """Displays the technical data associated with a specific pump."""
    pump = PumpManager.get_pump_by_id(pump_id)
    if not pump:
        flash('Pump not found.', 'danger')
        return redirect(url_for('pumps.index'))
        
    return render_template('pumps/view_tech_data.html', pump=pump)


@pumps_bp.route('/pumps/manual-update', methods=['GET', 'POST'])
def manual_update():
    """Allows for manually updating pump information via a form."""
    form = PumpManualUpdateForm()
    if form.validate_on_submit():
        try:
            # Note: Using SKU from the form to find the pump to update
            pump_to_update = PumpManager.get_pump_by_id(form.sku.data) 
            if pump_to_update:
                # Use the manager to update the pump with form data
                PumpManager.update_pump(pump_to_update, form.data)
                flash('Pump updated successfully.', 'success')
                return redirect(url_for('pumps.view_pump', pump_id=pump_to_update.id))
            else:
                flash('Pump with specified SKU not found.', 'danger')
        except ValidationError as e:
            flash(str(e), 'danger')
            
    return render_template('pumps/manual_update.html', form=form)


@pumps_bp.route('/api/pumps/search', methods=['POST'])
def api_search_pumps():
    """
    API endpoint for an AJAX pump search, expecting JSON.
    Returns pump data in JSON format.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON payload.'}), 400

        flow_rate = data.get('flow_rate')
        head = data.get('head')
        
        if not flow_rate or not head:
            raise ValidationError("Flow rate and head are required parameters.")
        
        # Use the manager to perform the search
        pumps = PumpManager.search_pumps(float(flow_rate), float(head))
        
        # Serialize the pump objects into dictionaries for the JSON response
        return jsonify([pump.to_dict() for pump in pumps])
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        # Log the full error for debugging
        # logger.error(f"API Pump Search Error: {e}") 
        return jsonify({'error': 'An internal server error occurred.'}), 500


@pumps_bp.route('/api/pumps/<int:pump_id>', methods=['GET'])
def api_get_pump(pump_id):
    """API endpoint to get details for a single pump."""
    try:
        pump = PumpManager.get_pump_by_id(pump_id)
        if pump:
            return jsonify(pump.to_dict())
        else:
            return jsonify({'error': 'Pump not found.'}), 404
    except Exception as e:
        # logger.error(f"API Get Pump Error: {e}")
        return jsonify({'error': 'An internal server error occurred.'}), 500