import csv
from app import app, db, Member, Inventory, parse_date

def load_sample_data():
    """Load sample data directly into the database."""
    with app.app_context():
        print("Loading sample members data...")
        # Load sample members
        members = [
            Member(first_name="John", last_name="Doe", email="john.doe@example.com", phone="123-456-7890"),
            Member(first_name="Jane", last_name="Smith", email="jane.smith@example.com", phone="987-654-3210"),
            Member(first_name="Sophie", last_name="Davis", booking_count=1, date_joined=parse_date("2024-01-02T12:10:11")),
            Member(first_name="Emily", last_name="Johnson", booking_count=0, date_joined=parse_date("2024-11-12T12:10:12")),
            Member(first_name="Jessica", last_name="Rodriguez", booking_count=1, date_joined=parse_date("2024-01-02T12:10:13"))
        ]
        
        for member in members:
            db.session.add(member)
        
        print("Loading sample inventory data...")
        # Load sample inventory
        inventory_items = [
            Inventory(
                name="Concert Tickets",
                description="VIP access to annual concert",
                total_count=100,
                remaining_count=100
            ),
            Inventory(
                name="Cooking Class",
                description="Gourmet cooking class with Chef Alex",
                total_count=20,
                remaining_count=20
            ),
            Inventory(
                name="Bali",
                description="Suspendisse congue erat ac ex venenatis mattis.",
                total_count=5,
                remaining_count=5,
                expiration_date=parse_date("19/11/2030")
            ),
            Inventory(
                name="Paris Trip",
                description="Pellentesque non aliquam eros quis posuere leo",
                total_count=3,
                remaining_count=3,
                expiration_date=parse_date("21/11/2030")
            ),
            Inventory(
                name="Hot Air Balloon",
                description="Etiam molestie sem id luctus facilisis",
                total_count=1,
                remaining_count=1,
                expiration_date=parse_date("23/11/2021")  # Expired item
            )
        ]
        
        for item in inventory_items:
            db.session.add(item)
        
        # Commit to database
        db.session.commit()
        print("Sample data loaded successfully!")

if __name__ == "__main__":
    load_sample_data() 