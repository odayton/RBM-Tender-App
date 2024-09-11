# app/utils/db_utils/db_deal_owners.py

from app.utils.db_utils.db_connection import get_db_connection

def insert_deal_owner(owner_data):
    """
    Inserts a new deal owner record into the DealOwners table.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    columns = ', '.join(owner_data.keys())
    placeholders = ', '.join(['?'] * len(owner_data))
    sql = f'INSERT INTO DealOwners ({columns}) VALUES ({placeholders})'
    cursor.execute(sql, tuple(owner_data.values()))

    conn.commit()
    cursor.close()
    conn.close()

def fetch_all_deal_owners():
    """
    Fetches all deal owners from the DealOwners table.
    Returns a list of deal owners.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, owner_name FROM DealOwners')
    deal_owners = cursor.fetchall()
    cursor.close()
    conn.close()
    return deal_owners
