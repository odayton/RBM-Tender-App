from app.utils.db_utils.db_connection import get_db_connection

def create_seismic_springs_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS SeismicSprings (
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
    
    conn.commit()
    cursor.close()
    conn.close()

def insert_seismic_spring(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    sql = '''INSERT INTO SeismicSprings (PartNumber, Name, MaxLoad_kg, StaticDeflection, SpringConstant_kg_mm, Stripe1, Stripe2, Cost)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
    
    cursor.execute(sql, (
        data['part_number'],
        data['name'],
        data['max_load_kg'],
        data['static_deflection'],
        data['spring_constant_kg_mm'],
        data['stripe1'],
        data['stripe2'],
        data['cost']
    ))
    
    conn.commit()
    cursor.close()
    conn.close()

def fetch_all_seismic_springs():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM SeismicSprings")
    seismic_springs = cursor.fetchall()
    cursor.close()
    conn.close()
    return seismic_springs