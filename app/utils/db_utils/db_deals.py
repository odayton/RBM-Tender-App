from app.utils.db_utils.db_connection import get_db_connection
from datetime import datetime

# Deal-related functions

def fetch_all_deals():
    """Fetch all deals from the Deals table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Deals")
    deals = cursor.fetchall()
    cursor.close()
    conn.close()
    return deals

def insert_deal(data):
    """Insert a new deal into the Deals table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    columns = ', '.join(data.keys())
    placeholders = ', '.join(['?'] * len(data))
    sql = f"INSERT INTO Deals ({columns}) VALUES ({placeholders})"
    cursor.execute(sql, tuple(data.values()))
    conn.commit()
    last_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return last_id

def update_deal(deal_id, data):
    """Update an existing deal in the Deals table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    columns = ', '.join([f"{col} = ?" for col in data.keys()])
    sql = f"UPDATE Deals SET {columns} WHERE id = ?"
    cursor.execute(sql, tuple(data.values()) + (deal_id,))
    conn.commit()
    cursor.close()
    conn.close()

def update_deal_stage_in_db(deal_id, new_stage):
    """Update the stage of a deal in the Deals table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = "UPDATE Deals SET stage = ?, updated_at = ? WHERE id = ?"
    cursor.execute(sql, (new_stage, datetime.now(), deal_id))
    conn.commit()
    cursor.close()
    conn.close()

def fetch_deal_by_id(deal_id):
    """Fetch a specific deal by its ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Deals WHERE id = ?", (deal_id,))
    deal = cursor.fetchone()
    cursor.close()
    conn.close()
    return deal

def deal_exists(deal_id):
    """Check if a deal with a specific ID exists in the Deals table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = "SELECT 1 FROM Deals WHERE id = ? LIMIT 1"
    cursor.execute(sql, (deal_id,))
    exists = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    return exists

def create_deals_table():
    """Create the Deals table if it does not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Deals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        stage TEXT,
        type TEXT,
        location TEXT,
        close_date TEXT,
        owner TEXT,
        contact_id INTEGER,
        company_id INTEGER,
        created_at TEXT,
        updated_at TEXT,
        amount REAL DEFAULT 0.0,
        FOREIGN KEY (contact_id) REFERENCES Contacts(id),
        FOREIGN KEY (company_id) REFERENCES Companies(id)
    )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

# Revision-related functions

def create_revisions_table():
    """Create the Revisions table if it does not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Revisions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        deal_id INTEGER,
        version TEXT,
        description TEXT,
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY (deal_id) REFERENCES Deals(id)
    )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

def fetch_revisions_by_deal_id(deal_id):
    """Fetch all revisions for a specific deal by deal ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Revisions WHERE deal_id = ?", (deal_id,))
    revisions = cursor.fetchall()
    cursor.close()
    conn.close()
    return revisions


def insert_revision(deal_id, version, description):
    """Insert a new revision into the Revisions table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Revisions (deal_id, version, description, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (deal_id, version, description, datetime.now(), datetime.now()))
    conn.commit()
    last_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return last_id

def update_revision(revision_id, data):
    """Update an existing revision in the Revisions table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    columns = ', '.join([f"{col} = ?" for col in data.keys()])
    sql = f"UPDATE Revisions SET {columns}, updated_at = ? WHERE id = ?"
    cursor.execute(sql, tuple(data.values()) + (datetime.now(), revision_id))
    conn.commit()
    cursor.close()
    conn.close()

def fetch_revision_by_id(revision_id):
    """Fetch a specific revision by its ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Revisions WHERE id = ?", (revision_id,))
    revision = cursor.fetchone()
    cursor.close()
    conn.close()
    return revision

# Automatically create tables when this module is imported
create_deals_table()
create_revisions_table()
