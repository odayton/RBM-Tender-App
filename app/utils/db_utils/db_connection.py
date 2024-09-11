# db_connection.py

import sqlite3

def get_db_connection():
    """
    Establishes and returns a database connection.
    Sets the row factory to sqlite3.Row for dict-like access to columns.
    """
    conn = sqlite3.connect('instance/RBM_Product.db')
    conn.row_factory = sqlite3.Row
    return conn

def fetch_all_from_table(table_name):
    """
    Fetches all records from a given table.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def insert_into_db(table_name, data):
    """
    Inserts a new record into a specified table.
    """
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
    return last_id

def record_exists(table_name, column, value):
    """
    Checks if a record exists in the specified table based on column and value.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = f'SELECT 1 FROM {table_name} WHERE {column} = ? LIMIT 1'
    cursor.execute(sql, (value,))
    exists = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    return exists

def create_table(sql):
    """
    General purpose function to create a table based on provided SQL.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()
