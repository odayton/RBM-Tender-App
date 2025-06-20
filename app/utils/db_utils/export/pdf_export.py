from typing import Dict, List, Any, Optional
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from app.core.core_database import DatabaseManager, DatabaseError
from app.core.core_logging import logger # Use central app logger

class PDFExporter:
    """Handles PDF export functionality for database data"""

    @staticmethod
    def _create_pdf_styles() -> Dict[str, ParagraphStyle]:
        """Creates a dictionary of standard paragraph styles for the PDF."""
        styles = getSampleStyleSheet()
        # Add a custom title style
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['h1'],
            fontSize=18,
            leading=22,
            spaceAfter=20,
            alignment=1 # Center alignment
        ))
        styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=styles['h2'],
            fontSize=14,
            leading=18,
            spaceBefore=10,
            spaceAfter=6
        ))
        return styles

    @staticmethod
    def _create_table_style() -> TableStyle:
        """Creates standard table styling."""
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F81BD')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])

    @staticmethod
    def export_deal_quote(deal_id: int) -> bytes:
        """Export a deal quote as a PDF."""
        logger.info(f"Generating PDF quote for deal ID: {deal_id}")
        try:
            # Fetch deal and line item data
            deal_query = "SELECT d.*, c.representative_name as contact_name, c.representative_email as contact_email, c.phone_number as contact_phone, comp.company_name, comp.address as company_address FROM deals d LEFT JOIN contacts c ON d.contact_id = c.id LEFT JOIN companies comp ON d.company_id = comp.id WHERE d.id = %s"
            deal_data = DatabaseManager.execute_query(deal_query, (deal_id,))
            if not deal_data:
                raise DatabaseError(f"Deal {deal_id} not found")
            deal = deal_data[0]

            items_query = "SELECT * FROM line_items WHERE deal_id = %s ORDER BY created_at"
            line_items = DatabaseManager.execute_query(items_query, (deal_id,))
            
            # Setup PDF document
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=72, bottomMargin=72, leftMargin=72, rightMargin=72)
            styles = PDFExporter._create_pdf_styles()
            elements = []

            # Add Title
            elements.append(Paragraph(f"Quotation: {deal.get('name', 'N/A')}", styles['CustomTitle']))

            # Add Company and Contact Info
            elements.append(Paragraph("Client Information", styles['CustomHeading']))
            company_info = [
                f"<b>Company:</b> {deal.get('company_name', 'N/A')}",
                f"<b>Address:</b> {deal.get('company_address', 'N/A')}",
                f"<b>Contact:</b> {deal.get('contact_name', 'N/A')}",
                f"<b>Email:</b> {deal.get('contact_email', 'N/A')}",
                f"<b>Phone:</b> {deal.get('contact_phone', 'N/A')}"
            ]
            for info in company_info:
                elements.append(Paragraph(info, styles['Normal']))
            elements.append(Spacer(1, 24))

            # Add Line Items Table
            elements.append(Paragraph("Line Items", styles['CustomHeading']))
            if line_items:
                data = [['Description', 'Qty', 'Unit Price', 'Total']]
                for item in line_items:
                    # Assuming quantity is 1 if not specified
                    quantity = item.get('quantity', 1) 
                    unit_price = item.get('amount', 0)
                    total_price = quantity * unit_price
                    data.append([
                        item.get('description', 'N/A'),
                        str(quantity),
                        f"${unit_price:,.2f}",
                        f"${total_price:,.2f}"
                    ])
                
                table = Table(data, colWidths=[250, 50, 80, 80])
                table.setStyle(PDFExporter._create_table_style())
                elements.append(table)
                elements.append(Spacer(1, 24))

            # Add Grand Total
            elements.append(Paragraph(f"Grand Total: ${deal.get('amount', 0):,.2f}", styles['CustomHeading']))
            
            # Build the PDF
            doc.build(elements)
            
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            logger.info(f"Successfully generated PDF of {len(pdf_bytes)} bytes for deal ID: {deal_id}")
            return pdf_bytes

        except Exception as e:
            logger.error(f"Error creating quote PDF for deal ID {deal_id}: {e}", exc_info=True)
            raise DatabaseError(f"Failed to create quote PDF: {e}")