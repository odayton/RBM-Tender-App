from typing import Dict, List, Optional
from app.extensions import db
from app.models import Pump, HistoricPumpData # Assuming these are your model names
from app.core.core_errors import DatabaseError
from app.core.core_logging import logger # Use central app logger

class PumpDatabaseManager:
    """Handles all pump-related database operations using the SQLAlchemy ORM."""

    @staticmethod
    def upsert_pump_details(pump_data: Dict) -> Pump:
        """Insert or update general pump details using the ORM."""
        try:
            sku = pump_data.get('sku')
            if not sku:
                raise ValueError("SKU is required to upsert pump details.")

            # Check if pump exists
            pump = Pump.query.filter_by(sku=sku).first()
            
            if pump:
                # Update existing pump
                for key, value in pump_data.items():
                    if hasattr(pump, key):
                        setattr(pump, key, value)
                logger.info(f"Updating pump with SKU: {sku}")
            else:
                # Insert new pump
                pump = Pump(**pump_data)
                db.session.add(pump)
                logger.info(f"Inserting new pump with SKU: {sku}")
            
            db.session.commit()
            return pump

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error upserting pump details for SKU '{pump_data.get('sku')}': {e}", exc_info=True)
            raise DatabaseError(f"Failed to upsert pump details: {e}")

    @staticmethod
    def fetch_all_pumps() -> List[Pump]:
        """Fetch all records from general_pump_details."""
        try:
            return Pump.query.order_by(Pump.sku).all()
        except Exception as e:
            logger.error(f"Error fetching all pumps: {e}", exc_info=True)
            raise DatabaseError(f"Failed to fetch all pumps: {e}")

    @staticmethod
    def fetch_pump_by_sku(sku: str) -> Optional[Pump]:
        """Fetch a specific pump by SKU."""
        try:
            return Pump.query.filter_by(sku=sku).first()
        except Exception as e:
            logger.error(f"Error fetching pump by SKU '{sku}': {e}", exc_info=True)
            raise DatabaseError(f"Failed to fetch pump by SKU: {e}")

    @staticmethod
    def fetch_all_historic_data() -> List[HistoricPumpData]:
        """Fetch all historic pump data, joined with general details."""
        try:
            return HistoricPumpData.query.options(
                db.joinedload(HistoricPumpData.pump) # Eager load the pump details
            ).order_by(HistoricPumpData.sku).all()
        except Exception as e:
            logger.error(f"Error fetching all historic pump data: {e}", exc_info=True)
            raise DatabaseError(f"Failed to fetch historic data: {e}")

    @staticmethod
    def upsert_historic_pump_data(data: Dict) -> HistoricPumpData:
        """Insert or update historic pump data using the ORM."""
        try:
            sku = data.get('sku')
            flow = data.get('flow')
            head = data.get('head')
            if not all([sku, flow, head]):
                raise ValueError("SKU, flow, and head are required to upsert historic data.")

            # Check if historic record exists
            historic_data = HistoricPumpData.query.filter_by(sku=sku, flow=flow, head=head).first()
            
            if historic_data:
                # Update existing record
                for key, value in data.items():
                    if hasattr(historic_data, key):
                        setattr(historic_data, key, value)
                logger.info(f"Updating historic data for SKU: {sku}")
            else:
                # Insert new record
                historic_data = HistoricPumpData(**data)
                db.session.add(historic_data)
                logger.info(f"Inserting new historic data for SKU: {sku}")

            db.session.commit()
            return historic_data
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error upserting historic pump data for SKU '{data.get('sku')}': {e}", exc_info=True)
            raise DatabaseError(f"Failed to upsert historic data: {e}")