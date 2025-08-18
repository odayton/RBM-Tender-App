from app.extensions import db
from app.models import Contact

class ContactManager:
    @staticmethod
    def get_all_contacts():
        return db.session.query(Contact).all()