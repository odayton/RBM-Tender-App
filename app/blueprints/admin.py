import os
import tempfile
import zipfile
import pandas as pd
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file, current_app
from werkzeug.utils import secure_filename

from app.utils.extract_pdf import extract_blank_nbg_tech_data
from app.utils.db_utils.db_connection import get_db_connection
from app.utils.db_utils.db_inertia_bases import insert_inertia_base
from app.utils.db_utils.db_rubber_mounts import insert_rubber_mount
from app.utils.db_utils.db_seismic_springs import insert_seismic_spring
from app.utils.db_utils.db_additional_price_adders import insert_additional_price_adder
from app.utils.db_utils.db_contacts import insert_contact, fetch_all_contacts
from app.utils.db_utils.db_deal_owners import insert_deal_owner
from app.utils.db_utils.db_companies import insert_company, fetch_all_companies
from app.utils.db_utils.db_pumps import fetch_all_general_pumps, insert_general_pump_details
from app.blueprints.forms import (
    InertiaBaseForm, ContactForm, SeismicSpringForm, BlankTechDataUploadForm,
    CompanyForm, DealOwnerForm, RubberMountForm, AdditionalPriceAdderForm, FileUploadForm
)

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/admin/create_contact', methods=['GET', 'POST'])
def create_contact():
    form = ContactForm()
    companies = fetch_all_companies()
    form.company_id.choices = [(company['id'], company['company_name']) for company in companies]

    if request.method == 'POST' and form.validate_on_submit():
        contact_data = {
            'representative_name': form.representative_name.data,
            'representative_email': form.representative_email.data,
            'phone_number': form.phone_number.data,
            'company_id': form.company_id.data,
        }
        try:
            insert_contact(contact_data)
            flash('Contact created successfully!', 'success')
            return redirect(url_for('admin.create_contact'))
        except Exception as e:
            flash(f"Error creating contact: {str(e)}", "danger")

    return render_template('admin/create_contact.html', form=form)

@admin_bp.route('/admin/create-deal-owner', methods=['GET', 'POST'])
def create_deal_owner():
    form = DealOwnerForm()
    if form.validate_on_submit():
        owner_data = {
            'owner_name': form.owner_name.data,
            'email': form.email.data,
            'phone_number': form.phone_number.data
        }
        try:
            insert_deal_owner(owner_data)
            flash("Deal owner created successfully!", "success")
            return redirect(url_for('admin.create_deal_owner'))
        except Exception as e:
            flash(f"Error creating deal owner: {str(e)}", "danger")
    return render_template('admin/create_deal_owner.html', form=form)

@admin_bp.route('/admin/create-company', methods=['GET', 'POST'])
def create_company():
    form = CompanyForm()
    if form.validate_on_submit():
        company_data = {
            'company_name': form.company_name.data, 
            'address': form.address.data
        }
        try:
            insert_company(company_data)
            flash("Company created successfully!", "success")
            return redirect(url_for('admin.create_company'))
        except Exception as e:
            flash(f"Error creating company: {str(e)}", "danger")
    return render_template('admin/create_company.html', form=form)

@admin_bp.route('/admin/blank-tech-data-upload', methods=['GET', 'POST'])
def blank_tech_data_upload():
    form = BlankTechDataUploadForm()
    if request.method == 'POST' and form.validate_on_submit():
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
                        insert_general_pump_details(extracted_text)

            if zip_file and allowed_zip_file(zip_file.filename):
                zip_filename = secure_filename(zip_file.filename)
                temp_path = os.path.join(tempfile.gettempdir(), zip_filename)
                zip_file.save(temp_path)
                extracted_data = extract_and_process_zip(temp_path, extract_blank_nbg_tech_data, "extracted_blank_graphs")
                all_extracted_data.extend(extracted_data)

            for text, images in all_extracted_data:
                if text:
                    insert_general_pump_details(text)

            flash('Blank tech data processed successfully. New pumps inserted and existing ones updated.')
            return redirect(url_for('admin.blank_tech_data_upload'))
    return render_template('admin/blank_tech_data_upload.html', form=form)

