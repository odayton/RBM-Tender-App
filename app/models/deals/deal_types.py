import enum

class AustralianState(enum.Enum):
    """Australian states and territories."""
    NSW = "New South Wales"
    VIC = "Victoria"
    QLD = "Queensland"
    WA = "Western Australia"
    SA = "South Australia"
    TAS = "Tasmania"
    NT = "Northern Territory"
    ACT = "Australian Capital Territory"

class DealType(enum.Enum):
    """Types of deals."""
    HVAC = "HVAC"
    HYDRAULIC = "Hydraulic"
    HYDRONIC = "Hydronic"
    DATA_CENTRES = "Data Centres"
    MERCHANT = "Merchant"
    WHOLESALER = "Wholesaler"
    OEM = "OEM"

class DealStage(enum.Enum):
    """Deal pipeline stages."""
    SALES_LEAD = "Sales Lead"
    TENDER = "Tender"
    PROPOSAL = "Proposal"
    NEGOTIATION = "Negotiation"
    WON = "Won"
    LOST = "Lost"
    ABANDONED = "Abandoned"