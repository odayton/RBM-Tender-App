from app.utils.db_utils.db_connection import get_db_connection

def create_additional_price_adders_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS AdditionalPriceAdders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL
    )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()

def insert_additional_price_adder(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    sql = '''INSERT INTO AdditionalPriceAdders (name, price)
             VALUES (?, ?)'''
    
    cursor.execute(sql, (data['name'], data['price']))
    
    conn.commit()
    cursor.close()
    conn.close()

def fetch_all_additional_price_adders():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM AdditionalPriceAdders")
    adders = cursor.fetchall()
    cursor.close()
    conn.close()
    return adders