@admin_bp.route('/admin/view-blank-tech-data')
def view_blank_tech_data():
    data = fetch_all_general_pumps()
    return render_template('admin/view_blank_tech_data.html', data=data)

@admin_bp.route('/admin/download-blank-tech-data')
def download_blank_tech_data():
    data = fetch_all_general_pumps()
    df = pd.DataFrame(data, columns=['SKU', 'Name', 'Poles', 'KW', 'IE Class', 'MEI', 'Weight', 'Length', 'Width', 'Height', 'Image Path'])
    excel_path = os.path.join(tempfile.gettempdir(), 'blank_tech_data.xlsx')
    df.to_excel(excel_path, index=False)
    return send_file(excel_path, as_attachment=True, attachment_filename='blank_tech_data.xlsx')

@admin_bp.route('/admin/create-inertia-bases', methods=['GET', 'POST'])
def create_inertia_bases():
    form = InertiaBaseForm()
    file_form = FileUploadForm()
    if form.validate_on_submit():
        inertia_base_data = {
            'part_number': form.part_number.data,
            'length': form.length.data,
            'width': form.width.data,
            'height': form.height.data,
            'spring_mount_height': form.spring_mount_height.data,
            'weight': form.weight.data,
            'spring_amount': form.spring_amount.data,
            'cost': form.cost.data
        }
        insert_inertia_base(inertia_base_data)
        flash('Inertia Base added successfully', 'success')
        return redirect(url_for('admin.create_inertia_bases'))
    return render_template('admin/create_inertia_bases.html', form=form, file_form=file_form)

@admin_bp.route('/admin/upload-inertia-bases', methods=['POST'])
def upload_inertia_bases():
    form = FileUploadForm()
    if form.validate_on_submit():
        file = form.file.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            process_inertia_bases_file(file_path)
            flash('Inertia Bases uploaded successfully', 'success')
        else:
            flash('Invalid file type', 'error')
    return redirect(url_for('admin.create_inertia_bases'))

@admin_bp.route('/admin/create-rubber-mounts', methods=['GET', 'POST'])
def create_rubber_mounts():
    form = RubberMountForm()
    file_form = FileUploadForm()
    if form.validate_on_submit():
        rubber_mount_data = {
            'part_number': form.part_number.data,
            'name': form.name.data,
            'weight': form.weight.data,
            'cost': form.cost.data
        }
        insert_rubber_mount(rubber_mount_data)
        flash('Rubber Mount added successfully', 'success')
        return redirect(url_for('admin.create_rubber_mounts'))
    return render_template('admin/create_rubber_mounts.html', form=form, file_form=file_form)

@admin_bp.route('/admin/upload-rubber-mounts', methods=['POST'])
def upload_rubber_mounts():
    form = FileUploadForm()
    if form.validate_on_submit():
        file = form.file.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            process_rubber_mounts_file(file_path)
            flash('Rubber Mounts uploaded successfully', 'success')
        else:
            flash('Invalid file type', 'error')
    return redirect(url_for('admin.create_rubber_mounts'))

@admin_bp.route('/admin/create-seismic-springs', methods=['GET', 'POST'])
def create_seismic_springs():
    form = SeismicSpringForm()
    file_form = FileUploadForm()
    if form.validate_on_submit():
        seismic_spring_data = {
            'part_number': form.part_number.data,
            'name': form.name.data,
            'max_load_kg': form.max_load_kg.data,
            'static_deflection': form.static_deflection.data,
            'spring_constant_kg_mm': form.spring_constant_kg_mm.data,
            'stripe1': form.stripe1.data,
            'stripe2': form.stripe2.data,
            'cost': form.cost.data
        }
        insert_seismic_spring(seismic_spring_data)
        flash('Seismic Spring added successfully', 'success')
        return redirect(url_for('admin.create_seismic_springs'))
    return render_template('admin/create_seismic_springs.html', form=form, file_form=file_form)

