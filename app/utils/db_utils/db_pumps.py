import sqlite3
from app.utils.db_utils.db_connection import get_db_connection



def create_pump_tables():
    """
    Creates tables related to pump details in the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table creation for GeneralPumpDetails
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS GeneralPumpDetails (
        sku TEXT PRIMARY KEY,
        name TEXT,
        poles INTEGER,
        kw REAL,
        ie_class TEXT,
        mei REAL,
        weight REAL,
        length REAL,
        width REAL,
        height REAL,
        image_path TEXT
    )
    ''')

    # Table creation for HistoricPumpData
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS HistoricPumpData (
        sku TEXT PRIMARY KEY,
        name TEXT,
        flow REAL,
        flow_unit TEXT,
        head REAL,
        head_unit TEXT,
        efficiency TEXT,
        absorbed_power TEXT,
        npsh TEXT,
        image_path TEXT
    )
    ''')

    conn.commit()
    cursor.close()
    conn.close()

def insert_general_pump_details(pump_data):
    """
    Inserts a new pump record into the GeneralPumpDetails table.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    columns = ', '.join(pump_data.keys())
    placeholders = ', '.join(['?'] * len(pump_data))
    sql = f'INSERT INTO GeneralPumpDetails ({columns}) VALUES ({placeholders})'
    cursor.execute(sql, tuple(pump_data.values()))

    conn.commit()
    cursor.close()
    conn.close()

def fetch_all_general_pumps():
    """
    Fetches all records from the GeneralPumpDetails table.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM GeneralPumpDetails")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return [dict(row) for row in data]  # Convert rows to dictionaries

def fetch_pump_by_sku(sku):
    """
    Fetches a specific pump by its SKU from the GeneralPumpDetails table.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM GeneralPumpDetails WHERE sku = ?", (sku,))
    data = cursor.fetchone()
    cursor.close()
    conn.close()
    return dict(data) if data else None  # Convert row to dictionary if exists

def update_pump_details(sku, updated_data):
    """
    Updates pump details for a specific SKU in the GeneralPumpDetails table.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    columns = ', '.join([f"{col} = ?" for col in updated_data.keys()])
    sql = f'UPDATE GeneralPumpDetails SET {columns} WHERE sku = ?'
    cursor.execute(sql, tuple(updated_data.values()) + (sku,))

    conn.commit()
    cursor.close()
    conn.close()

def fetch_historic_pump_data():
    """
    Fetches all records from the HistoricPumpData table.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM HistoricPumpData")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return [dict(row) for row in data]  # Convert rows to dictionaries

def insert_historic_pump_data(historic_data):
    """
    Inserts a new historic pump record into the HistoricPumpData table.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    columns = ', '.join(historic_data.keys())
    placeholders = ', '.join(['?'] * len(historic_data))
    sql = f'INSERT INTO HistoricPumpData ({columns}) VALUES ({placeholders})'
    cursor.execute(sql, tuple(historic_data.values()))

    conn.commit()
    cursor.close()
    conn.close()
