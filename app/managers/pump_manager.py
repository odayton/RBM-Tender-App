# app/managers/pump_manager.py

from typing import List, Optional
from app.app_extensions import db
from app.models import Pump, PumpAssembly

class PumpManager:
    """Manages all pump-related database operations using the SQLAlchemy ORM."""

    @staticmethod
    def search_pumps(flow_rate: float, head: float) -> List[Pump]:
        """Finds pumps that match the given flow and head requirements within a tolerance."""
        # A 10% tolerance is applied to the search
        tolerance = 0.1
        pumps = Pump.query.filter(
            Pump.flow_rate >= flow_rate * (1 - tolerance),
            Pump.flow_rate <= flow_rate * (1 + tolerance),
            Pump.head >= head * (1 - tolerance),
            Pump.head <= head * (1 + tolerance)
        ).all()
        return pumps

    @staticmethod
    def get_historic_pumps() -> List[Pump]:
        """Fetches all pumps that have been used in an assembly."""
        # This query finds all pumps that have at least one entry in the pump_assemblies table
        return Pump.query.join(PumpAssembly).all()

    @staticmethod
    def get_pump_by_id(pump_id: int) -> Optional[Pump]:
        """Fetches a single pump by its primary key."""
        return Pump.query.get(pump_id)

    @staticmethod
    def update_pump(pump: Pump, data: dict) -> Pump:
        """Updates a pump's attributes from a dictionary."""
        for key, value in data.items():
            if hasattr(pump, key):
                setattr(pump, key, value)
        db.session.commit()
        return pump