@admin_bp.route('/admin/upload-seismic-springs', methods=['POST'])
def upload_seismic_springs():
    form = FileUploadForm()
    if form.validate_on_submit():
        file = form.file.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            process_seismic_springs_file(file_path)
            flash('Seismic Springs uploaded successfully', 'success')
        else:
            flash('Invalid file type', 'error')
    return redirect(url_for('admin.create_seismic_springs'))

@admin_bp.route('/admin/create-additional-price-adders', methods=['GET', 'POST'])
def create_additional_price_adders():
    form = AdditionalPriceAdderForm()
    file_form = FileUploadForm()
    if form.validate_on_submit():
        adder_data = {
            'name': form.name.data,
            'price': form.price.data
        }
        insert_additional_price_adder(adder_data)
        flash('Additional Price Adder added successfully', 'success')
        return redirect(url_for('admin.create_additional_price_adders'))
    return render_template('admin/create_additional_price_adders.html', form=form, file_form=file_form)

@admin_bp.route('/admin/upload-additional-price-adders', methods=['POST'])
def upload_additional_price_adders():
    form = FileUploadForm()
    if form.validate_on_submit():
        file = form.file.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            process_additional_price_adders_file(file_path)
            flash('Additional Price Adders uploaded successfully', 'success')
        else:
            flash('Invalid file type', 'error')
    return redirect(url_for('admin.create_additional_price_adders'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'xlsx', 'xls'}

def allowed_zip_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'zip'

def process_and_store_pdf(pdf_path, extraction_function, output_folder):
    try:
        extracted_text, extracted_images = extraction_function(pdf_path, image_output_folder=output_folder)
        return extracted_text, extracted_images
    except Exception as e:
        print(f"Error processing PDF {pdf_path}: {e}")
        return None, None

def extract_and_process_zip(zip_path, extraction_function, output_folder):
    extracted_data = []
    with tempfile.TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if allowed_file(file):
                        file_path = os.path.join(root, file)
                        text, images = process_and_store_pdf(file_path, extraction_function, output_folder)
                        if text is not None and images is not None:
                            extracted_data.append((text, images))
    return extracted_data

def process_inertia_bases_file(file_path):
    df = pd.read_excel(file_path)
    for _, row in df.iterrows():
        inertia_base_data = {
            'part_number': row['PartNumber'],
            'length': row['Length'],
            'width': row['Width'],
            'height': row['Height'],
            'spring_mount_height': row['SpringMountHeight'],
            'weight': row['Weight'],
            'spring_amount': row['SpringAmount'],
            'cost': row['Cost']
        }
        insert_inertia_base(inertia_base_data)
    os.remove(file_path)  # Remove the temporary file after processing

def process_rubber_mounts_file(file_path):
    df = pd.read_excel(file_path)
    for _, row in df.iterrows():
        rubber_mount_data = {
            'part_number': row['PartNumber'],
            'name': row['Name'],
            'weight': row['Weight'],
            'cost': row['Cost']
        }
        insert_rubber_mount(rubber_mount_data)
    os.remove(file_path)

def process_seismic_springs_file(file_path):
    df = pd.read_excel(file_path)
    for _, row in df.iterrows():
        seismic_spring_data = {
            'part_number': row['PartNumber'],
            'name': row['Name'],
            'max_load_kg': row['MaxLoad_kg'],
            'static_deflection': row['StaticDeflection'],
            'spring_constant_kg_mm': row['SpringConstant_kg_mm'],
            'stripe1': row['Stripe1'],
            'stripe2': row['Stripe2'],
            'cost': row['Cost']
        }
        insert_seismic_spring(seismic_spring_data)
    os.remove(file_path)

def process_additional_price_adders_file(file_path):
    df = pd.read_excel(file_path)
    for _, row in df.iterrows():
        adder_data = {
            'name': row['Name'],
            'price': row['Price']
        }
        insert_additional_price_adder(adder_data)
    os.remove(file_path)