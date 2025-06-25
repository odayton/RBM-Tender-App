from app.extensions import db
from app.models import RubberMount

class RubberMountManager:
    @staticmethod
    def get_all():
        """Retrieves all rubber mounts."""
        return db.session.query(RubberMount).all()

    @staticmethod
    def create(model, rated_load, deflection):
        """Creates a new rubber mount."""
        new_mount = RubberMount(model=model, rated_load=rated_load, deflection=deflection)
        db.session.add(new_mount)
        db.session.commit()
        return new_mount