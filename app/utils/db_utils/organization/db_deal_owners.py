from app.extensions import db
from app.models import User

class DealOwnerManager:
    @staticmethod
    def get_all_deal_owners():
        return db.session.query(User).all()