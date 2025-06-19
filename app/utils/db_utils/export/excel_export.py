# app/utils/db_utils/export/excel_export.py

from typing import Dict, List, Any, Optional, Union
import logging
import pandas as pd
from io import BytesIO
from datetime import datetime
from app.core.core_database import DatabaseManager, DatabaseError

logger = logging.getLogger(__name__)

class ExcelExporter:
    """Handles Excel export functionality for database data"""

    @staticmethod
    def create_workbook() -> tuple[pd.ExcelWriter, Any]:
        """Create a new Excel workbook with standard formatting"""
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        workbook = writer.book
        
        # Define standard formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4F81BD',
            'color': 'white',
            'border': 1,
            'text_wrap': True,
            'valign': 'vcenter'
        })
        
        return writer, header_format

    @staticmethod
    def export_pump_data(filters: Optional[Dict] = None) -> bytes:
        """Export pump data to Excel file"""
        try:
            # Build base query
            query = """
                SELECT 
                    gp.sku,
                    gp.name as pump_name,
                    gp.poles,
                    gp.kw,
                    gp.ie_class,
                    gp.mei,
                    gp.weight,
                    gp.length,
                    gp.width,
                    gp.height,
                    gp.list_price,
                    hp.flow,
                    hp.flow_unit,
                    hp.head,
                    hp.head_unit,
                    hp.efficiency,
                    hp.absorbed_power,
                    hp.npsh
                FROM general_pump_details gp
                LEFT JOIN historic_pump_data hp ON gp.sku = hp.sku
                WHERE 1=1
            """
            
            params = []
            if filters:
                if 'sku' in filters:
                    query += " AND gp.sku = %s"
                    params.append(filters['sku'])
                if 'kw_range' in filters:
                    query += " AND gp.kw BETWEEN %s AND %s"
                    params.extend(filters['kw_range'])

            # Create workbook
            writer, header_format = ExcelExporter.create_workbook()
            
            # Fetch and write data
            data = DatabaseManager.execute_query(query, tuple(params) if params else None)
            df = pd.DataFrame(data)
            
            # Write to Excel with formatting
            df.to_excel(writer, sheet_name='Pump Data', index=False)
            worksheet = writer.sheets['Pump Data']
            
            # Format headers
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                worksheet.set_column(col_num, col_num, 15)

            # Auto-filter
            worksheet.autofilter(0, 0, len(df), len(df.columns) - 1)
            
            # Save and return
            writer.close()
            return writer.handles.handle.getvalue()

        except Exception as e:
            logger.error(f"Error exporting pump data: {str(e)}")
            raise DatabaseError(f"Failed to export pump data: {str(e)}")

    @staticmethod
    def export_deal_data(deal_id: int) -> bytes:
        """Export deal data with line items to Excel file"""
        try:
            # Fetch deal data
            deal_query = """
                SELECT 
                    d.id as deal_id,
                    d.name as deal_name,
                    d.stage,
                    d.type as deal_type,
                    d.location,
                    d.close_date,
                    d.owner,
                    c.representative_name as contact_name,
                    comp.company_name,
                    d.amount as total_amount,
                    d.created_at,
                    d.updated_at
                FROM deals d
                LEFT JOIN contacts c ON d.contact_id = c.id
                LEFT JOIN companies comp ON d.company_id = comp.id
                WHERE d.id = %s
            """
            
            # Fetch line items
            items_query = """
                SELECT 
                    entity_type,
                    entity_id,
                    pump_name,
                    flow,
                    head,
                    description,
                    amount,
                    created_at
                FROM line_items
                WHERE deal_id = %s
                ORDER BY created_at
            """
            
            deal_data = DatabaseManager.execute_query(deal_query, (deal_id,))
            line_items = DatabaseManager.execute_query(items_query, (deal_id,))
            
            if not deal_data:
                raise DatabaseError(f"Deal {deal_id} not found")

            # Create workbook
            writer, header_format = ExcelExporter.create_workbook()
            
            # Write deal details
            deal_df = pd.DataFrame([deal_data[0]])
            deal_df.to_excel(writer, sheet_name='Deal Details', index=False)
            
            # Write line items
            items_df = pd.DataFrame(line_items)
            items_df.to_excel(writer, sheet_name='Line Items', index=False)
            
            # Format sheets
            for sheet_name in ['Deal Details', 'Line Items']:
                worksheet = writer.sheets[sheet_name]
                df = deal_df if sheet_name == 'Deal Details' else items_df
                
                # Format headers
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                    worksheet.set_column(col_num, col_num, 15)
                
                # Auto-filter
                worksheet.autofilter(0, 0, len(df), len(df.columns) - 1)
            
            # Save and return
            writer.close()
            return writer.handles.handle.getvalue()

        except Exception as e:
            logger.error(f"Error exporting deal data: {str(e)}")
            raise DatabaseError(f"Failed to export deal data: {str(e)}")

    @staticmethod
    def export_bom_data(filters: Optional[Dict] = None) -> bytes:
        """Export BOM data to Excel file"""
        try:
            query = """
                SELECT 
                    b.pump_sku,
                    gp.name as pump_name,
                    b.inertia_base_part_number,
                    ib.name as inertia_base_name,
                    b.seismic_spring_part_number,
                    ss.name as spring_name,
                    b.created_at
                FROM bom b
                LEFT JOIN general_pump_details gp ON b.pump_sku = gp.sku
                LEFT JOIN inertia_bases ib ON b.inertia_base_part_number = ib.part_number
                LEFT JOIN seismic_springs ss ON b.seismic_spring_part_number = ss.part_number
                WHERE 1=1
            """
            
            params = []
            if filters:
                if 'pump_sku' in filters:
                    query += " AND b.pump_sku = %s"
                    params.append(filters['pump_sku'])

            # Create workbook
            writer, header_format = ExcelExporter.create_workbook()
            
            # Fetch and write data
            data = DatabaseManager.execute_query(query, tuple(params) if params else None)
            df = pd.DataFrame(data)
            
            # Write to Excel with formatting
            df.to_excel(writer, sheet_name='BOM Data', index=False)
            worksheet = writer.sheets['BOM Data']
            
            # Format headers
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                worksheet.set_column(col_num, col_num, 15)

            # Auto-filter
            worksheet.autofilter(0, 0, len(df), len(df.columns) - 1)
            
            # Save and return
            writer.close()
            return writer.handles.handle.getvalue()

        except Exception as e:
            logger.error(f"Error exporting BOM data: {str(e)}")
            raise DatabaseError(f"Failed to export BOM data: {str(e)}")