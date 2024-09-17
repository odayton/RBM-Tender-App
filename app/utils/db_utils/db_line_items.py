# db_line_items.py

from app.utils.db_utils.db_connection import get_db_connection

def fetch_all_line_items():
    """Fetch all line items from the LineItems table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LineItems")
    line_items = cursor.fetchall()
    cursor.close()
    conn.close()
    return line_items

def insert_line_item(data):
    """Insert a new line item into the LineItems table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    columns = ', '.join(data.keys())
    placeholders = ', '.join(['?'] * len(data))
    sql = f"INSERT INTO LineItems ({columns}) VALUES ({placeholders})"
    cursor.execute(sql, tuple(data.values()))
    conn.commit()
    last_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return last_id

def update_line_item(item_id, data):
    """Update an existing line item in the LineItems table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    columns = ', '.join([f"{col} = ?" for col in data.keys()])
    sql = f"UPDATE LineItems SET {columns} WHERE id = ?"
    cursor.execute(sql, tuple(data.values()) + (item_id,))
    conn.commit()
    cursor.close()
    conn.close()

def line_item_exists(item_id):
    """Check if a line item with a specific ID exists in the LineItems table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = "SELECT 1 FROM LineItems WHERE id = ? LIMIT 1"
    cursor.execute(sql, (item_id,))
    exists = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    return exists

def create_line_items_table():
    """
    Create the LineItems table if it does not exist.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS LineItems (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        deal_id INTEGER,
        entity_type TEXT,
        entity_id TEXT,
        pump_name TEXT,  -- Add this field
        flow REAL,
        head REAL,
        description TEXT,
        amount REAL,
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY (deal_id) REFERENCES Deals(id)
    )
    ''')

    conn.commit()
    cursor.close()
    conn.close()


def fetch_line_items_by_deal_id(deal_id):
    """Fetch line items by deal ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LineItems WHERE deal_id = ?", (deal_id,))
    line_items = cursor.fetchall()
    cursor.close()
    conn.close()
    return [dict(item) for item in line_items]
