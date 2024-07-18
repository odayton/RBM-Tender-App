import re
import fitz  # PyMuPDF
import os
from PIL import Image
from app.utils.db_utils import insert_into_db

def extract_rotated_text(pdf_path):
    pdf_document = fitz.open(pdf_path)
    last_page = pdf_document[-1]
    last_page.set_rotation(90)  # Rotate the last page by 90 degrees
    text = last_page.get_text("text")
    pdf_document.close()
    return text

def extract_text_pymupdf(pdf_path):
    try:
        pdf_document = fitz.open(pdf_path)
        text = ""
        
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text += page.get_text("text")
        
        pdf_document.close()
        return text
    except Exception as e:
        return f"Error processing PDF with PyMuPDF: {e}"

def extract_blank_nbg_tech_data(pdf_path, image_output_folder="extracted_blank_graphs"):
    text_pymupdf = extract_text_pymupdf(pdf_path)
    image = Blank_Graph_Extraction(pdf_path, text_pymupdf, image_output_folder)
    return extract_blank_pdf_info(text_pymupdf, pdf_path), image

def extract_historic_nbg_tech_data(pdf_path, image_output_folder="extracted_historic_graphs"):
    text_pymupdf = extract_text_pymupdf(pdf_path)
    image = Historic_Graph_Extraction(pdf_path, text_pymupdf, image_output_folder)
    return extract_historic_pdf_info(text_pymupdf, pdf_path), image

def extract_blank_pdf_info(text, pdf_path):
    pdf_info = {
        'sku': '',
        'name': '',
        'poles': 0,
        'kw': 0.0,
        'ie_class': '',
        'mei': 0.0,
        'weight': 0.0,
        'length': 0.0,
        'width': 0.0,
        'height': 0.0,
    }

    # Extract rotated text from the last page
    last_page_text = extract_rotated_text(pdf_path)

    # Extract dimensions from the last page text
    disclaimer_match = re.search(r'Disclaimer: This simplified dimensional drawing does not show all details.\n([\s\S]*)', last_page_text)
    if disclaimer_match:
        dimensions_text = disclaimer_match.group(1).strip()
        dimensions = list(map(float, re.findall(r'\d+\.?\d*', dimensions_text)))

        if len(dimensions) >= 22:
            pdf_info['length'] = dimensions[0] + dimensions[3]
            pdf_info['width'] = dimensions[15] + dimensions[16]
            pdf_info['height'] = dimensions[19] + dimensions[20]

    # Use regex to find the values for each field
    sku_match = re.search(r'Product No\.\s*:\s*(\d+)', text)
    name_match = re.search(r'\b(NBG[\w\s-]+/\d+)', text)
    poles_match = re.search(r'Number of poles\s*:\s*(\d+)', text)
    kw_match = re.search(r'Rated power - P2\s*:\s*([\d.]+)\s*kW', text)
    ie_class_match = re.search(r'IE Efficiency class\s*:\s*(\w+)', text)
    mei_match = re.search(r'Minimum efficiency index, MEI ≥\s*:\s*([\d.]+)', text)
    weight_match = re.search(r'Gross weight\s*:\s*([\d.]+)\s*kg', text)

    if sku_match:
        pdf_info['sku'] = sku_match.group(1)
    if name_match:
        pdf_info['name'] = name_match.group(1).strip()
    if poles_match:
        pdf_info['poles'] = int(poles_match.group(1))
    if kw_match:
        pdf_info['kw'] = float(kw_match.group(1))
    if ie_class_match:
        pdf_info['ie_class'] = ie_class_match.group(1)
    if mei_match:
        pdf_info['mei'] = float(mei_match.group(1))
    if weight_match:
        pdf_info['weight'] = float(weight_match.group(1))

    return pdf_info

def extract_historic_pdf_info(text, pdf_path):
    pdf_info = {
        'sku': '',
        'name': '',
        'flow': 0.0,
        'flow_unit': '',
        'head': 0.0,
        'head_unit': '',
        'efficiency': '',
        'absorbed_power': '',
        'npsh': ''
    }

    # Use regex to find the values for each field
    sku_match = re.search(r'Product No\.\s*:\s*(\d+)', text)
    name_match = re.search(r'\b(NBG[\w\s-]+/\d+)', text)
    flow_match = re.search(r'Actual calculated flow\s*:\s*([\d.]+)\s*(l/s|m\^3/h)', text)
    head_match = re.search(r'Resulting head of the pump\s*:\s*([\d.]+)\s*(kPa|m)', text)
    efficiency_match = re.search(r'Eta pump\s*=\s*([\d.]+%)', text)
    absorbed_power_match = re.search(r'P2\s*=\s*([\d.]+)\s*(kW)', text)
    npsh_match = re.search(r'NPSH\s*=\s*([\d.]+)\s*(kPa|m)', text)

    if sku_match:
        pdf_info['sku'] = sku_match.group(1)
    if name_match:
        pdf_info['name'] = name_match.group(1).strip()
    if flow_match:
        pdf_info['flow'] = float(flow_match.group(1))
        pdf_info['flow_unit'] = flow_match.group(2).replace('/', '')
    if head_match:
        pdf_info['head'] = float(head_match.group(1))
        pdf_info['head_unit'] = head_match.group(2)
    if efficiency_match:
        pdf_info['efficiency'] = efficiency_match.group(1)
    if absorbed_power_match:
        pdf_info['absorbed_power'] = absorbed_power_match.group(1)
    if npsh_match:
        pdf_info['npsh'] = npsh_match.group(1)

    return pdf_info

