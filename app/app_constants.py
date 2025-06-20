from enum import Enum

# General Application Constants
APP_NAME = "RBM-Tender-App"
APP_VERSION = "0.1.0"

# User Roles
class UserRoles(Enum):
    ADMIN = 'admin'
    ENGINEER = 'engineer'
    SALES = 'sales'
    VIEWER = 'viewer'

# Deal Statuses
class DealStatus(Enum):
    DRAFT = 'Draft'
    SUBMITTED = 'Submitted'
    WON = 'Won'
    LOST = 'Lost'
    ARCHIVED = 'Archived'

# Pricing Tiers
class PricingTier(Enum):
    STANDARD = 'Standard'
    PREMIUM = 'Premium'
    DISCOUNTED = 'Discounted'

# System Messages
MSG_DEAL_CREATED = "New deal created successfully."
MSG_DEAL_UPDATED = "Deal updated successfully."
MSG_INVALID_INPUT = "Invalid input provided. Please check the fields and try again."
MSG_UNAUTHORIZED_ACTION = "You are not authorized to perform this action."

# Default Values
DEFAULT_CURRENCY = "AUD"
DEFAULT_MARGIN = 1.25

# Report Types
class ReportType(Enum):
    DEAL_SUMMARY = 'deal_summary'
    SALES_PERFORMANCE = 'sales_performance'
    PUMP_USAGE = 'pump_usage'