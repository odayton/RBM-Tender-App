from app.extensions import db
from app.models import Quote

class RevisionManager:
    @staticmethod
    def get_revisions_for_deal(deal_id):
        return db.session.query(Quote).filter_by(deal_id=deal_id).all()