# app/utils/db_utils/export/report_generator.py

from typing import Dict, List, Any, Optional, Union
import logging
from datetime import datetime, timedelta
import pandas as pd
from app.core.core_database import DatabaseManager, DatabaseError
from .excel_export import ExcelExporter
from .pdf_export import PDFExporter

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Handles generation of various business reports"""

    @staticmethod
    def generate_sales_report(
        start_date: datetime,
        end_date: datetime,
        format: str = 'excel'
    ) -> bytes:
        """Generate sales report for specified period"""
        try:
            query = """
                SELECT 
                    d.id as deal_id,
                    d.name as deal_name,
                    d.stage,
                    d.type as deal_type,
                    d.amount,
                    d.created_at,
                    d.close_date,
                    c.representative_name as contact_name,
                    comp.company_name,
                    do.owner_name as deal_owner
                FROM deals d
                LEFT JOIN contacts c ON d.contact_id = c.id
                LEFT JOIN companies comp ON d.company_id = comp.id
                LEFT JOIN deal_owners do ON d.owner = do.id
                WHERE d.created_at BETWEEN %s AND %s
                ORDER BY d.created_at DESC
            """
            
            data = DatabaseManager.execute_query(query, (start_date, end_date))
            
            if format == 'excel':
                return ReportGenerator._generate_excel_sales_report(data, start_date, end_date)
            elif format == 'pdf':
                return ReportGenerator._generate_pdf_sales_report(data, start_date, end_date)
            else:
                raise ValueError(f"Unsupported format: {format}")

        except Exception as e:
            logger.error(f"Error generating sales report: {str(e)}")
            raise DatabaseError(f"Failed to generate sales report: {str(e)}")

    @staticmethod
    def generate_pump_usage_report(period_months: int = 12) -> bytes:
        """Generate pump usage analysis report"""
        try:
            query = """
                WITH pump_usage AS (
                    SELECT 
                        p.sku,
                        p.name as pump_name,
                        p.poles,
                        p.kw,
                        COUNT(li.id) as usage_count,
                        SUM(li.amount) as total_revenue,
                        MAX(li.created_at) as last_used
                    FROM general_pump_details p
                    LEFT JOIN line_items li ON li.entity_id = p.sku 
                        AND li.entity_type = 'pump'
                        AND li.created_at >= NOW() - INTERVAL '%s months'
                    GROUP BY p.sku, p.name, p.poles, p.kw
                )
                SELECT 
                    sku,
                    pump_name,
                    poles,
                    kw,
                    usage_count,
                    total_revenue,
                    last_used,
                    CASE 
                        WHEN usage_count = 0 THEN 'Inactive'
                        WHEN usage_count > 10 THEN 'High Usage'
                        WHEN usage_count > 5 THEN 'Medium Usage'
                        ELSE 'Low Usage'
                    END as usage_category
                FROM pump_usage
                ORDER BY usage_count DESC, total_revenue DESC
            """
            
            data = DatabaseManager.execute_query(query, (period_months,))
            return ReportGenerator._generate_excel_pump_report(data, period_months)

        except Exception as e:
            logger.error(f"Error generating pump usage report: {str(e)}")
            raise DatabaseError(f"Failed to generate pump usage report: {str(e)}")

    @staticmethod
    def generate_deal_pipeline_report() -> bytes:
        """Generate deal pipeline analysis report"""
        try:
            query = """
                WITH pipeline_stats AS (
                    SELECT 
                        stage,
                        COUNT(*) as deal_count,
                        SUM(amount) as total_amount,
                        AVG(amount) as avg_amount,
                        MIN(created_at) as oldest_deal,
                        MAX(created_at) as newest_deal,
                        AVG(EXTRACT(EPOCH FROM (NOW() - created_at))/86400) as avg_age_days
                    FROM deals
                    WHERE stage NOT IN ('Closed Won', 'Closed Lost', 'Abandoned')
                    GROUP BY stage
                ),
                stage_conversion AS (
                    SELECT 
                        stage,
                        COUNT(*) FILTER (WHERE stage = 'Closed Won') as won_count,
                        COUNT(*) as total_count,
                        ROUND(COUNT(*) FILTER (WHERE stage = 'Closed Won')::NUMERIC / 
                              NULLIF(COUNT(*), 0) * 100, 2) as conversion_rate
                    FROM deals
                    GROUP BY stage
                )
                SELECT 
                    ps.*,
                    sc.conversion_rate
                FROM pipeline_stats ps
                LEFT JOIN stage_conversion sc ON ps.stage = sc.stage
                ORDER BY 
                    CASE 
                        WHEN ps.stage = 'Sales Lead' THEN 1
                        WHEN ps.stage = 'Tender' THEN 2
                        WHEN ps.stage = 'Proposal' THEN 3
                        WHEN ps.stage = 'Negotiation' THEN 4
                        ELSE 5
                    END
            """
            
            data = DatabaseManager.execute_query(query)
            return ReportGenerator._generate_excel_pipeline_report(data)

        except Exception as e:
            logger.error(f"Error generating pipeline report: {str(e)}")
            raise DatabaseError(f"Failed to generate pipeline report: {str(e)}")

    @staticmethod
    def _generate_excel_sales_report(data: List[Dict], start_date: datetime, end_date: datetime) -> bytes:
        """Generate formatted Excel sales report"""
        writer, header_format = ExcelExporter.create_workbook()
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Create summary sheet
        summary_data = {
            'Total Deals': len(df),
            'Total Value': df['amount'].sum(),
            'Average Deal Size': df['amount'].mean(),
            'Won Deals': len(df[df['stage'] == 'Closed Won']),
            'Lost Deals': len(df[df['stage'] == 'Closed Lost']),
            'Period Start': start_date,
            'Period End': end_date
        }
        
        summary_df = pd.DataFrame([summary_data])
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Create details sheet
        df.to_excel(writer, sheet_name='Deal Details', index=False)
        
        # Format sheets
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            df_to_format = summary_df if sheet_name == 'Summary' else df
            
            # Format headers
            for col_num, value in enumerate(df_to_format.columns.values):
                worksheet.write(0, col_num, value, header_format)
                worksheet.set_column(col_num, col_num, 15)
            
            # Auto-filter
            worksheet.autofilter(0, 0, len(df_to_format), len(df_to_format.columns) - 1)
        
        writer.close()
        return writer.handles.handle.getvalue()

    @staticmethod
    def _generate_excel_pump_report(data: List[Dict], period_months: int) -> bytes:
        """Generate formatted Excel pump usage report"""
        writer, header_format = ExcelExporter.create_workbook()
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Create summary statistics
        summary_data = {
            'Total Pumps': len(df),
            'Active Pumps': len(df[df['usage_count'] > 0]),
            'Total Revenue': df['total_revenue'].sum(),
            'High Usage Pumps': len(df[df['usage_category'] == 'High Usage']),
            'Medium Usage Pumps': len(df[df['usage_category'] == 'Medium Usage']),
            'Low Usage Pumps': len(df[df['usage_category'] == 'Low Usage']),
            'Inactive Pumps': len(df[df['usage_category'] == 'Inactive']),
            'Analysis Period (Months)': period_months
        }
        
        summary_df = pd.DataFrame([summary_data])
        
        # Write sheets
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        df.to_excel(writer, sheet_name='Pump Details', index=False)
        
        # Format sheets
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            df_to_format = summary_df if sheet_name == 'Summary' else df
            
            # Format headers
            for col_num, value in enumerate(df_to_format.columns.values):
                worksheet.write(0, col_num, value, header_format)
                worksheet.set_column(col_num, col_num, 15)
            
            worksheet.autofilter(0, 0, len(df_to_format), len(df_to_format.columns) - 1)
        
        writer.close()
        return writer.handles.handle.getvalue()

    @staticmethod
    def _generate_excel_pipeline_report(data: List[Dict]) -> bytes:
        """Generate formatted Excel pipeline report"""
        writer, header_format = ExcelExporter.create_workbook()
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Add calculated fields
        df['avg_age_days'] = df['avg_age_days'].round(1)
        df['total_amount'] = df['total_amount'].round(2)
        df['avg_amount'] = df['avg_amount'].round(2)
        
        # Write and format
        df.to_excel(writer, sheet_name='Pipeline Analysis', index=False)
        worksheet = writer.sheets['Pipeline Analysis']
        
        # Format headers
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, 15)
        
        writer.close()
        return writer.handles.handle.getvalue()