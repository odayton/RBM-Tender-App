from enum import Enum, auto
from typing import Dict, List

class FeatureFlags:
    # Add attributes or methods here
    ENABLE_SOME_FEATURE = True

class Paths:
    # Add relevant attributes or methods
    BASE_DIR = "/path/to/base"
    TECH_DATA_DIR = f"{BASE_DIR}/uploads/tech-data"
    HISTORIC_GRAPHS_DIR = f"{BASE_DIR}/extracted_historic_graphs"
    BLANK_GRAPHS_DIR = f"{BASE_DIR}/extracted_blank_graphs"
    GENERAL_UPLOADS_DIR = f"{BASE_DIR}/uploads/others"

    @staticmethod
    def get_full_path(relative_path: str) -> str:
        """Get the full path for a given relative path."""
        return f"{Paths.BASE_DIR}/{relative_path}"


class PumpType(Enum):
    """Pump types available in the system"""
    NBG = "NBG"
    CR = "CR"
    TP = "TP"
    CM = "CM"
    MAGNA = "MAGNA"
    UPS = "UPS"
    CRE = "CRE"
    TPE = "TPE"
    NK = "NK"

class AustralianState(Enum):
    """Australian states and territories"""
    NSW = "New South Wales"
    VIC = "Victoria"
    QLD = "Queensland"
    WA = "Western Australia"
    SA = "South Australia"
    TAS = "Tasmania"
    NT = "Northern Territory"
    ACT = "Australian Capital Territory"

class DealType(Enum):
    """Types of deals"""
    HVAC = "HVAC"
    HYDRAULIC = "Hydraulic"
    HYDRONIC = "Hydronic"
    DATA_CENTRES = "Data Centres"
    MERCHANT = "Merchant"
    WHOLESALER = "Wholesaler"
    OEM = "OEM"

class DealStage(Enum):
    """Deal pipeline stages"""
    SALES_LEAD = "Sales Lead"
    TENDER = "Tender"
    PROPOSAL = "Proposal"
    NEGOTIATION = "Negotiation"
    WON = "Won"
    LOST = "Lost"
    ABANDONED = "Abandoned"

# File upload constants
ALLOWED_EXTENSIONS: Dict[str, List[str]] = {
    'pdf': ['pdf'],
    'excel': ['xlsx', 'xls'],
    'image': ['jpg', 'jpeg', 'png']
}

# Path constants
UPLOAD_PATHS = {
    'tech_data': 'uploads/tech-data',
    'historic_graphs': 'extracted_historic_graphs',
    'blank_graphs': 'extracted_blank_graphs',
    'general': 'uploads/others'
}

# Database constants
DB_DATE_FORMAT = "%Y-%m-%d"
DB_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Pagination constants
ITEMS_PER_PAGE = {
    'deals': 20,
    'pumps': 50,
    'search_results': 25
}

# Form constants
FORM_VALIDATORS = {
    'min_flow_rate': 0,
    'max_flow_rate': 10000,
    'min_head': 0,
    'max_head': 1000,
    'min_power': 0,
    'max_power': 1000
}

# Display constants
CURRENCY_SYMBOL = '$'
DECIMAL_PLACES = 2

# System settings
CACHE_TIMEOUT = 300  # seconds
MAX_UPLOAD_SIZE = 16 * 1024 * 1024  # 16MB
MAX_SEARCH_RESULTS = 100

# Stage transition mappings
STAGE_TRANSITIONS = {
    DealStage.SALES_LEAD: [DealStage.TENDER, DealStage.ABANDONED],
    DealStage.TENDER: [DealStage.PROPOSAL, DealStage.LOST, DealStage.ABANDONED],
    DealStage.PROPOSAL: [DealStage.NEGOTIATION, DealStage.LOST, DealStage.ABANDONED],
    DealStage.NEGOTIATION: [DealStage.WON, DealStage.LOST, DealStage.ABANDONED],
    DealStage.WON: [],  # No transitions from Won
    DealStage.LOST: [DealStage.SALES_LEAD],  # Can reopen as Sales Lead
    DealStage.ABANDONED: [DealStage.SALES_LEAD]  # Can reopen as Sales Lead
}

# Stage colors for UI
STAGE_COLORS = {
    DealStage.SALES_LEAD: 'blue',
    DealStage.TENDER: 'yellow',
    DealStage.PROPOSAL: 'purple',
    DealStage.NEGOTIATION: 'orange',
    DealStage.WON: 'green',
    DealStage.LOST: 'red',
    DealStage.ABANDONED: 'gray'
}

# Error messages
ERROR_MESSAGES = {
    'required_field': 'This field is required.',
    'invalid_email': 'Please enter a valid email address.',
    'invalid_phone': 'Please enter a valid phone number.',
    'invalid_number': 'Please enter a valid number.',
    'invalid_file': 'Invalid file type.',
    'file_too_large': 'File size exceeds maximum limit.',
    'invalid_date': 'Please enter a valid date.',
    'invalid_stage_transition': 'Invalid stage transition.',
    'invalid_currency': 'Please enter a valid amount.'
}

# Success messages
SUCCESS_MESSAGES = {
    'deal_created': 'Deal created successfully.',
    'deal_updated': 'Deal updated successfully.',
    'quote_created': 'Quote created successfully.',
    'quote_updated': 'Quote updated successfully.',
    'pump_selected': 'Pump selected successfully.',
    'file_uploaded': 'File uploaded successfully.',
    'data_imported': 'Data imported successfully.'
}
