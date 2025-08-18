from typing import Dict, List, Any, Optional
import pandas as pd
from io import BytesIO
from app.core.core_database import DatabaseManager, DatabaseError
from app.core.core_logging import logger # Use central app logger

class ExcelExporter:
    """Handles Excel export functionality for database data"""

    @staticmethod
    def _format_worksheet(writer: pd.ExcelWriter, df: pd.DataFrame, sheet_name: str):
        """A helper method to apply standard formatting to an Excel worksheet."""
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]

        header_format = workbook.add_format({
            'bold': True, 'bg_color': '#4F81BD', 'color': 'white',
            'border': 1, 'text_wrap': True, 'valign': 'vcenter'
        })

        # Format headers and set column widths
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            # Set column width based on header or content length
            column_len = max(df[value].astype(str).map(len).max(), len(value))
            worksheet.set_column(col_num, col_num, column_len + 2)

        # Add auto-filter
        if not df.empty:
            worksheet.autofilter(0, 0, len(df), len(df.columns) - 1)

    @staticmethod
    def export_pump_data(filters: Optional[Dict] = None) -> bytes:
        """Export pump data to an Excel file."""
        logger.info(f"Exporting pump data with filters: {filters}")
        try:
            query = """
                SELECT 
                    gp.sku, gp.name as pump_name, gp.poles, gp.kw, gp.ie_class,
                    gp.mei, gp.weight, gp.length, gp.width, gp.height, gp.list_price,
                    hp.flow, hp.flow_unit, hp.head, hp.head_unit, hp.efficiency,
                    hp.absorbed_power, hp.npsh
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

            data = DatabaseManager.execute_query(query, tuple(params) if params else None)
            df = pd.DataFrame(data)
            
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                ExcelExporter._format_worksheet(writer, df, 'Pump Data')
            
            logger.info(f"Successfully generated Excel export for {len(df)} pumps.")
            return output.getvalue()

        except Exception as e:
            logger.error(f"Error exporting pump data: {e}", exc_info=True)
            raise DatabaseError(f"Failed to export pump data: {e}")

    @staticmethod
    def export_deal_data(deal_id: int) -> bytes:
        """Export deal data with line items to an Excel file."""
        logger.info(f"Exporting deal data for deal ID: {deal_id}")
        try:
            # Fetch deal data
            deal_query = "SELECT d.id as deal_id, d.name as deal_name, d.stage, d.type as deal_type, d.location, d.close_date, d.owner, c.representative_name as contact_name, comp.company_name, d.amount as total_amount, d.created_at, d.updated_at FROM deals d LEFT JOIN contacts c ON d.contact_id = c.id LEFT JOIN companies comp ON d.company_id = comp.id WHERE d.id = %s"
            deal_data = DatabaseManager.execute_query(deal_query, (deal_id,))
            if not deal_data:
                raise DatabaseError(f"Deal {deal_id} not found")

            # Fetch line items
            items_query = "SELECT entity_type, entity_id, pump_name, flow, head, description, amount, created_at FROM line_items WHERE deal_id = %s ORDER BY created_at"
            line_items = DatabaseManager.execute_query(items_query, (deal_id,))
            
            deal_df = pd.DataFrame(deal_data)
            items_df = pd.DataFrame(line_items)

            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                ExcelExporter._format_worksheet(writer, deal_df, 'Deal Details')
                ExcelExporter._format_worksheet(writer, items_df, 'Line Items')

            logger.info(f"Successfully generated Excel export for deal {deal_id}.")
            return output.getvalue()

        except Exception as e:
            logger.error(f"Error exporting deal data for deal ID {deal_id}: {e}", exc_info=True)
            raise DatabaseError(f"Failed to export deal data: {e}")

    @staticmethod
    def export_bom_data(filters: Optional[Dict] = None) -> bytes:
        """Export BOM data to an Excel file."""
        logger.info(f"Exporting BOM data with filters: {filters}")
        try:
            query = """
                SELECT b.pump_sku, gp.name as pump_name, b.inertia_base_part_number, 
                       ib.name as inertia_base_name, b.seismic_spring_part_number, 
                       ss.name as spring_name, b.created_at
                FROM bom b
                LEFT JOIN general_pump_details gp ON b.pump_sku = gp.sku
                LEFT JOIN inertia_bases ib ON b.inertia_base_part_number = ib.part_number
                LEFT JOIN seismic_springs ss ON b.seismic_spring_part_number = ss.part_number
                WHERE 1=1
            """
            params = []
            if filters and 'pump_sku' in filters:
                query += " AND b.pump_sku = %s"
                params.append(filters['pump_sku'])

            data = DatabaseManager.execute_query(query, tuple(params) if params else None)
            df = pd.DataFrame(data)

            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                ExcelExporter._format_worksheet(writer, df, 'BOM Data')

            logger.info(f"Successfully generated Excel export for {len(df)} BOM entries.")
            return output.getvalue()

        except Exception as e:
            logger.error(f"Error exporting BOM data: {e}", exc_info=True)
            raise DatabaseError(f"Failed to export BOM data: {e}")