import sqlite3
from utils.db_utils.db_connection import get_db_connection

def create_inertia_bases_table():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table creation for InertiaBases
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS InertiaBases (
        PartNumber TEXT PRIMARY KEY,
        Name TEXT,
        Length REAL,
        Width REAL,
        Height REAL,
        Weight REAL,
        SpringMountHeight REAL,
        SpringQty INTEGER,
        SpringLoad REAL,
        Cost REAL
    )
    ''')

    conn.commit()
    conn.close()

# Initialize table
create_inertia_bases_table()
