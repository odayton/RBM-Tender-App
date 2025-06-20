from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from app.models import Pump
from .forms import PumpForm, PumpSearchForm
from app.core.core_logging import logger

# Import the correct blueprint from this feature's __init__.py
from . import pumps_bp

# Correct the import path for the manager class and use an alias
from app.utils.db_utils.pump.db_pumps import PumpDatabaseManager as PumpManager

@pumps_bp.route('/', methods=['GET', 'POST'])
#@login_required
def pumps_list():
    """Display a list of all pumps."""
    search_form = PumpSearchForm()
    pumps = Pump.query.order_by(Pump.part_number).all() # Use ORM
    
    if search_form.validate_on_submit():
        search_term = search_form.search.data
        pumps = Pump.query.filter(Pump.part_number.ilike(f'%{search_term}%')).all()
    
    return render_template('pumps/pumps.html', pumps=pumps, search_form=search_form)

@pumps_bp.route('/add', methods=['GET', 'POST'])
#@login_required
def add_pump():
    """Add a new pump to the database."""
    form = PumpForm()
    if form.validate_on_submit():
        try:
            new_pump = Pump()
            form.populate_obj(new_pump)
            new_pump.save()
            flash('Pump added successfully!', 'success')
            return redirect(url_for('pumps.pumps_list'))
        except Exception as e:
            logger.error(f"Error adding pump: {e}")
            flash('An error occurred while adding the pump.', 'error')
            
    return render_template('pumps/add_pump.html', form=form)

@pumps_bp.route('/<int:pump_id>/edit', methods=['GET', 'POST'])
#@login_required
def edit_pump(pump_id):
    """Edit an existing pump."""
    pump = Pump.query.get_or_404(pump_id)
    form = PumpForm(obj=pump)
    
    if form.validate_on_submit():
        try:
            form.populate_obj(pump)
            pump.save()
            flash('Pump updated successfully!', 'success')
            return redirect(url_for('pumps.pumps_list'))
        except Exception as e:
            logger.error(f"Error updating pump {pump_id}: {e}")
            flash('An error occurred while updating the pump.', 'error')
            
    return render_template('pumps/edit_pump.html', form=form, pump=pump)

@pumps_bp.route('/<int:pump_id>/delete', methods=['POST'])
#@login_required
def delete_pump(pump_id):
    """Delete a pump."""
    pump = Pump.query.get_or_404(pump_id)
    try:
        pump.delete()
        flash('Pump deleted successfully!', 'success')
    except Exception as e:
        logger.error(f"Error deleting pump {pump_id}: {e}")
        flash('An error occurred while deleting the pump.', 'error')
        
    return redirect(url_for('pumps.pumps_list'))