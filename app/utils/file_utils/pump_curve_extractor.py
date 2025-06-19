import re
import fitz  # PyMuPDF
import os
import io
from PIL import Image
from typing import Tuple, Dict, Any, Optional

# --- Helper Functions ---

def extract_rotated_text(pdf_path: str) -> str:
    """Extracts text from the last page of a PDF after rotating it 90 degrees."""
    try:
        with fitz.open(pdf_path) as pdf_document:
            if not len(pdf_document):
                return ""
            last_page = pdf_document[-1]
            last_page.set_rotation(90)
            text = last_page.get_text("text")
        return text
    except Exception as e:
        return f"Error extracting rotated text: {e}"

def extract_text_pymupdf(pdf_path: str) -> str:
    """Extracts all text from every page of a PDF document."""
    try:
        with fitz.open(pdf_path) as pdf_document:
            text = ""
            for page in pdf_document:
                text += page.get_text("text")
        return text
    except Exception as e:
        return f"Error processing PDF with PyMuPDF: {e}"


# --- Main Extraction Logic ---

def extract_blank_nbg_tech_data(pdf_path: str) -> Tuple[Dict[str, Any], Optional[Tuple[str, bytes]]]:
    """
    Orchestrates the extraction of data and the graph image from a blank tech data PDF.

    Args:
        pdf_path (str): The full path to the saved PDF file.

    Returns:
        A tuple containing:
        - A dictionary of the extracted pump information.
        - A tuple of (filename, image_bytes) for the graph, or None if no graph is found.
    """
    text_pymupdf = extract_text_pymupdf(pdf_path)
    info_dict = extract_blank_pdf_info(text_pymupdf, pdf_path)
    
    graph_tuple = extract_and_crop_image_from_pdf(pdf_path, text_pymupdf)
    
    return info_dict, graph_tuple


def extract_historic_nbg_tech_data(pdf_path: str) -> Tuple[Dict[str, Any], Optional[Tuple[str, bytes]]]:
    """
    Orchestrates the extraction of data and the graph image from a historic tech data PDF.

    Args:
        pdf_path (str): The full path to the saved PDF file.

    Returns:
        A tuple containing:
        - A dictionary of the extracted pump information.
        - A tuple of (filename, image_bytes) for the graph, or None if no graph is found.
    """
    text_pymupdf = extract_text_pymupdf(pdf_path)
    info_dict = extract_historic_pdf_info(text_pymupdf)

    graph_tuple = extract_and_crop_image_from_pdf_historic(pdf_path, text_pymupdf)

    return info_dict, graph_tuple


# --- Data and Image Processing Details ---

def extract_and_crop_image_from_pdf(pdf_path: str, text: str) -> Optional[Tuple[str, bytes]]:
    """
    Extracts, crops, and returns a graph image from a "blank" PDF as bytes.
    It no longer saves the file itself.

    Args:
        pdf_path (str): Path to the PDF file.
        text (str): Full text extracted from the PDF for naming.

    Returns:
        A tuple of (filename, image_bytes) or None if an error occurs.
    """
    try:
        with fitz.open(pdf_path) as pdf_document:
            if len(pdf_document) < 3:
                return None

            sku_match = re.search(r'Product No\.\s*:\s*(\d+)', text)
            name_match = re.search(r'\b(NBG[\w\s-]+/\d+)', text)
            sku = sku_match.group(1) if sku_match else "unknown_sku"
            name = name_match.group(1).replace("/", "-") if name_match else "unknown_name"
            final_filename = f"{sku}-{name}_graph.png"
            
            page = pdf_document.load_page(2)
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            crop_box = (50, 75, 525, 450)
            cropped_img = img.crop(crop_box)

            img_byte_buffer = io.BytesIO()
            cropped_img.save(img_byte_buffer, format='PNG')
            
            return final_filename, img_byte_buffer.getvalue()
    except Exception:
        return None


def extract_and_crop_image_from_pdf_historic(pdf_path: str, text: str) -> Optional[Tuple[str, bytes]]:
    """
    Extracts, crops, and returns a graph image from a "historic" PDF as bytes.
    It no longer saves the file itself.
    """
    try:
        with fitz.open(pdf_path) as pdf_document:
            if len(pdf_document) < 3:
                return None

            sku_match = re.search(r'Product No\.\s*:\s*(\d+)', text)
            name_match = re.search(r'\b(NBG[\w\s-]+/\d+)', text)
            flow_match = re.search(r'Actual calculated flow:\s*([\d.]+)', text)
            head_match = re.search(r'Resulting head of the pump:\s*([\d.]+)', text)
            sku = sku_match.group(1) if sku_match else "unknown_sku"
            name = name_match.group(1).replace("/", "-") if name_match else "unknown_name"
            flow = flow_match.group(1) if flow_match else "x"
            head = head_match.group(1) if head_match else "x"
            final_filename = f"{sku}-{name}-{flow}lps-{head}kpa_graph.png"
            
            page = pdf_document.load_page(2)
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            crop_box = (50, 75, 525, 450)
            cropped_img = img.crop(crop_box)

            img_byte_buffer = io.BytesIO()
            cropped_img.save(img_byte_buffer, format='PNG')

            return final_filename, img_byte_buffer.getvalue()
    except Exception:
        return None


