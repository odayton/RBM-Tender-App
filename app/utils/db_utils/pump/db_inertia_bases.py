from app.extensions import db
from app.models import InertiaBase

class InertiaBaseManager:
    @staticmethod
    def get_all():
        """Retrieves all inertia bases."""
        return db.session.query(InertiaBase).all()

    @staticmethod
    def create(model, length, width, height):
        """Creates a new inertia base."""
        new_base = InertiaBase(model=model, length=length, width=width, height=height)
        db.session.add(new_base)
        db.session.commit()
        return new_base