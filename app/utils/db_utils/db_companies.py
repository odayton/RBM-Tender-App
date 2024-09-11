from app.utils.db_utils.db_connection import get_db_connection

def fetch_all_companies():
    """Fetch all companies from the Companies table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Companies")
    companies = cursor.fetchall()
    cursor.close()
    conn.close()
    return companies

def insert_company(data):
    """Insert a new company into the Companies table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    columns = ', '.join(data.keys())
    placeholders = ', '.join(['?'] * len(data))
    sql = f"INSERT INTO Companies ({columns}) VALUES ({placeholders})"
    cursor.execute(sql, tuple(data.values()))
    conn.commit()
    last_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return last_id

def update_company(company_id, data):
    """Update an existing company in the Companies table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    columns = ', '.join([f"{col} = ?" for col in data.keys()])
    sql = f"UPDATE Companies SET {columns} WHERE id = ?"
    cursor.execute(sql, tuple(data.values()) + (company_id,))
    conn.commit()
    cursor.close()
    conn.close()

def company_exists(company_id):
    """Check if a company with a specific ID exists in the Companies table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = "SELECT 1 FROM Companies WHERE id = ? LIMIT 1"
    cursor.execute(sql, (company_id,))
    exists = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    return exists

def create_companies_table():
    """Create the Companies table if it does not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT,
        address TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

def add_company_to_deal(deal_id, company_id):
    """Adds a company to a deal in the DealCompanies table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = "INSERT INTO DealCompanies (deal_id, company_id) VALUES (?, ?)"
    cursor.execute(sql, (deal_id, company_id))
    conn.commit()
    cursor.close()
    conn.close()

def create_deal_companies_table():
    """Create the DealCompanies table if it does not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS DealCompanies (
        deal_id INTEGER,
        company_id INTEGER,
        FOREIGN KEY (deal_id) REFERENCES Deals(id),
        FOREIGN KEY (company_id) REFERENCES Companies(id)
    )
    ''')
    conn.commit()
    cursor.close()
    conn.close()
