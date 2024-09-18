from app.utils.db_utils.db_connection import get_db_connection

def create_inertia_bases_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS InertiaBases (
        PartNumber TEXT PRIMARY KEY,
        Length REAL,
        Width REAL,
        Height REAL,
        SpringMountHeight REAL,
        Weight REAL,
        SpringAmount INTEGER,
        Cost REAL
    )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()

def insert_inertia_base(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    sql = '''INSERT INTO InertiaBases (PartNumber, Length, Width, Height, SpringMountHeight, Weight, SpringAmount, Cost)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
    
    cursor.execute(sql, (
        data['part_number'],
        data['length'],
        data['width'],
        data['height'],
        data['spring_mount_height'],
        data['weight'],
        data['spring_amount'],
        data['cost']
    ))
    
    conn.commit()
    cursor.close()
    conn.close()

def fetch_all_inertia_bases():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM InertiaBases")
    inertia_bases = cursor.fetchall()
    cursor.close()
    conn.close()
    return inertia_bases