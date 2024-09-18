import sqlite3
import logging

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
    cursor = conn.cursor()
    columns = ', '.join(data.keys())
    placeholders = ', '.join(['?'] * len(data))
    sql = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'
    cursor.execute(sql, tuple(data.values()))
    conn.commit()
    last_id = cursor.lastrowid
    cursor.close()
    conn.close()
    logging.info(f"Inserted into {table_name}: {data}")
    return last_id

def record_exists(table_name, conditions):
    conn = get_db_connection()
    cursor = conn.cursor()
    conditions_str = ' AND '.join([f"{col} = ?" for col in conditions.keys()])
    sql = f'SELECT COUNT(*) FROM {table_name} WHERE {conditions_str}'
    cursor.execute(sql, tuple(conditions.values()))
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    logging.info(f"Checked existence in {table_name}: {conditions}, Result: {count > 0}")
    return count > 0

def create_table(sql):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()