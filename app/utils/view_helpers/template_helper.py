from typing import Dict, Any, List, Optional
from datetime import datetime
from decimal import Decimal

class TemplateHelper:
    """Helper functions for template rendering"""
    
    @staticmethod
    def format_currency(value: Optional[Decimal], default: str = '$0.00') -> str:
        """Format currency value"""
        if value is None:
            return default
        return f'${value:,.2f}'
    
    @staticmethod
    def format_date(value: Optional[datetime], format_str: str = '%Y-%m-%d') -> str:
        """Format date value"""
        if value is None:
            return ''
        return value.strftime(format_str)
    
    @staticmethod
    def format_date_dd_mm_yyyy(value: Optional[datetime]) -> str:
        """Format date value in dd-mm-yyyy format"""
        if value is None:
            return ''
        return value.strftime('%d-%m-%Y')
    
    @staticmethod
    def format_datetime(value: Optional[datetime], format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
        """Format datetime value"""
        if value is None:
            return ''
        return value.strftime(format_str)
    
    @staticmethod
    def get_deal_stage_class(stage: str) -> str:
        """Get CSS class for deal stage"""
        stage_classes = {
            'Sales Lead': 'bg-blue-100 text-blue-800',
            'Tender': 'bg-yellow-100 text-yellow-800',
            'Proposal': 'bg-purple-100 text-purple-800',
            'Negotiation': 'bg-orange-100 text-orange-800',
            'Won': 'bg-green-100 text-green-800',
            'Lost': 'bg-red-100 text-red-800',
            'Abandoned': 'bg-gray-100 text-gray-800'
        }
        return stage_classes.get(stage, 'bg-gray-100 text-gray-800')
    
    @staticmethod
    def truncate_text(text: str, length: int = 50) -> str:
        """Truncate text to specified length"""
        if not text:
            return ''
        if len(text) <= length:
            return text
        return text[:length] + '...'
    
    @staticmethod
    def get_file_icon(filename: str) -> str:
        """Get appropriate icon class for file type"""
        ext = filename.split('.')[-1].lower()
        icons = {
            'pdf': 'file-pdf',
            'xlsx': 'file-excel',
            'xls': 'file-excel',
            'doc': 'file-word',
            'docx': 'file-word'
        }
        return icons.get(ext, 'file')
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} TB"

    @staticmethod
    def format_phone(phone: Optional[str]) -> str:
        """Format phone number"""
        if not phone:
            return ''
        # Remove non-numeric characters
        clean_phone = ''.join(filter(str.isdigit, phone))
        if len(clean_phone) == 10:
            return f"({clean_phone[:3]}) {clean_phone[3:6]}-{clean_phone[6:]}"
        return phone
    
    @staticmethod
    def add_months_to_date(date_value, months: int = 1) -> datetime:
        """Add months to a date and return datetime object"""
        from datetime import datetime, timedelta
        
        if isinstance(date_value, str) and date_value == "now":
            current_date = datetime.now()
        elif isinstance(date_value, datetime):
            current_date = date_value
        else:
            current_date = datetime.now()
        
        # Add months using relativedelta for proper month handling
        try:
            from dateutil.relativedelta import relativedelta
            future_date = current_date + relativedelta(months=months)
        except ImportError:
            # Fallback to simple addition if dateutil is not available
            # This is a simplified approach - adds 30 days per month
            future_date = current_date + timedelta(days=30 * months)
        
        return future_date
    
