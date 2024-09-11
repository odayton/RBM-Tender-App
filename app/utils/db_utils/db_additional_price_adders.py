import sqlite3
from app.utils.db_utils.db_connection import get_db_connection


def create_additional_price_adders_table():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table creation for AdditionalPriceAdders
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS AdditionalPriceAdders (
        IPAdder REAL,
        DripTrayAdder REAL
    )
    ''')

    conn.commit()
    conn.close()

# Initialize table
create_additional_price_adders_table()
