import logging
import os
import tempfile
import zipfile
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify
from werkzeug.utils import secure_filename
from app.utils.extract_pdf import extract_blank_nbg_tech_data, extract_historic_nbg_tech_data
from app.utils.db_utils.db_connection import insert_into_db, get_db_connection, record_exists
from app.utils.db_utils.db_pumps import fetch_all_general_pumps, fetch_historic_pump_data
from app.utils.view_utils import fetch_historic_with_general
from app.blueprints.forms import ManualUpdateForm, BlankTechDataUploadForm, HistoricTechDataUploadForm, SearchPumpsForm, CSRFForm

# Set up logging
logging.basicConfig(filename='pump_upload.log', level=logging.DEBUG)

pumps_bp = Blueprint('pumps', __name__)

@pumps_bp.route('/pumps', methods=['GET'])
def pumps():
    return render_template('pumps/pumps.html')

@pumps_bp.route('/pumps/add-pump', methods=['GET', 'POST'])
def add_pump_page():
    form = BlankTechDataUploadForm()
    if form.validate_on_submit():
        file = form.file.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            extracted_text, extracted_images = process_and_store_pdf(file_path, extract_blank_nbg_tech_data, "extracted_blank_graphs")
            insert_into_db('GeneralPumpDetails', extracted_text)
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
    deal_id = request.args.get('deal_id')

    if form.validate_on_submit():
        flow = form.flow.data
        head = form.head.data
        head_unit = form.head_unit.data
        poles = form.poles.data
        model_type = form.model_type.data

        query = """
            SELECT h.*, g.poles, g.kw
            FROM HistoricPumpData h
            LEFT JOIN GeneralPumpDetails g ON h.sku = g.sku
            WHERE 1=1
        """
        params = []

        if flow is not None:
            flow_min, flow_max = flow * 0.95, flow * 1.05
            query += " AND h.flow BETWEEN ? AND ?"
            params.extend([flow_min, flow_max])
        if head is not None:
            head_min, head_max = head * 0.95, head * 1.05
            query += " AND h.head BETWEEN ? AND ?"
            params.extend([head_min, head_max])
        if head_unit:
            query += " AND LOWER(h.head_unit) = LOWER(?)"
            params.append(head_unit)
        if poles:
            query += " AND g.poles = ?"
            params.append(poles)
        if model_type:
            query += " AND h.model_type = ?"
            params.append(model_type)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()
        conn.close()

        results = [dict(row) for row in results]

    return render_template('pumps/search_pumps.html', form=form, results=results, deal_id=deal_id)

@pumps_bp.route('/pumps/tech-data-upload', methods=['GET', 'POST'])
def tech_data_upload():
    form = HistoricTechDataUploadForm()
    if form.validate_on_submit():
        files = request.files.getlist('file')
        zip_file = request.files.get('zip_file')

        if not files and not zip_file:
            form.file.errors.append('At least one file or ZIP archive is required.')
        else:
            processed_files = set()

            if files:
                for file in files:
                    if file and allowed_file(file.filename):
                        process_single_file(file, processed_files)

            if zip_file and allowed_zip_file(zip_file.filename):
                process_zip_file(zip_file, processed_files)

            flash(f'Processed {len(processed_files)} files.')
            return redirect(url_for('pumps.tech_data_upload'))

    return render_template('pumps/tech_data_upload.html', form=form)

@pumps_bp.route('/pumps/view-historic-pumps', methods=['GET', 'POST'])
def view_historic_pumps():
    form = CSRFForm()
    data = fetch_historic_with_general()
    return render_template('pumps/view_historic_pumps.html', form=form, data=data)

@pumps_bp.route('/pumps/remove-historic-pump/<sku>', methods=['POST'])
def remove_historic_pump(sku):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM HistoricPumpData WHERE sku = ?", (sku,))
    conn.commit()
    conn.close()

    flash('Historic pump removed successfully.')
    return redirect(url_for('pumps.view_historic_pumps'))

@pumps_bp.route('/pumps/add-historic-pump/<sku>', methods=['GET'])
def add_historic_pump(sku):
    # Implement the logic to add the historic pump
    flash('Historic pump added successfully.')
    return redirect(url_for('pumps.view_historic_pumps'))

@pumps_bp.route('/pumps/get-table-data/<table_name>')
def get_table_data(table_name):
    if table_name == "GeneralPumpDetails":
        data = fetch_all_general_pumps()
    elif table_name == "HistoricPumpData":
        data = fetch_historic_pump_data()
    else:
        data = []

    return jsonify(data)

def process_single_file(file, processed_files):
    filename = secure_filename(file.filename)
    if filename in processed_files:
        logging.info(f"Skipping already processed file: {filename}")
        return

    temp_path = os.path.join(tempfile.gettempdir(), filename)
    file.save(temp_path)

    extracted_text, _ = process_and_store_pdf(
        temp_path, extract_historic_nbg_tech_data, "extracted_historic_graphs", is_historic=True
    )

    if extracted_text:
        logging.info(f"Extracted data from {filename}: {extracted_text}")
        insert_if_not_exists(extracted_text)
        processed_files.add(filename)

def process_zip_file(zip_file, processed_files):
    zip_filename = secure_filename(zip_file.filename)
    temp_path = os.path.join(tempfile.gettempdir(), zip_filename)
    zip_file.save(temp_path)

    with zipfile.ZipFile(temp_path, 'r') as zip_ref:
        for file_info in zip_ref.infolist():
            if allowed_file(file_info.filename):
                extracted_filename = secure_filename(file_info.filename)
                if extracted_filename in processed_files:
                    logging.info(f"Skipping already processed file from ZIP: {extracted_filename}")
                    continue

                with zip_ref.open(file_info) as file:
                    temp_file_path = os.path.join(tempfile.gettempdir(), extracted_filename)
                    with open(temp_file_path, 'wb') as temp_file:
                        temp_file.write(file.read())

                    extracted_text, _ = process_and_store_pdf(
                        temp_file_path, extract_historic_nbg_tech_data, "extracted_historic_graphs", is_historic=True
                    )

                    if extracted_text:
                        logging.info(f"Extracted data from ZIP file {extracted_filename}: {extracted_text}")
                        insert_if_not_exists(extracted_text)
                        processed_files.add(extracted_filename)

def insert_if_not_exists(extracted_text):
    conditions = {
        'sku': extracted_text['sku'],
        'flow': extracted_text['flow'],
        'head': extracted_text['head']
    }
    logging.info(f"Checking if record exists: {conditions}")
    if not record_exists('HistoricPumpData', conditions):
        logging.info(f"Inserting new record: {extracted_text}")
        insert_into_db('HistoricPumpData', extracted_text)
    else:
        logging.info(f"Record already exists, skipping insertion: {extracted_text}")

def process_and_store_pdf(pdf_path, extraction_function, output_folder, is_historic=False):
    try:
        extracted_text, extracted_images = extraction_function(pdf_path, image_output_folder=output_folder)
        return extracted_text, extracted_images
    except Exception as e:
        logging.error(f"Error processing PDF {pdf_path}: {e}")
        return None, None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf'}

def allowed_zip_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'zip'