def Blank_Graph_Extraction(pdf_path, text, output_folder="extracted_blank_graphs"):
    pdf_document = fitz.open(pdf_path)
    os.makedirs(output_folder, exist_ok=True)

    # Extract SKU and Name for image naming
    sku_match = re.search(r'Product No\.\s*:\s*(\d+)', text)
    name_match = re.search(r'\b(NBG[\w\s-]+/\d+)', text)
    sku = sku_match.group(1) if sku_match else "unknown_sku"
    name = name_match.group(1).replace("/", "-") if name_match else "unknown_name"
    image_base_name = f"{sku}-{name}"

    cropped_image_path = None

    # Only render and save the third page as an image
    if len(pdf_document) >= 3:
        page_num = 2  # Third page (0-indexed)
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap()
        full_image_path = os.path.join(output_folder, f"{image_base_name}.png")
        pix.save(full_image_path)

        # Crop the image using specified pixel values
        img = Image.open(full_image_path)
        left = 50   # Adjust as needed
        top = 75    # Adjust as needed
        right = 525 # Adjust as needed
        bottom = 450 # Adjust as needed
        crop_box = (left, top, right, bottom)
        cropped_img = img.crop(crop_box)
        cropped_image_path = os.path.join(output_folder, f"{image_base_name}_graph.png")
        cropped_img.save(cropped_image_path)
        
        # Remove the full image as it's not needed
        os.remove(full_image_path)

    pdf_document.close()
    return cropped_image_path

def Historic_Graph_Extraction(pdf_path, text, output_folder="extracted_historic_graphs"):
    pdf_document = fitz.open(pdf_path)
    os.makedirs(output_folder, exist_ok=True)

    # Extract SKU, Name, Flow, and Head for image naming
    sku_match = re.search(r'Product No\.\s*:\s*(\d+)', text)
    name_match = re.search(r'\b(NBG[\w\s-]+/\d+)', text)
    flow_match = re.search(r'Actual calculated flow\s*:\s*([\d.]+)\s*(l/s|m\^3/h)', text)
    head_match = re.search(r'Resulting head of the pump\s*:\s*([\d.]+)\s*(kPa|m)', text)
    sku = sku_match.group(1) if sku_match else "unknown_sku"
    name = name_match.group(1).replace("/", "-") if name_match else "unknown_name"
    flow = flow_match.group(1).replace('.', '-') if flow_match else "unknown_flow"
    flow_unit = flow_match.group(2).replace('/', '') if flow_match else "unknown_unit"
    head = head_match.group(1).replace('.', '-') if head_match else "unknown_head"
    head_unit = head_match.group(2) if head_match else "unknown_unit"
    image_base_name = f"{sku}-{name}-{flow}-{flow_unit}-{head}-{head_unit}"

    cropped_image_path = None

    # Only render and save the third page as an image
    if len(pdf_document) >= 3:
        page_num = 2  # Third page (0-indexed)
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap()
        full_image_path = os.path.join(output_folder, f"{image_base_name}.png")
        pix.save(full_image_path)

        # Crop the image using specified pixel values
        img = Image.open(full_image_path)
        left = 50   # Adjust as needed
        top = 75    # Adjust as needed
        right = 525 # Adjust as needed
        bottom = 450 # Adjust as needed
        crop_box = (left, top, right, bottom)
        cropped_img = img.crop(crop_box)
        cropped_image_path = os.path.join(output_folder, f"{image_base_name}_graph.png")
        cropped_img.save(cropped_image_path)
        
        # Remove the full image as it's not needed
        os.remove(full_image_path)

    pdf_document.close()
    return cropped_image_path

def process_and_store_pdf(pdf_path, extraction_function, output_folder, is_historic=False):
    try:
        extracted_text, extracted_images = extraction_function(pdf_path, image_output_folder=output_folder)
        print(f"Extracted Text from {pdf_path}:\n{extracted_text}")
        
        if is_historic:
            # Insert into HistoricPumpDetails table
            data = {
                'sku': extracted_text['sku'],
                'name': extracted_text['name'],
                'flow': extracted_text['flow'],
                'flow_unit': extracted_text['flow_unit'],
                'head': extracted_text['head'],
                'head_unit': extracted_text['head_unit'],
                'efficiency': extracted_text['efficiency'],
                'absorbed_power': extracted_text['absorbed_power'],
                'npsh': extracted_text['npsh'],
                'image_path': extracted_images if extracted_images else ''
            }
            insert_into_db('HistoricPumpDetails', data)
        else:
            # Insert into GeneralPumpDetails table
            data = {
                'sku': extracted_text['sku'],
                'name': extracted_text['name'],
                'poles': extracted_text['poles'],
                'kw': extracted_text['kw'],
                'ie_class': extracted_text['ie_class'],
                'mei': extracted_text['mei'],
                'weight': extracted_text['weight'],
                'length': extracted_text['length'],
                'width': extracted_text['width'],
                'height': extracted_text['height'],
                'image_path': extracted_images if extracted_images else ''
            }
            insert_into_db('GeneralPumpDetails', data)
        
        return extracted_text, extracted_images
    except Exception as e:
        print(f"Error processing PDF {pdf_path}: {e}")
        return None, None
