from typing import Dict, List, Optional
from sqlalchemy import func
from app.extensions import db
from app.models import Company, Contact, DealCompany  # Assuming DealCompany is your junction model
from app.core.core_errors import DatabaseError
from app.core.core_logging import logger

class CompanyDatabaseManager:
    """Handles all company-related database operations using the SQLAlchemy ORM."""

    @staticmethod
    def validate_company_data(company_data: Dict) -> None:
        """Validate company data before insertion/update."""
        if not company_data.get('company_name'):
            raise ValueError("Company name is required.")

    @staticmethod
    def insert_company(company_data: Dict) -> Company:
        """Insert a new company using the ORM."""
        try:
            CompanyDatabaseManager.validate_company_data(company_data)
            
            new_company = Company(**company_data)
            db.session.add(new_company)
            db.session.commit()
            
            logger.info(f"Successfully inserted company '{new_company.company_name}' with ID: {new_company.id}")
            return new_company
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error inserting company: {e}", exc_info=True)
            raise DatabaseError(f"Failed to insert company: {e}")

    @staticmethod
    def fetch_all_companies_with_counts() -> List[Company]:
        """Fetch all companies with contact and deal counts."""
        try:
            # Subquery for contact counts
            contact_count_sub = db.session.query(
                Contact.company_id, func.count(Contact.id).label('contacts_count')
            ).group_by(Contact.company_id).subquery()

            # Subquery for deal counts
            deal_count_sub = db.session.query(
                DealCompany.company_id, func.count(DealCompany.deal_id).label('deals_count')
            ).group_by(DealCompany.company_id).subquery()

            # Main query joining the counts
            return db.session.query(
                Company, 
                contact_count_sub.c.contacts_count, 
                deal_count_sub.c.deals_count
            ).outerjoin(
                contact_count_sub, Company.id == contact_count_sub.c.company_id
            ).outerjoin(
                deal_count_sub, Company.id == deal_count_sub.c.company_id
            ).order_by(Company.company_name).all()

        except Exception as e:
            logger.error(f"Error fetching all companies with counts: {e}", exc_info=True)
            raise DatabaseError(f"Failed to fetch companies: {e}")

    @staticmethod
    def add_company_to_deal(deal_id: int, company_id: int) -> Optional[DealCompany]:
        """Add a company to a deal, preventing duplicates."""
        try:
            # Check if the association already exists
            existing = DealCompany.query.filter_by(deal_id=deal_id, company_id=company_id).first()
            if existing:
                logger.warning(f"Company {company_id} is already associated with deal {deal_id}.")
                return existing

            new_association = DealCompany(deal_id=deal_id, company_id=company_id)
            db.session.add(new_association)
            db.session.commit()
            
            logger.info(f"Successfully added company {company_id} to deal {deal_id}.")
            return new_association
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding company {company_id} to deal {deal_id}: {e}", exc_info=True)
            raise DatabaseError(f"Failed to add company to deal: {e}")

    @staticmethod
    def update_company(company_id: int, updated_data: Dict) -> Optional[Company]:
        """Update company information."""
        try:
            company = Company.query.get(company_id)
            if not company:
                logger.warning(f"Attempted to update non-existent company with ID {company_id}.")
                return None

            # Update fields from the dictionary
            for key, value in updated_data.items():
                if hasattr(company, key):
                    setattr(company, key, value)
            
            db.session.commit()
            logger.info(f"Successfully updated company with ID: {company_id}")
            return company
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating company {company_id}: {e}", exc_info=True)
            raise DatabaseError(f"Failed to update company: {e}")

    @staticmethod
    def fetch_company_by_id(company_id: int) -> Optional[Company]:
        """Fetch a specific company by its ID."""
        try:
            return Company.query.get(company_id)
        except Exception as e:
            logger.error(f"Error fetching company by ID {company_id}: {e}", exc_info=True)
            raise DatabaseError(f"Failed to fetch company: {e}")