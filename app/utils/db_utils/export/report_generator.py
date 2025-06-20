from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
from io import BytesIO
from app.core.core_database import DatabaseManager, DatabaseError
from .excel_export import ExcelExporter
from .pdf_export import PDFExporter
from app.core.core_logging import logger # Use central app logger

class ReportGenerator:
    """Handles generation of various business reports"""

    @staticmethod
    def generate_sales_report(
        start_date: datetime,
        end_date: datetime,
        format: str = 'excel'
    ) -> bytes:
        """Generate sales report for a specified period."""
        logger.info(f"Generating sales report from {start_date} to {end_date} in {format} format.")
        try:
            query = """
                SELECT 
                    d.id as deal_id, d.name as deal_name, d.stage, d.type as deal_type,
                    d.amount, d.created_at, d.close_date,
                    c.representative_name as contact_name, comp.company_name, do.owner_name as deal_owner
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
                # Assuming PDFExporter has a method for this kind of report
                # This would need to be implemented in pdf_export.py
                raise NotImplementedError("PDF sales report is not yet implemented.")
            else:
                raise ValueError(f"Unsupported format: {format}")

        except Exception as e:
            logger.error(f"Error generating sales report: {e}", exc_info=True)
            raise DatabaseError(f"Failed to generate sales report: {e}")

    @staticmethod
    def generate_pump_usage_report(period_months: int = 12) -> bytes:
        """Generate pump usage analysis report for a given period in months."""
        logger.info(f"Generating pump usage report for the last {period_months} months.")
        try:
            query = """
                WITH pump_usage AS (
                    SELECT 
                        p.sku, p.name as pump_name, p.poles, p.kw,
                        COUNT(li.id) as usage_count,
                        SUM(li.amount) as total_revenue,
                        MAX(li.created_at) as last_used
                    FROM general_pump_details p
                    LEFT JOIN line_items li ON li.entity_id = p.sku AND li.entity_type = 'pump'
                                            AND li.created_at >= NOW() - INTERVAL '%s months'
                    GROUP BY p.sku, p.name, p.poles, p.kw
                )
                SELECT 
                    sku, pump_name, poles, kw, usage_count, total_revenue, last_used,
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
            logger.error(f"Error generating pump usage report: {e}", exc_info=True)
            raise DatabaseError(f"Failed to generate pump usage report: {e}")

    @staticmethod
    def generate_deal_pipeline_report() -> bytes:
        """Generate deal pipeline analysis report."""
        logger.info("Generating deal pipeline report.")
        try:
            query = """
                WITH pipeline_stats AS (
                    SELECT 
                        stage, COUNT(*) as deal_count, SUM(amount) as total_amount,
                        AVG(amount) as avg_amount, MIN(created_at) as oldest_deal,
                        MAX(created_at) as newest_deal,
                        AVG(EXTRACT(EPOCH FROM (NOW() - created_at))/86400) as avg_age_days
                    FROM deals
                    WHERE stage NOT IN ('Closed Won', 'Closed Lost', 'Abandoned')
                    GROUP BY stage
                )
                SELECT * FROM pipeline_stats
                ORDER BY avg_age_days DESC
            """
            data = DatabaseManager.execute_query(query)
            return ReportGenerator._generate_excel_pipeline_report(data)

        except Exception as e:
            logger.error(f"Error generating pipeline report: {e}", exc_info=True)
            raise DatabaseError(f"Failed to generate pipeline report: {e}")

    @staticmethod
    def _generate_excel_sales_report(data: List[Dict], start_date: datetime, end_date: datetime) -> bytes:
        """Generate a formatted multi-sheet Excel sales report."""
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            details_df = pd.DataFrame(data)
            
            summary_data = {
                'Metric': ['Total Deals', 'Total Value', 'Average Deal Size', 'Won Deals', 'Lost Deals', 'Period Start', 'Period End'],
                'Value': [
                    len(details_df),
                    details_df['amount'].sum(),
                    details_df['amount'].mean(),
                    len(details_df[details_df['stage'] == 'Closed Won']),
                    len(details_df[details_df['stage'] == 'Closed Lost']),
                    start_date.strftime('%Y-%m-%d'),
                    end_date.strftime('%Y-%m-%d')
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            
            ExcelExporter._format_worksheet(writer, summary_df, 'Summary')
            ExcelExporter._format_worksheet(writer, details_df, 'Deal Details')
        
        return output.getvalue()

    @staticmethod
    def _generate_excel_pump_report(data: List[Dict], period_months: int) -> bytes:
        """Generate a formatted multi-sheet Excel pump usage report."""
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            details_df = pd.DataFrame(data)
            
            summary_data = {
                'Metric': ['Total Pumps Analysed', 'Active Pumps', 'Total Revenue', 'High Usage', 'Medium Usage', 'Low Usage', 'Inactive', 'Analysis Period (Months)'],
                'Value': [
                    len(details_df),
                    len(details_df[details_df['usage_count'] > 0]),
                    details_df['total_revenue'].sum(),
                    len(details_df[details_df['usage_category'] == 'High Usage']),
                    len(details_df[details_df['usage_category'] == 'Medium Usage']),
                    len(details_df[details_df['usage_category'] == 'Low Usage']),
                    len(details_df[details_df['usage_category'] == 'Inactive']),
                    period_months
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            
            ExcelExporter._format_worksheet(writer, summary_df, 'Summary')
            ExcelExporter._format_worksheet(writer, details_df, 'Pump Details')
        
        return output.getvalue()

    @staticmethod
    def _generate_excel_pipeline_report(data: List[Dict]) -> bytes:
        """Generate a formatted Excel pipeline report."""
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df = pd.DataFrame(data)
            # Perform rounding for cleaner output
            for col in ['total_amount', 'avg_amount', 'avg_age_days']:
                if col in df.columns:
                    df[col] = df[col].round(2)
            
            ExcelExporter._format_worksheet(writer, df, 'Pipeline Analysis')

        return output.getvalue()