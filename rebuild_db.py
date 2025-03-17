import sqlite3
from datetime import datetime, date
import os

def rebuild_database():
    """Rebuild the database with explicit SQL."""
    # Remove existing database if it exists
    if os.path.exists('booking.db'):
        os.remove('booking.db')
        print("Removed existing database.")
    
    # Create a new database
    conn = sqlite3.connect('booking.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
    CREATE TABLE member (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        booking_count INTEGER DEFAULT 0,
        date_joined TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        total_count INTEGER DEFAULT 0,
        remaining_count INTEGER DEFAULT 0,
        expiration_date DATE
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE booking (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_reference TEXT NOT NULL UNIQUE,
        booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        member_id INTEGER NOT NULL,
        inventory_id INTEGER NOT NULL,
        is_active BOOLEAN DEFAULT 1,
        FOREIGN KEY (member_id) REFERENCES member (id),
        FOREIGN KEY (inventory_id) REFERENCES inventory (id)
    )
    ''')
    
    # Insert sample data
    # Members
    members = [
        ('John', 'Doe', 'john.doe@example.com', '123-456-7890', 0, None),
        ('Jane', 'Smith', 'jane.smith@example.com', '987-654-3210', 0, None),
        ('Sophie', 'Davis', None, None, 1, '2024-01-02 12:10:11'),
        ('Emily', 'Johnson', None, None, 0, '2024-11-12 12:10:12'),
        ('Jessica', 'Rodriguez', None, None, 1, '2024-01-02 12:10:13')
    ]
    
    cursor.executemany('''
    INSERT INTO member (first_name, last_name, email, phone, booking_count, date_joined)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', members)
    
    # Inventory
    inventory_items = [
        ('Concert Tickets', 'VIP access to annual concert', 100, 100, None),
        ('Cooking Class', 'Gourmet cooking class with Chef Alex', 20, 20, None),
        ('Bali', 'Suspendisse congue erat ac ex venenatis mattis.', 5, 5, '2030-11-19'),
        ('Paris Trip', 'Pellentesque non aliquam eros quis posuere leo', 3, 3, '2030-11-21'),
        ('Hot Air Balloon', 'Etiam molestie sem id luctus facilisis', 1, 1, '2021-11-23')
    ]
    
    cursor.executemany('''
    INSERT INTO inventory (name, description, total_count, remaining_count, expiration_date)
    VALUES (?, ?, ?, ?, ?)
    ''', inventory_items)
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("Database rebuilt successfully with sample data!")

if __name__ == "__main__":
    rebuild_database() 