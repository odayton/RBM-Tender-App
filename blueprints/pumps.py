# blueprints/pumps.py

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
import os
import tempfile
import shutil
from extract_pdf import extract_pdf_info
from utils.db_utils import fetch_all_from_table, insert_into_db, update_db_from_excel, write_to_db, get_db_connection
from blueprints.forms import SearchPumpsForm, ManualUpdateForm

pumps_bp = Blueprint('pumps', __name__)

@pumps_bp.route('/')
def pumps():
    return render_template('pumps.html')

@pumps_bp.route('/add')
def add_pump_page():
    return render_template('add_pump.html')

@pumps_bp.route('/view')
def view_pumps_page():
    tables = [
        'Pump_Details',
        'Large_Seismic_Springs',
        'Additional_Price_Adders',
        'Small_Seismic_Springs',
        'Inertia_Bases'
    ]
    return render_template('view_pumps.html', tables=tables)

@pumps_bp.route('/get_table_data/<table_name>', methods=['GET'])
def get_table_data(table_name):
    data = fetch_all_from_table(table_name)
    return jsonify(data)

@pumps_bp.route('/manual-update', methods=['GET', 'POST'])
def manual_update():
    form = ManualUpdateForm()
    if form.validate_on_submit():
        if form.file.data:
            filename = secure_filename(form.file.data.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            form.file.data.save(filepath)
            update_db_from_excel(filepath)
            flash('Database updated successfully from Excel file')
            return redirect(url_for('pumps.manual_update'))

        else:
            table = form.table.data
            data = {
                'Large_Seismic_Springs': {
                    'Part_Number': form.part_number.data,
                    'Name': form.name.data,
                    'Max_Load_kg': form.max_load_kg.data,
                    'Static_Deflection': form.static_deflection.data,
                    'Spring_Constant_kg_mm': form.spring_constant_kg_mm.data,
                    'Inner': form.inner.data,
                    'Outer': form.outer.data,
                    'Cost': form.cost.data
                },
                'Additional_Price_Adders': {
                    'IP_Adder': form.ip_adder.data,
                    'Drip_Tray_Adder': form.drip_tray_adder.data
                },
                'Small_Seismic_Springs': {
                    'Part_Number': form.part_number.data,
                    'Name': form.name.data,
                    'Max_Load_kg': form.max_load_kg.data,
                    'Static_Deflection': form.static_deflection.data,
                    'Spring_Constant_kg_mm': form.spring_constant_kg_mm.data,
                    'Stripe_1': form.inner.data,  # Adjust as needed
                    'Stripe_2': form.outer.data,  # Adjust as needed
                    'Cost': form.cost.data
                },
                'Inertia_Bases': {
                    'Part_Number': form.part_number.data,
                    'Name': form.name.data,
                    'Length': form.length.data,
                    'Width': form.width.data,
                    'Height': form.height.data,
                    'Spring_Mount_Height': form.spring_mount_height.data,
                    'Spring_Type': form.spring_type.data,
                    'Weight': form.weight.data,
                    'Spring_Qty': form.spring_qty.data,
                    'Spring_Load': form.spring_load.data,
                    'Cost': form.cost.data
                }
            }.get(table)

            if data:
                insert_into_db(table, data)

            flash('Record added successfully')
            return redirect(url_for('pumps.manual_update'))
    return render_template('manual_update.html', form=form)

@pumps_bp.route('/tech-data-upload', methods=['GET', 'POST'])
def tech_data_upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            try:
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_filepath = os.path.join(temp_dir, secure_filename(file.filename))
                    file.save(temp_filepath)

                    pdf_info = extract_pdf_info(temp_filepath)
                    unique_filename = f"{pdf_info['sku']}_{pdf_info['flow_l_s']}_{pdf_info['head_kpa']}.pdf"
                    write_to_db(pdf_info)

                    final_path = os.path.join(current_app.config['TECH_DATA_FOLDER'], unique_filename)
                    shutil.move(temp_filepath, final_path)

                flash('Technical data uploaded successfully')
                return redirect(url_for('pumps.tech_data_upload'))
            except Exception as e:
                flash(f"An error occurred: {e}")
                return redirect(request.url)
    return render_template('tech_data_upload.html')

@pumps_bp.route('/search', methods=['GET', 'POST'])
def search_pumps():
    form = SearchPumpsForm()
    results = []
    if form.validate_on_submit():
        flow = form.flow.data
        head = form.head.data
        head_unit = form.head_unit.data
        poles = form.poles.data
        model_type = form.model_type.data

        query = "SELECT * FROM Pump_Details WHERE 1=1"
        params = []

        if flow:
            flow_min = flow * 0.95
            flow_max = flow * 1.05
            query += " AND Flow_L_s BETWEEN ? AND ?"
            params.extend([flow_min, flow_max])

        if head:
            if head_unit == 'kpa':
                head_min = head * 0.95
                head_max = head * 1.05
                query += " AND Head_kPa BETWEEN ? AND ?"
                params.extend([head_min, head_max])
            elif head_unit == 'm':
                head_min = head * 0.95
                head_max = head * 1.05
                query += " AND Head_m BETWEEN ? AND ?"
                params.extend([head_min, head_max])

        if poles:
            query += " AND Poles = ?"
            params.append(poles)

        if model_type:
            query += " AND Name LIKE ?"
            params.append(f"%{model_type}%")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in rows]
        conn.close()

    return render_template('search_pumps.html', form=form, results=results)

@pumps_bp.route('/add_to_quote', methods=['POST'])
def add_to_quote():
    data = request.get_json()
    sku = data.get('sku')
    name = data.get('name')
    flow = data.get('flow')
    head = data.get('head')
    cost = data.get('cost')
    # Perform logic to add the pump to the quote
    # This is a placeholder, implement the actual logic as needed
    return jsonify({'status': 'success'})
