from app import app, db, Member, Inventory
import sqlite3

def get_table_schema(table_name):
    """Get the schema of a table directly from SQLite."""
    with sqlite3.connect('booking.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print(f"\nTable '{table_name}' schema:")
        for column in columns:
            print(f"  {column[1]} ({column[2]})")

def inspect_database():
    """Inspect the database schema."""
    with app.app_context():
        # Get tables from SQLAlchemy metadata
        tables = db.metadata.tables
        print("Tables in database:")
        for table_name in tables.keys():
            print(f" - {table_name}")
        
        # Inspect specific tables
        get_table_schema('member')
        get_table_schema('inventory')
        get_table_schema('booking')

if __name__ == "__main__":
    inspect_database() 