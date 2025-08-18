from app.extensions import db
from app.models import Pump
from sqlalchemy.orm import joinedload
from sqlalchemy import func

class PumpDatabaseManager:
    @staticmethod
    def get_pump_by_id(pump_id):
        """Retrieves a single pump by its ID, eagerly loading related data."""
        return db.session.query(Pump).options(
            joinedload(Pump.assemblies)
        ).filter(Pump.id == pump_id).first()

    @staticmethod
    def get_all_pumps():
        """Retrieves all pumps from the database."""
        return db.session.query(Pump).all()

    @staticmethod
    def search_pumps(search_query):
        """
        Searches for pumps by model name.
        The query is case-insensitive.
        """
        if not search_query:
            return []
            
        search_filter = func.lower(Pump.pump_model).contains(func.lower(search_query))
        
        return db.session.query(Pump).filter(search_filter).all()

    @staticmethod
    def update_pump(pump_id, update_data):
        """
        Updates a pump's details in the database.
        """
        pump = db.session.query(Pump).get(pump_id)
        if pump:
            for key, value in update_data.items():
                setattr(pump, key, value)
            db.session.commit()
            return pump
        return None