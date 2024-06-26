import sqlite3
import pandas as pd
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Get a connection to the SQLite database."""
    conn = sqlite3.connect('instance/RBM_Product.db')
    return conn

def create_tables():
    """Create necessary database tables for the application."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.executescript('''
    CREATE TABLE IF NOT EXISTS PumpDetails (
        SKU TEXT PRIMARY KEY,
        Name TEXT NOT NULL,
        Flow_Ls REAL,
        Head_kPa REAL,
        Head_m REAL,
        Poles TEXT,
        kW REAL,
        IE_Class TEXT,
        MEI REAL,
        Absorbed_Power REAL,
        NPSH REAL,
        Efficiency REAL,
        Weight REAL,
        Length REAL,
        Width REAL,
        Height REAL,
        Cost REAL
    );

    CREATE TABLE IF NOT EXISTS InertiaBases (
        PartNumber TEXT PRIMARY KEY,
        Name TEXT NOT NULL,
        Length REAL,
        Width REAL,
        Height REAL,
        SpringMountHeight REAL,
        SpringType TEXT,
        Weight REAL,
        SpringQty INTEGER,
        SpringLoad REAL,
        Cost REAL
    );

    CREATE TABLE IF NOT EXISTS SeismicSprings (
        PartNumber TEXT PRIMARY KEY,
        Name TEXT NOT NULL,
        MaxLoad_kg REAL,
        StaticDeflection REAL,
        SpringConstant_kgmm REAL,
        Inner REAL,
        Outer REAL,
        Cost REAL
    );

    CREATE TABLE IF NOT EXISTS Customers (
        Email TEXT PRIMARY KEY,
        Name TEXT NOT NULL,
        Company TEXT NOT NULL,
        Position TEXT
    );

    CREATE TABLE IF NOT EXISTS Quotes (
        QuoteID INTEGER PRIMARY KEY AUTOINCREMENT,
        Project TEXT NOT NULL,
        Customer TEXT NOT NULL,
        ProjectLocation TEXT,
        Company TEXT,
        Description TEXT,
        Quantity INTEGER,
        Cost REAL,
        FOREIGN KEY (Customer) REFERENCES Customers(Email)
    );

    CREATE TABLE IF NOT EXISTS QuoteItems (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        QuoteID INTEGER NOT NULL,
        PumpID TEXT NOT NULL,
        UnitPrice REAL NOT NULL,
        FOREIGN KEY (QuoteID) REFERENCES Quotes(QuoteID) ON DELETE CASCADE,
        FOREIGN KEY (PumpID) REFERENCES PumpDetails(SKU)
    );
    ''')

    conn.commit()
    conn.close()
    logger.info("Database tables created successfully.")

def fetch_all_from_table(table_name):
    """Fetch all rows from a specified table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM {table_name}')
    columns = [description[0] for description in cursor.description]
    rows = cursor.fetchall()
    conn.close()
    return {'columns': columns, 'rows': rows}

def insert_into_db(table, data):
    """Insert a new row into a specified table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    columns = ', '.join(data.keys())
    placeholders = ', '.join('?' * len(data))
    sql = f'INSERT INTO {table} ({columns}) VALUES ({placeholders})'
    cursor.execute(sql, list(data.values()))

    conn.commit()
    conn.close()
    logger.info(f"Inserted data into {table}: {data}")

def update_db_from_excel(filepath):
    """Update the database using an Excel file."""
    conn = get_db_connection()
    
    # Read the Excel file
    df = pd.read_excel(filepath, sheet_name=None)

    for sheet_name, data in df.items():
        data.to_sql(sheet_name, conn, if_exists='append', index=False)

    conn.commit()
    conn.close()
    logger.info(f"Database updated from Excel file: {filepath}")

def write_to_db(pump_info):
    """Write or update pump information in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if an entry with the specified SKU already exists
    cursor.execute("SELECT * FROM PumpDetails WHERE SKU = ?", (pump_info['sku'],))
    existing_entry = cursor.fetchone()

    if existing_entry:
        # Update the existing pump details
        cursor.execute('''
            UPDATE PumpDetails SET 
            Name = ?, Flow_Ls = ?, Head_kPa = ?, Head_m = ?, Poles = ?, kW = ?, 
            IE_Class = ?, MEI = ?, Absorbed_Power = ?, NPSH = ?, Efficiency = ?, 
            Weight = ?, Length = ?, Width = ?, Height = ?, Cost = ?
            WHERE SKU = ?
        ''', (
            pump_info['name'], pump_info['flow_ls'], pump_info['head_kpa'], pump_info['head_m'], 
            pump_info['poles'], pump_info['kw'], pump_info['ie_class'], pump_info['mei'], 
            pump_info['absorbed_power'], pump_info['npsh'], pump_info['efficiency'], 
            pump_info['weight'], pump_info['length'], pump_info['width'], pump_info['height'], 
            pump_info['cost'], pump_info['sku']
        ))
        logger.info(f"Updated existing entry in PumpDetails: {pump_info['sku']}")
    else:
        # Insert new pump details
        cursor.execute('''
            INSERT INTO PumpDetails 
            (SKU, Name, Flow_Ls, Head_kPa, Head_m, Poles, kW, IE_Class, MEI, Absorbed_Power, 
            NPSH, Efficiency, Weight, Length, Width, Height, Cost)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            pump_info['sku'], pump_info['name'], pump_info['flow_ls'], pump_info['head_kpa'], 
            pump_info['head_m'], pump_info['poles'], pump_info['kw'], pump_info['ie_class'], 
            pump_info['mei'], pump_info['absorbed_power'], pump_info['npsh'], pump_info['efficiency'], 
            pump_info['weight'], pump_info['length'], pump_info['width'], pump_info['height'], 
            pump_info['cost']
        ))
        logger.info(f"Inserted new entry into PumpDetails: {pump_info['sku']}")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_tables()
