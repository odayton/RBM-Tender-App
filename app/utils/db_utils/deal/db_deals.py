from app.extensions import db
from app.models import Deal

class DealManager:
    @staticmethod
    def get_all_deals():
        return db.session.query(Deal).all()

    @staticmethod
    def get_deal_by_id(deal_id):
        return db.session.query(Deal).get(deal_id)

    @staticmethod
    def create_deal(data):
        new_deal = Deal(**data)
        db.session.add(new_deal)
        db.session.commit()
        return new_deal