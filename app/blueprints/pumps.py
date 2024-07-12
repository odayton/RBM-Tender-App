import os
import logging
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from app.utils.extract_pdf import extract_blank_nbg_tech_data, extract_historic_nbg_tech_data
from app.utils.db_utils import fetch_all_from_table, write_to_db, insert_into_db, update_db_from_excel
from app.blueprints.forms import ManualUpdateForm, TechDataUploadForm, SearchPumpsForm

pumps_bp = Blueprint('pumps', __name__)

@pumps_bp.route('/pumps/view-pumps')
def view_pumps_page():
    data = fetch_all_from_table('GeneralPumpDetails')
    return render_template('pumps/view_pumps.html', data=data)

@pumps_bp.route('/pumps/add-pump', methods=['GET', 'POST'])
def add_pump_page():
    form = TechDataUploadForm()
    if form.validate_on_submit():
        file = form.file.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            if 'historical' in filename.lower():
                extract_historic_nbg_tech_data(file_path)
            else:
                extract_blank_nbg_tech_data(file_path)
            flash('File uploaded and processed successfully.')
            return redirect(url_for('pumps.add_pump_page'))
    return render_template('pumps/add_pump.html', form=form)

@pumps_bp.route('/pumps/manual-update', methods=['GET', 'POST'])
def manual_update_page():
    form = ManualUpdateForm()
    if form.validate_on_submit():
        data = {
            'PartNumber': form.part_number.data,
            'Name': form.name.data,
            'MaxLoad_kg': form.max_load_kg.data,
            'StaticDeflection': form.static_deflection.data,
            'SpringConstant_kg_mm': form.spring_constant_kg_mm.data,
            'Inner': form.inner.data,
            'Outer': form.outer.data,
            'Cost': form.cost.data,
            'IP_Adder': form.ip_adder.data,
            'DripTray_Adder': form.drip_tray_adder.data,
            'Length': form.length.data,
            'Width': form.width.data,
            'Height': form.height.data,
            'SpringMountHeight': form.spring_mount_height.data,
            'SpringType': form.spring_type.data,
            'Weight': form.weight.data,
            'SpringQty': form.spring_qty.data,
            'SpringLoad': form.spring_load.data
        }
        insert_into_db(form.table.data, data)
        flash('Data updated successfully.')
        return redirect(url_for('pumps.manual_update_page'))
    return render_template('pumps/manual_update.html', form=form)

@pumps_bp.route('/pumps/search-pumps', methods=['GET', 'POST'])
def search_pumps():
    form = SearchPumpsForm()
    results = []
    if form.validate_on_submit():
        # Implement search logic here
        pass
    return render_template('pumps/search_pumps.html', form=form, results=results)

@pumps_bp.route('/pumps/tech-data-upload', methods=['GET', 'POST'])
def tech_data_upload():
    form = TechDataUploadForm()
    if form.validate_on_submit():
        file = form.file.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            extract_blank_nbg_tech_data(file_path)
            flash('File uploaded and processed successfully.')
            return redirect(url_for('pumps.tech_data_upload'))
    return render_template('pumps/tech_data_upload.html', form=form)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf'}
