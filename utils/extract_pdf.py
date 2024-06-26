from pdfminer.high_level import extract_text
import re

def extract_pdf_info(pdf_path):
    pdf_info = {
        'sku': '',
        'name': '',
        'flow_l_s': 0.0,
        'head_kpa': 0.0,
        'head_m': 0.0,  # Calculated as head_kpa / 9.81
        'poles': 0,
        'kw': 0.0,
        'ie_class': '',
        'mei': 0.0,
        'absorbed_power': 0.0,
        'npsh': 0.0,
        'npsh_unit': '',
        'efficiency': 0.0,
        'weight': 0.0,
        'length': 0.0,
        'width': 0.0,
        'height': 0.0,
        'cost': 0.0,
        'link': ''  # New field for link
    }

    text = extract_text(pdf_path)

    # Extract dimensions from the text (if applicable)
    disclaimer_match = re.search(r'Disclaimer: This simplified dimensional drawing does not show all details.\n([\s\S]*)', text)
    if disclaimer_match:
        dimensions_text = disclaimer_match.group(1).strip()
        dimensions = list(map(float, re.findall(r'\d+\.?\d*', dimensions_text)))

        if len(dimensions) >= 22:
            pdf_info['length'] = dimensions[0] + dimensions[3]
            pdf_info['width'] = dimensions[15] + dimensions[16]
            pdf_info['height'] = dimensions[19] + dimensions[20]

    model_type = 'NBG' if 'NBG' in text else 'CR'

    # Use regex to find the values for each field
    sku_match = re.search(r'Product No\.\s*:\s*(\d+)', text)
    name_match = re.search(r'(\d+)\s+([\w\s-]+)\s*\n', text) if model_type == 'CR' else re.search(r'\b(NBG[\w\s-]+/\d+)', text)
    flow_match = re.search(r'Actual calculated flow\s*:\s*([\d.]+)\s*l/s', text)
    head_kpa_match = re.search(r'Resulting head of the pump\s*:\s*([\d.]+)\s*kPa', text)
    poles_match = re.search(r'Number of poles\s*:\s*(\d+)', text)
    kw_match = re.search(r'Rated power - P2\s*:\s*([\d.]+)\s*kW', text)
    ie_class_match = re.search(r'IE Efficiency class\s*:\s*(\w+)', text)
    mei_match = re.search(r'Minimum efficiency index, MEI ≥\s*:\s*([\d.]+)', text)
    absorbed_power_match = re.search(r'P2\s*=\s*([\d.]+)\s*kW', text)
    npsh_match = re.search(r'NPSH\s*=\s*([\d.]+)\s*(kPa|m)', text)
    efficiency_match = re.search(r'Eta pump\s*=\s*([\d.]+)\s*%', text)
    weight_match = re.search(r'Gross weight\s*:\s*([\d.]+)\s*kg', text)
    cost_match = re.search(r'Cost\s*:\s*([\d.]+)', text)

    if sku_match:
        pdf_info['sku'] = sku_match.group(1)
    if name_match:
        if model_type == 'CR':
            pdf_info['name'] = name_match.group(2).strip()
        else:
            pdf_info['name'] = name_match.group(1).strip()
            formatted_name = pdf_info['name'].lower().replace(' ', '-').replace('/', '')
            url = f"https://product-selection.grundfos.com/au/products/nbg-nbge/nbg/{formatted_name}-{pdf_info['sku']}"
            pdf_info['link'] = f'<a href="{url}">link</a>'
            print(f"Generated link: {pdf_info['link']}")
    if flow_match:
        pdf_info['flow_l_s'] = float(flow_match.group(1))
    if head_kpa_match:
        pdf_info['head_kpa'] = float(head_kpa_match.group(1))
        pdf_info['head_m'] = round(pdf_info['head_kpa'] / 9.81, 2)
    if poles_match:
        pdf_info['poles'] = int(poles_match.group(1))
    if kw_match:
        pdf_info['kw'] = float(kw_match.group(1))
    if ie_class_match:
        pdf_info['ie_class'] = ie_class_match.group(1)
    if mei_match:
        pdf_info['mei'] = float(mei_match.group(1))
    if absorbed_power_match:
        pdf_info['absorbed_power'] = float(absorbed_power_match.group(1))
    if npsh_match:
        pdf_info['npsh'] = float(npsh_match.group(1))
        pdf_info['npsh_unit'] = npsh_match.group(2)
    if efficiency_match:
        pdf_info['efficiency'] = float(efficiency_match.group(1))
    if weight_match:
        pdf_info['weight'] = float(weight_match.group(1))
    if cost_match:
        pdf_info['cost'] = float(cost_match.group(1))

    return pdf_info
