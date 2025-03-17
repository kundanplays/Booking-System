import csv
import os
from app import app, db, Member, Inventory, parse_date

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
            if os.path.exists('members.csv'):
                with open('members.csv', 'r') as f:
                    csv_reader = csv.DictReader(f)
                    headers = csv_reader.fieldnames
                    
                    # Detect format type
                    if 'name' in headers and 'surname' in headers:
                        # Appendix 1 format
                        for row in csv_reader:
                            # Convert booking_count to integer or default to 0
                            booking_count = int(row.get('booking_count', 0)) if row.get('booking_count', '').strip() else 0
                            
                            member = Member(
                                first_name=row.get('name', '').strip(),
                                last_name=row.get('surname', '').strip(),
                                booking_count=booking_count,
                                date_joined=parse_date(row.get('date_joined'))
                            )
                            db.session.add(member)
                    else:
                        # Original format
                        for row in csv_reader:
                            member = Member(
                                first_name=row.get('first_name', '').strip(),
                                last_name=row.get('last_name', '').strip(),
                                email=row.get('email', '').strip(),
                                phone=row.get('phone', '').strip()
                            )
                            db.session.add(member)
                print("Members data loaded successfully.")
            else:
                print("No members.csv file found.")
        except Exception as e:
            print(f"Error loading members data: {e}")
        
        # Load inventory from CSV
        try:
            if os.path.exists('inventory.csv'):
                with open('inventory.csv', 'r') as f:
                    csv_reader = csv.DictReader(f)
                    headers = csv_reader.fieldnames
                    
                    # Detect format type
                    if 'title' in headers:
                        # Appendix 2 format
                        for row in csv_reader:
                            # For this format, we'll set total_count same as remaining_count initially
                            remaining_count = int(row.get('remaining_count', 0)) if row.get('remaining_count', '').strip() else 0
                            
                            inventory = Inventory(
                                name=row.get('title', '').strip(),
                                description=row.get('description', '').strip(),
                                remaining_count=remaining_count,
                                total_count=remaining_count,  # Setting total same as remaining for this format
                                expiration_date=parse_date(row.get('expiration_date'))
                            )
                            db.session.add(inventory)
                    else:
                        # Original format
                        for row in csv_reader:
                            inventory = Inventory(
                                name=row.get('name', '').strip(),
                                description=row.get('description', '').strip(),
                                total_count=int(row.get('total_count', 0)) if row.get('total_count', '').strip() else 0,
                                remaining_count=int(row.get('remaining_count', 0)) if row.get('remaining_count', '').strip() else 0
                            )
                            db.session.add(inventory)
                print("Inventory data loaded successfully.")
            else:
                print("No inventory.csv file found.")
        except Exception as e:
            print(f"Error loading inventory data: {e}")
        
        # Commit changes
        db.session.commit()
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_database() 