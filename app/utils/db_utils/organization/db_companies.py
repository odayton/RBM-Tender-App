# app/utils/db_utils/db_companies.py

from typing import Dict, List, Optional
import logging
from app.core.core_database import DatabaseManager, DatabaseError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompanyDatabaseManager:
    """Handles all company-related database operations"""

    @staticmethod
    def create_company_tables() -> None:
        """Creates company-related tables with PostgreSQL optimizations"""
        try:
            queries = [
                # Companies table
                """
                CREATE TABLE IF NOT EXISTS companies (
                    id SERIAL PRIMARY KEY,
                    company_name TEXT NOT NULL,
                    address TEXT,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(company_name);
                """,

                # Deal Companies junction table
                """
                CREATE TABLE IF NOT EXISTS deal_companies (
                    id SERIAL PRIMARY KEY,
                    deal_id INTEGER REFERENCES deals(id) ON DELETE CASCADE,
                    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
                    UNIQUE (deal_id, company_id)
                );

                CREATE INDEX IF NOT EXISTS idx_deal_companies ON deal_companies(deal_id, company_id);
                """
            ]

            for query in queries:
                DatabaseManager.execute_query(query)

            logger.info("Company tables created successfully")
        except Exception as e:
            logger.error(f"Error creating company tables: {str(e)}")
            raise DatabaseError(f"Failed to create company tables: {str(e)}")

    @staticmethod
    def validate_company_data(company_data: Dict) -> None:
        """Validate company data before insertion/update"""
        if not company_data.get('company_name'):
            raise ValueError("Company name is required")

    @staticmethod
    def insert_company(company_data: Dict) -> int:
        """Insert a new company"""
        try:
            # Validate company data
            CompanyDatabaseManager.validate_company_data(company_data)

            fields = ', '.join(company_data.keys())
            placeholders = ', '.join(['%s'] * len(company_data))
            query = f"""
                INSERT INTO companies ({fields})
                VALUES ({placeholders})
                RETURNING id
            """
            
            return DatabaseManager.insert_returning_id(query, tuple(company_data.values()))

        except Exception as e:
            logger.error(f"Error inserting company: {str(e)}")
            raise DatabaseError(f"Failed to insert company: {str(e)}")

    @staticmethod
    def fetch_all_companies() -> List[Dict]:
        """Fetch all companies with basic information"""
        try:
            query = """
                SELECT c.*,
                    (SELECT COUNT(*) FROM contacts WHERE company_id = c.id) as contacts_count,
                    (SELECT COUNT(*) FROM deal_companies WHERE company_id = c.id) as deals_count
                FROM companies c
                ORDER BY c.company_name
            """
            return DatabaseManager.execute_query(query)

        except Exception as e:
            logger.error(f"Error fetching companies: {str(e)}")
            raise DatabaseError(f"Failed to fetch companies: {str(e)}")

    @staticmethod
    def add_company_to_deal(deal_id: int, company_id: int) -> None:
        """Add a company to a deal"""
        try:
            query = """
                INSERT INTO deal_companies (deal_id, company_id)
                VALUES (%s, %s)
                ON CONFLICT (deal_id, company_id) DO NOTHING
            """
            DatabaseManager.execute_query(query, (deal_id, company_id))

        except Exception as e:
            logger.error(f"Error adding company to deal: {str(e)}")
            raise DatabaseError(f"Failed to add company to deal: {str(e)}")

    @staticmethod
    def update_company(company_id: int, updated_data: Dict) -> None:
        """Update company information"""
        try:
            # Get existing company data
            existing_company = CompanyDatabaseManager.fetch_company_by_id(company_id)
            if not existing_company:
                raise DatabaseError(f"Company {company_id} not found")

            # Validate updated data
            CompanyDatabaseManager.validate_company_data({
                **existing_company,
                **updated_data
            })

            fields = [f"{k} = %s" for k in updated_data.keys()]
            query = f"""
                UPDATE companies 
                SET {', '.join(fields)}
                WHERE id = %s
            """
            values = list(updated_data.values()) + [company_id]
            DatabaseManager.execute_query(query, tuple(values))

        except Exception as e:
            logger.error(f"Error updating company: {str(e)}")
            raise DatabaseError(f"Failed to update company: {str(e)}")

    @staticmethod
    def fetch_company_by_id(company_id: int) -> Optional[Dict]:
        """Fetch a specific company"""
        try:
            query = """
                SELECT c.*,
                    (SELECT COUNT(*) FROM contacts WHERE company_id = c.id) as contacts_count,
                    (SELECT COUNT(*) FROM deal_companies WHERE company_id = c.id) as deals_count
                FROM companies c
                WHERE c.id = %s
            """
            results = DatabaseManager.execute_query(query, (company_id,))
            return results[0] if results else None

        except Exception as e:
            logger.error(f"Error fetching company: {str(e)}")
            raise DatabaseError(f"Failed to fetch company: {str(e)}")

# Initialize tables when module is imported
try:
    CompanyDatabaseManager.create_company_tables()
except Exception as e:
    logger.error(f"Failed to initialize company tables: {str(e)}")