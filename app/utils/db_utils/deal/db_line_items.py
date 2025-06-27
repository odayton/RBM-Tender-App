from app.extensions import db
from app.models import QuoteLineItem

class LineItemManager:
    @staticmethod
    def add_line_item(quote_id, data):
        new_item = QuoteLineItem(quote_id=quote_id, **data)
        db.session.add(new_item)
        db.session.commit()
        return new_item