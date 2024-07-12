import re
import fitz  # PyMuPDF

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
        
        return text
    except Exception as e:
        return f"Error processing PDF with PyMuPDF: {e}"

def extract_blank_nbg_tech_data(pdf_path):
    text_pymupdf = extract_text_pymupdf(pdf_path)
    return extract_blank_pdf_info(text_pymupdf, pdf_path)

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

# Placeholder for the future historic data extraction logic
def extract_historic_nbg_tech_data(pdf_path):
    pass  # Implement the specific logic for historic NBG Tech Data here
