import sqlite3
from app.utils.db_utils.db_connection import get_db_connection

def create_contact_tables():
    """
    Creates the Contacts table in the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table creation for Contacts
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        representative_name TEXT,
        representative_email TEXT,
        phone_number TEXT, 
        company_id INTEGER,
        FOREIGN KEY (company_id) REFERENCES Companies (id)
    )
    ''')

    conn.commit()
    cursor.close()
    conn.close()

def insert_contact(contact_data):
    """
    Inserts a new contact record into the Contacts table.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    columns = ', '.join(contact_data.keys())
    placeholders = ', '.join(['?'] * len(contact_data))
    sql = f'INSERT INTO Contacts ({columns}) VALUES ({placeholders})'
    cursor.execute(sql, tuple(contact_data.values()))

    conn.commit()
    cursor.close()
    conn.close()

def fetch_all_contacts():
    """
    Fetches all records from the Contacts table.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Contacts")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def fetch_contact_by_id(contact_id):
    """
    Fetches a specific contact by its ID from the Contacts table.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Contacts WHERE id = ?", (contact_id,))
    data = cursor.fetchone()
    cursor.close()
    conn.close()
    return data

def update_contact(contact_id, updated_data):
    """
    Updates contact details for a specific contact ID in the Contacts table.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    columns = ', '.join([f"{col} = ?" for col in updated_data.keys()])
    sql = f'UPDATE Contacts SET {columns} WHERE id = ?'
    cursor.execute(sql, tuple(updated_data.values()) + (contact_id,))

    conn.commit()
    cursor.close()
    conn.close()

def add_contact_to_deal(deal_id, contact_id):
    """
    Adds a contact to a specific deal by inserting a record into the DealContacts table.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = "INSERT INTO DealContacts (deal_id, contact_id) VALUES (?, ?)"
    cursor.execute(sql, (deal_id, contact_id))

    conn.commit()
    cursor.close()
    conn.close()
