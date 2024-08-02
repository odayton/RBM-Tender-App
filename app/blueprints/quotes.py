from flask import Blueprint, render_template
from datetime import datetime, timedelta

quotes_bp = Blueprint('quotes', __name__)

@quotes_bp.route('/quotes')
def view_quotes():
    data = {
        'total_deal_amount': 0,  # Example static data
        'avg_deal_amount': 0,    # Example static data
        'quotes_mtd': 0,         # Example static data
        'quotes_last_month': 0,  # Example static data
        'avg_deal_age': 0,       # Example static data
        'current_date': datetime.now(),
        'timedelta': timedelta
    }
    return render_template('quote/quotes.html', **data)
