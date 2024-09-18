from app.utils.db_utils.db_connection import get_db_connection

def create_rubber_mounts_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS RubberMounts (
        PartNumber TEXT PRIMARY KEY,
        Name TEXT,
        Weight REAL,
        Cost REAL
    )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()

def insert_rubber_mount(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    sql = '''INSERT INTO RubberMounts (PartNumber, Name, Weight, Cost)
             VALUES (?, ?, ?, ?)'''
    
    cursor.execute(sql, (
        data['part_number'],
        data['name'],
        data['weight'],
        data['cost']
    ))
    
    conn.commit()
    cursor.close()
    conn.close()

def fetch_all_rubber_mounts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM RubberMounts")
    rubber_mounts = cursor.fetchall()
    cursor.close()
    conn.close()
    return rubber_mounts