def extract_blank_pdf_info(text: str, pdf_path: str) -> Dict[str, Any]:
    """Extracts textual information from a "blank" tech data sheet."""
    pdf_info = {
        'sku': '', 'name': '', 'poles': 0, 'kw': 0.0, 'ie_class': '', 
        'mei': 0.0, 'weight': 0.0, 'length': 0.0, 'width': 0.0, 'height': 0.0
    }

    last_page_text = extract_rotated_text(pdf_path)
    disclaimer_match = re.search(r'Disclaimer:.*?([\s\S]*)', last_page_text)
    if disclaimer_match:
        dimensions_text = disclaimer_match.group(1).strip()
        dimensions = [float(d) for d in re.findall(r'\d+\.?\d*', dimensions_text)]
        if len(dimensions) >= 22:
            pdf_info.update({
                'length': dimensions[0] + dimensions[3],
                'width': dimensions[15] + dimensions[16],
                'height': dimensions[19] + dimensions[20]
            })

    sku_match = re.search(r'Product No\.\s*:\s*(\d+)', text)
    name_match = re.search(r'\b(NBG[\w\s-]+/\d+)', text)
    poles_match = re.search(r'Number of poles\s*:\s*(\d+)', text)
    kw_match = re.search(r'Rated power - P2\s*:\s*([\d.]+)\s*kW', text)
    ie_class_match = re.search(r'IE Efficiency class\s*:\s*(\w+)', text)
    mei_match = re.search(r'Minimum efficiency index, MEI ≥\s*:\s*([\d.]+)', text)
    weight_match = re.search(r'Gross weight\s*:\s*([\d.]+)\s*kg', text)

    if sku_match: pdf_info['sku'] = sku_match.group(1)
    if name_match: pdf_info['name'] = name_match.group(1).strip()
    if poles_match: pdf_info['poles'] = int(poles_match.group(1))
    if kw_match: pdf_info['kw'] = float(kw_match.group(1))
    if ie_class_match: pdf_info['ie_class'] = ie_class_match.group(1)
    if mei_match: pdf_info['mei'] = float(mei_match.group(1))
    if weight_match: pdf_info['weight'] = float(weight_match.group(1))
    
    return pdf_info


def extract_historic_pdf_info(text: str) -> Dict[str, Any]:
    """Extracts textual information from a "historic" tech data sheet."""
    pdf_info = {
        'sku': '', 'name': '', 'flow': 0.0, 'flow_unit': '', 'head': 0.0, 
        'head_unit': '', 'efficiency': '', 'absorbed_power': '', 'npsh': ''
    }

    sku_match = re.search(r'Product No\.\s*:\s*(\d+)', text)
    name_match = re.search(r'\b(NBG[\w\s-]+/\d+)', text)
    flow_match = re.search(r'Actual calculated flow:\s*([\d.]+)\s*(l/s|m\^3/h)', text)
    head_match = re.search(r'Resulting head of the pump:\s*([\d.]+)\s*(kPa)', text)
    efficiency_match = re.search(r'Eta pump\s*=\s*([\d.]+)\s*%', text)
    absorbed_power_match = re.search(r'P2 =\s*([\d.]+\s*kW)', text)
    npsh_match = re.search(r'NPSH =\s*([\d.]+)\s*kPa', text)

    if sku_match: pdf_info['sku'] = sku_match.group(1)
    if name_match: pdf_info['name'] = name_match.group(1).strip()
    if flow_match:
        pdf_info['flow'] = float(flow_match.group(1))
        pdf_info['flow_unit'] = flow_match.group(2).replace('^', '')
    if head_match:
        pdf_info['head'] = float(head_match.group(1))
        pdf_info['head_unit'] = head_match.group(2)
    if efficiency_match: pdf_info['efficiency'] = efficiency_match.group(1) + '%'
    if absorbed_power_match: pdf_info['absorbed_power'] = absorbed_power_match.group(1)
    if npsh_match: pdf_info['npsh'] = npsh_match.group(1)
    
    return pdf_info