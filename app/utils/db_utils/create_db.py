import sqlite3
from app.utils.db_utils.db_connection import get_db_connection
from app.utils.db_utils.db_additional_price_adders import create_additional_price_adders_table
from app.utils.db_utils.db_companies import create_companies_table, create_deal_companies_table
from app.utils.db_utils.db_contacts import create_contact_tables
from app.utils.db_utils.db_deals import create_deals_table, create_revisions_table
from app.utils.db_utils.db_inertia_bases import create_inertia_bases_table
from app.utils.db_utils.db_line_items import create_line_items_table
from app.utils.db_utils.db_pumps import create_pump_tables
from app.utils.db_utils.db_rubber_mounts import create_rubber_mounts_table
from app.utils.db_utils.db_seismic_springs import create_seismic_springs_table
from app.utils.db_utils.db_deal_owners import create_deal_owners_table

def create_database():
    conn = get_db_connection()
    conn.close()
    print("Database created successfully.")

def create_all_tables():
    create_additional_price_adders_table()
    create_companies_table()
    create_deal_companies_table()
    create_contact_tables()
    create_deals_table()
    create_revisions_table()
    create_inertia_bases_table()
    create_line_items_table()
    create_pump_tables()
    create_rubber_mounts_table()
    create_seismic_springs_table()
    create_deal_owners_table()

    print("All tables created successfully.")

if __name__ == "__main__":
    create_database()
    create_all_tables()