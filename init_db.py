import csv
from app import app, db, Member, Inventory

def init_database():
    """Initialize the database with sample data from CSV files."""
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if database already has data
        if Member.query.count() > 0 or Inventory.query.count() > 0:
            print("Database already contains data. Skipping initialization.")
            return
        
        # Load members from CSV
        try:
            with open('members.csv', 'r') as f:
                csv_reader = csv.DictReader(f)
                for row in csv_reader:
                    member = Member(
                        first_name=row.get('first_name'),
                        last_name=row.get('last_name'),
                        email=row.get('email'),
                        phone=row.get('phone')
                    )
                    db.session.add(member)
            print("Members data loaded successfully.")
        except Exception as e:
            print(f"Error loading members data: {e}")
        
        # Load inventory from CSV
        try:
            with open('inventory.csv', 'r') as f:
                csv_reader = csv.DictReader(f)
                for row in csv_reader:
                    inventory = Inventory(
                        name=row.get('name'),
                        description=row.get('description'),
                        total_count=int(row.get('total_count', 0)),
                        remaining_count=int(row.get('remaining_count', 0))
                    )
                    db.session.add(inventory)
            print("Inventory data loaded successfully.")
        except Exception as e:
            print(f"Error loading inventory data: {e}")
        
        # Commit changes
        db.session.commit()
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_database() 