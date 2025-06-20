from typing import Dict, List, Optional
from app.extensions import db # Corrected Import
from app.models import Deal, Quote, QuoteLineItem, DealStage
from app.core.core_errors import DatabaseError
from app.core.core_logging import logger

class DealDatabaseManager:
    """Manages all deal-related database operations using the SQLAlchemy ORM."""

    @staticmethod
    def create_deal(data: Dict) -> Deal:
        """
        Creates a new Deal record in the database from a dictionary of data.
        Args:
            data: A dictionary containing the deal attributes.
        Returns:
            The newly created Deal object.
        """
        try:
            new_deal = Deal(**data)
            db.session.add(new_deal)
            db.session.commit()
            logger.info(f"Successfully created deal: {new_deal.project_name} (ID: {new_deal.id})")
            return new_deal
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating deal: {e}", exc_info=True)
            raise DatabaseError(f"Failed to create deal: {e}")

    @staticmethod
    def get_deal_by_id(deal_id: int) -> Optional[Deal]:
        """
        Fetches a single deal by its primary key.
        Args:
            deal_id: The ID of the deal to retrieve.
        Returns:
            The Deal object if found, otherwise None.
        """
        try:
            return Deal.query.get(deal_id)
        except Exception as e:
            logger.error(f"Error fetching deal with id {deal_id}: {e}", exc_info=True)
            raise DatabaseError(f"Failed to fetch deal: {e}")

    @staticmethod
    def get_all_deals() -> List[Deal]:
        """
        Fetches all deals, ordered by creation date.
        Returns:
            A list of all Deal objects.
        """
        try:
            return Deal.query.order_by(Deal.created_date.desc()).all()
        except Exception as e:
            logger.error(f"Error fetching all deals: {e}", exc_info=True)
            raise DatabaseError(f"Failed to fetch deals: {e}")

    @staticmethod
    def update_deal_stage(deal_id: int, new_stage: DealStage) -> Optional[Deal]:
        """
        Updates the stage of a specific deal.
        Args:
            deal_id: The ID of the deal to update.
            new_stage: The new DealStage enum value.
        Returns:
            The updated Deal object.
        """
        try:
            deal = Deal.query.get(deal_id)
            if deal:
                deal.stage = new_stage
                db.session.commit()
                logger.info(f"Successfully updated stage for deal {deal_id} to {new_stage.value}")
                return deal
            logger.warning(f"Attempted to update stage for non-existent deal with ID {deal_id}")
            return None
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating deal stage for deal {deal_id}: {e}", exc_info=True)
            raise DatabaseError(f"Failed to update deal stage: {e}")

    @staticmethod
    def create_quote_for_deal(deal_id: int, quote_data: Dict) -> Quote:
        """Creates a new Quote and associates it with a Deal."""
        try:
            quote_data['deal_id'] = deal_id
            new_quote = Quote(**quote_data)
            db.session.add(new_quote)
            db.session.commit()
            logger.info(f"Successfully created quote for deal {deal_id}")
            return new_quote
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating quote for deal {deal_id}: {e}", exc_info=True)
            raise DatabaseError(f"Failed to create quote: {e}")