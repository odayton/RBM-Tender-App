import os
import tempfile
import zipfile
import pandas as pd
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from werkzeug.utils import secure_filename
from app.utils.extract_pdf import extract_blank_nbg_tech_data
from app.utils.db_utils import fetch_all_from_table, insert_into_db
from app.blueprints.forms import BlankTechDataUploadForm

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/admin/blank-tech-data-upload', methods=['GET', 'POST'])
def blank_tech_data_upload():
    form = BlankTechDataUploadForm()
    if request.method == 'POST':
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
                            extracted_text, extracted_images = process_and_store_pdf(temp_path, extract_blank_nbg_tech_data, "extracted_blank_graphs")
                            all_extracted_data.append((extracted_text, extracted_images))
                            print(f"Extracted Text: {extracted_text}")
                            insert_into_db('GeneralPumpDetails', extracted_text)  # Insert into GeneralPumpDetails
                            for img_path in extracted_images:
                                print(f"Saved Image: {img_path}")

                if zip_file and allowed_zip_file(zip_file.filename):
                    zip_filename = secure_filename(zip_file.filename)
                    temp_path = os.path.join(tempfile.gettempdir(), zip_filename)
                    zip_file.save(temp_path)
                    print(f"ZIP file saved to: {temp_path}")
                    extracted_data = extract_and_process_zip(temp_path, extract_blank_nbg_tech_data, "extracted_blank_graphs")
                    all_extracted_data.extend(extracted_data)

                for text, images in all_extracted_data:
                    if text:
                        print(f"Extracted Text: {text}")
                        insert_into_db('GeneralPumpDetails', text)  # Insert into GeneralPumpDetails
                        for img_path in images:
                            print(f"Saved Image: {img_path}")

                flash('Blank tech data uploaded successfully')
                return redirect(url_for('admin.blank_tech_data_upload'))
    return render_template('admin/blank_tech_data_upload.html', form=form)

@admin_bp.route('/admin/view-blank-tech-data')
def view_blank_tech_data():
    data = fetch_all_from_table('GeneralPumpDetails')
    return render_template('admin/view_blank_tech_data.html', data=data)

@admin_bp.route('/admin/download-blank-tech-data')
def download_blank_tech_data():
    data = fetch_all_from_table('GeneralPumpDetails')

    # Convert data to DataFrame
    df = pd.DataFrame(data, columns=['SKU', 'Name', 'Poles', 'KW', 'IE Class', 'MEI', 'Weight', 'Length', 'Width', 'Height', 'Image Path'])

    # Save DataFrame to an Excel file
    excel_path = os.path.join(tempfile.gettempdir(), 'blank_tech_data.xlsx')
    df.to_excel(excel_path, index=False)

    return send_file(excel_path, as_attachment=True, attachment_filename='blank_tech_data.xlsx')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf'}

def allowed_zip_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'zip'

def process_and_store_pdf(pdf_path, extraction_function, output_folder):
    try:
        extracted_text, extracted_images = extraction_function(pdf_path, image_output_folder=output_folder)
        print(f"Extracted Text from {pdf_path}:\n{extracted_text}")
        return extracted_text, extracted_images
    except Exception as e:
        print(f"Error processing PDF {pdf_path}: {e}")
        return None, None

def extract_and_process_zip(zip_path, extraction_function, output_folder):
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
                        text, images = process_and_store_pdf(file_path, extraction_function, output_folder)
                        if text is not None and images is not None:
                            extracted_data.append((text, images))
                            print(f"Extracted Text from {file_path}: {text}")
                            for img_path in images:
                                print(f"Saved Image: {img_path}")
                        else:
                            print(f"Failed to extract data from {file_path}")
    return extracted_data
