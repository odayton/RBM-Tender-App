from app.extensions import db
from app.models import SeismicSpring

class SeismicSpringManager:
    @staticmethod
    def get_all():
        """Retrieves all seismic springs."""
        return db.session.query(SeismicSpring).all()

    @staticmethod
    def create(model, rated_load, deflection):
        """Creates a new seismic spring."""
        new_spring = SeismicSpring(model=model, rated_load=rated_load, deflection=deflection)
        db.session.add(new_spring)
        db.session.commit()
        return new_spring