import sqlite3

def get_db_connection():
    conn = sqlite3.connect('instance/RBM_Product.db')
    conn.row_factory = sqlite3.Row
    return conn

def fetch_historic_with_general():
    conn = get_db_connection()
    query = '''
    SELECT h.sku, h.name, h.flow, h.flow_unit, h.head, h.head_unit, g.kw, g.poles, h.efficiency, h.absorbed_power, h.npsh 
    FROM HistoricPumpData h
    LEFT JOIN GeneralPumpDetails g ON h.sku = g.sku
    '''
    rows = conn.execute(query).fetchall()
    conn.close()
    return rows
