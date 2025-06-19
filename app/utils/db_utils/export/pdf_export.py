# app/utils/db_utils/export/pdf_export.py

from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
from app.core.core_database import DatabaseManager, DatabaseError

logger = logging.getLogger(__name__)

class PDFExporter:
    """Handles PDF export functionality for database data"""

    @staticmethod
    def create_pdf_template(title: str) -> tuple[SimpleDocTemplate, dict]:
        """Create a PDF template with standard styling"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30
        )
        
        return doc, {
            'title_style': title_style,
            'normal_style': styles['Normal'],
            'heading_style': styles['Heading2']
        }

    @staticmethod
    def create_table_style() -> TableStyle:
        """Create standard table styling"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F81BD')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])

    @staticmethod
    def export_deal_quote(deal_id: int) -> bytes:
        """Export deal quote as PDF"""
        try:
            # Fetch deal data
            deal_query = """
                SELECT 
                    d.*,
                    c.representative_name as contact_name,
                    c.representative_email as contact_email,
                    c.phone_number as contact_phone,
                    comp.company_name,
                    comp.address as company_address
                FROM deals d
                LEFT JOIN contacts c ON d.contact_id = c.id
                LEFT JOIN companies comp ON d.company_id = comp.id
                WHERE d.id = %s
            """
            
            # Fetch line items
            items_query = """
                SELECT *
                FROM line_items
                WHERE deal_id = %s
                ORDER BY created_at
            """
            
            deal_data = DatabaseManager.execute_query(deal_query, (deal_id,))
            line_items = DatabaseManager.execute_query(items_query, (deal_id,))
            
            if not deal_data:
                raise DatabaseError(f"Deal {deal_id} not found")
                
            deal = deal_data[0]
            
            # Create PDF
            doc, styles = PDFExporter.create_pdf_template(f"Quote: {deal['name']}")
            elements = []
            
            # Add title
            elements.append(Paragraph(f"Quote: {deal['name']}", styles['title_style']))
            
            # Add company and contact info
            elements.append(Paragraph("Company Information", styles['heading_style']))
            company_info = [
                f"Company: {deal['company_name']}",
                f"Address: {deal['company_address']}",
                f"Contact: {deal['contact_name']}",
                f"Email: {deal['contact_email']}",
                f"Phone: {deal['contact_phone']}"
            ]
            for info in company_info:
                elements.append(Paragraph(info, styles['normal_style']))
                elements.append(Spacer(1, 12))
            
            # Add line items table
            elements.append(Paragraph("Line Items", styles['heading_style']))
            if line_items:
                # Define columns
                columns = ['Description', 'Quantity', 'Unit Price', 'Total']
                data = [columns]  # Header row
                
                # Add line items
                for item in line_items:
                    data.append([
                        item['description'],
                        '1',  # Default quantity
                        f"${item['amount']:,.2f}",
                        f"${item['amount']:,.2f}"
                    ])
                
                # Create table
                table = Table(data)
                table.setStyle(PDFExporter.create_table_style())
                elements.append(table)
                
                # Add total
                elements.append(Spacer(1, 20))
                elements.append(Paragraph(
                    f"Total Amount: ${deal['amount']:,.2f}",
                    styles['heading_style']
                ))
            
            # Build PDF
            doc.build(elements)
            buffer = doc.handle
            buffer.seek(0)
            return buffer.getvalue()

        except Exception as e:
            logger.error(f"Error creating quote PDF: {str(e)}")
            raise DatabaseError(f"Failed to create quote PDF: {str(e)}")