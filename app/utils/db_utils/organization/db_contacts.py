from typing import Dict, List, Optional
import re
from app.extensions import db
from app.models import Contact, Company, DealContact # Assuming these are your model names
from app.core.core_errors import DatabaseError
from app.core.core_logging import logger # Use central app logger

class ContactDatabaseManager:
    """Handles all contact-related database operations using the SQLAlchemy ORM."""

    @staticmethod
    def validate_contact_data(contact_data: Dict) -> None:
        """Validate contact data before insertion/update."""
        if not contact_data.get('representative_name'):
            raise ValueError("Representative name is required.")
        
        email = contact_data.get('representative_email')
        if not email:
            raise ValueError("Email is required.")
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError("Invalid email format.")

    @staticmethod
    def insert_contact(contact_data: Dict) -> Contact:
        """Insert a new contact using the ORM."""
        try:
            ContactDatabaseManager.validate_contact_data(contact_data)
            
            new_contact = Contact(**contact_data)
            db.session.add(new_contact)
            db.session.commit()
            
            logger.info(f"Successfully inserted contact '{new_contact.representative_name}' with ID: {new_contact.id}")
            return new_contact
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error inserting contact: {e}", exc_info=True)
            if 'unique constraint' in str(e).lower():
                raise DatabaseError("A contact with this email may already exist for this company.")
            raise DatabaseError(f"Failed to insert contact: {e}")

    @staticmethod
    def fetch_all_contacts() -> List[Contact]:
        """Fetch all contacts with their company information."""
        try:
            # Eagerly load the related Company object to avoid N+1 query problems
            return Contact.query.options(db.joinedload(Contact.company)).order_by(Contact.representative_name).all()
        except Exception as e:
            logger.error(f"Error fetching all contacts: {e}", exc_info=True)
            raise DatabaseError(f"Failed to fetch contacts: {e}")

    @staticmethod
    def add_contact_to_deal(deal_id: int, contact_id: int) -> Optional[DealContact]:
        """Add a contact to a deal, preventing duplicates."""
        try:
            existing = DealContact.query.filter_by(deal_id=deal_id, contact_id=contact_id).first()
            if existing:
                logger.warning(f"Contact {contact_id} is already associated with deal {deal_id}.")
                return existing

            new_association = DealContact(deal_id=deal_id, contact_id=contact_id)
            db.session.add(new_association)
            db.session.commit()
            
            logger.info(f"Successfully added contact {contact_id} to deal {deal_id}.")
            return new_association
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding contact {contact_id} to deal {deal_id}: {e}", exc_info=True)
            raise DatabaseError(f"Failed to add contact to deal: {e}")

    @staticmethod
    def update_contact(contact_id: int, updated_data: Dict) -> Optional[Contact]:
        """Update contact information."""
        try:
            contact = Contact.query.get(contact_id)
            if not contact:
                logger.warning(f"Attempted to update non-existent contact with ID {contact_id}.")
                return None

            # Validate before updating
            # Create a merged dictionary to validate the final state
            merged_data = {
                'representative_name': contact.representative_name,
                'representative_email': contact.representative_email,
                **updated_data
            }
            ContactDatabaseManager.validate_contact_data(merged_data)

            for key, value in updated_data.items():
                if hasattr(contact, key):
                    setattr(contact, key, value)
            
            db.session.commit()
            logger.info(f"Successfully updated contact with ID: {contact_id}")
            return contact
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating contact {contact_id}: {e}", exc_info=True)
            raise DatabaseError(f"Failed to update contact: {e}")

    @staticmethod
    def fetch_contact_by_id(contact_id: int) -> Optional[Contact]:
        """Fetch a specific contact by its ID."""
        try:
            # Eagerly load the related Company object
            return Contact.query.options(db.joinedload(Contact.company)).get(contact_id)
        except Exception as e:
            logger.error(f"Error fetching contact by ID {contact_id}: {e}", exc_info=True)
            raise DatabaseError(f"Failed to fetch contact: {e}")