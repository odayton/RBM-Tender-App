import sqlite3

def get_db_connection():
    conn = sqlite3.connect('instance/RBM_Product.db')
    conn.row_factory = sqlite3.Row
    return conn

def fetch_all_from_table(table_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def insert_into_db(table_name, data):
    conn = get_db_connection()
    columns = ', '.join(data.keys())
    placeholders = ', '.join(['?'] * len(data))
    sql = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'
    conn.execute(sql, tuple(data.values()))
    conn.commit()
    conn.close()

def record_exists(table_name, column, value):
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = f'SELECT 1 FROM {table_name} WHERE {column} = ? LIMIT 1'
    cursor.execute(sql, (value,))
    exists = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    return exists

def write_to_db(data, table_name):
    conn = sqlite3.connect('instance/RBM_Product.db')
    cursor = conn.cursor()
    placeholders = ", ".join(["?" for _ in data])
    columns = ", ".join(data.keys())
    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    cursor.execute(sql, tuple(data.values()))
    conn.commit()
    conn.close()

def update_db_from_excel(table_name, data):
    conn = sqlite3.connect('instance/RBM_Product.db')
    cursor = conn.cursor()
    columns = ", ".join([f"{col} = ?" for col in data.keys()])
    sql = f"UPDATE {table_name} SET {columns} WHERE PartNumber = ?"
    cursor.execute(sql, tuple(data.values()) + (data["PartNumber"],))
    conn.commit()
    conn.close()

def record_exists(table_name, sku, flow, head):
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = f'SELECT 1 FROM {table_name} WHERE sku = ? AND flow = ? AND head = ? LIMIT 1'
    cursor.execute(sql, (sku, flow, head))
    exists = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    return exists

# Ensure the updated schema for the tables
def create_tables():
    conn = sqlite3.connect('instance/RBM_Product.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS GeneralPumpDetails (
        sku TEXT,
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

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS HistoricPumpData (
        sku TEXT,
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

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS SmallSeismicSprings (
        PartNumber TEXT PRIMARY KEY,
        Name TEXT,
        MaxLoad_kg REAL,
        StaticDeflection REAL,
        SpringConstant_kg_mm REAL,
        Stripe1 TEXT,
        Stripe2 TEXT,
        Cost REAL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS LargeSeismicSprings (
        PartNumber TEXT PRIMARY KEY,
        Name TEXT,
        MaxLoad_kg REAL,
        StaticDeflection REAL,
        SpringConstant_kg_mm REAL,
        Inner TEXT,
        Outer TEXT,
        Cost REAL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS AdditionalPriceAdders (
        IPAdder REAL,
        DripTrayAdder REAL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS RubberMounts (
        PartNumber TEXT PRIMARY KEY,
        Name TEXT,
        Weight REAL,
        Cost REAL
    )
    ''')

    conn.commit()
    conn.close()

# Call the create_tables function to ensure tables are created
create_tables()
