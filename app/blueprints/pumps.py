import os
import tempfile
import zipfile
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify
from werkzeug.utils import secure_filename
from app.utils.extract_pdf import extract_historic_nbg_tech_data
from app.utils.db_utils import fetch_all_from_table, insert_into_db
from app.utils.view_utils import fetch_historic_with_general
from app.blueprints.forms import ManualUpdateForm, BlankTechDataUploadForm, HistoricTechDataUploadForm, SearchPumpsForm

pumps_bp = Blueprint('pumps', __name__)

@pumps_bp.route('/pumps/pumps')
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
    form = HistoricTechDataUploadForm()
    if form.validate_on_submit():
        files = request.files.getlist('file')
        zip_file = request.files.get('zip_file')

        if not files and not zip_file:
            form.file.errors.append('At least one file or ZIP archive is required.')
        else:
            all_extracted_data = []

            if files:
                for file in files:
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        temp_path = os.path.join(tempfile.gettempdir(), filename)
                        file.save(temp_path)
                        extracted_text, extracted_images = process_and_store_pdf(temp_path, extract_historic_nbg_tech_data, "extracted_historic_graphs", is_historic=True)
                        all_extracted_data.append((extracted_text, extracted_images))
                        print(f"Extracted Text: {extracted_text}")
                        insert_into_db('HistoricPumpDetails', extracted_text)  # Insert into HistoricPumpDetails
                        for img_path in extracted_images:
                            print(f"Saved Image: {img_path}")

            if zip_file and allowed_zip_file(zip_file.filename):
                zip_filename = secure_filename(zip_file.filename)
                temp_path = os.path.join(tempfile.gettempdir(), zip_filename)
                zip_file.save(temp_path)
                print(f"ZIP file saved to: {temp_path}")
                extracted_data = extract_and_process_zip(temp_path, extract_historic_nbg_tech_data, "extracted_historic_graphs", is_historic=True)
                all_extracted_data.extend(extracted_data)

            for text, images in all_extracted_data:
                print(f"Extracted Text: {text}")
                insert_into_db('HistoricPumpDetails', text)  # Insert into HistoricPumpDetails
                for img_path in images:
                    print(f"Saved Image: {img_path}")

            flash('Historic tech data uploaded successfully.')
            return redirect(url_for('pumps.tech_data_upload'))
    return render_template('pumps/tech_data_upload.html', form=form)

@pumps_bp.route('/pumps/view-historic-pumps')
def view_historic_pumps():
    data = fetch_historic_with_general()
    return render_template('pumps/view_historic_pumps.html', data=data)

@pumps_bp.route('/pumps/get-table-data/<table_name>')
def get_table_data(table_name):
    data = fetch_all_from_table(table_name)
    return jsonify(data)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf'}

def allowed_zip_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'zip'

def process_and_store_pdf(pdf_path, extraction_function, output_folder, is_historic=False):
    try:
        extracted_text, extracted_images = extraction_function(pdf_path, image_output_folder=output_folder)
        print(f"Extracted Text from {pdf_path}:\n{extracted_text}")
        return extracted_text, extracted_images
    except Exception as e:
        print(f"Error processing PDF {pdf_path}: {e}")
        return None, None

def extract_and_process_zip(zip_path, extraction_function, output_folder, is_historic=False):
    extracted_data = []
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Extracting ZIP file to temporary directory: {temp_dir}")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
            print(f"ZIP file extracted to: {temp_dir}")
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    print(f"Found file in ZIP: {file}")
                    if allowed_file(file):
                        file_path = os.path.join(root, file)
                        print(f"Processing extracted file: {file_path}")
                        text, images = process_and_store_pdf(file_path, extraction_function, output_folder, is_historic)
                        if text is not None and images is not None:
                            extracted_data.append((text, images))
                            print(f"Extracted Text from {file_path}: {text}")
                            for img_path in images:
                                print(f"Saved Image: {img_path}")
                        else:
                            print(f"Failed to extract data from {file_path}")
    return extracted_data
