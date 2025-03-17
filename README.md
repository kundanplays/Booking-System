# Booking System

A Flask web application for managing inventory bookings.

## Features

- Upload member data via CSV
- Upload inventory data via CSV
- Book inventory items for members
- Cancel bookings
- Track booking history
- Enforce booking limits (maximum 2 active bookings per member)
- Track inventory availability

## Requirements

- Python 3.7 or higher
- Flask
- Flask-SQLAlchemy
- Werkzeug

## Installation

1. Clone the repository
   ```
   git clone https://github.com/yourusername/booking-system.git
   cd booking-system
   ```

2. Create a virtual environment (optional but recommended)
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```
   pip install -r requirements.txt
   ```

## Running the Application

1. Start the Flask development server
   ```
   python app.py
   ```

2. Open your browser and navigate to http://127.0.0.1:5000/

## CSV Data Format

The application accepts two types of CSV files:

### Members CSV (members.csv)

```
first_name,last_name,email,phone
John,Doe,john.doe@example.com,123-456-7890
Jane,Smith,jane.smith@example.com,098-765-4321
```

### Inventory CSV (inventory.csv)

```
name,description,total_count,remaining_count
Concert Tickets,VIP access to annual concert,100,100
Cooking Class,Gourmet cooking class with Chef Alex,20,20
```

## API Endpoints

- **GET /** - Home page
- **GET /upload** - Upload CSV form
- **POST /upload** - Process CSV upload
- **POST /book** - Book an inventory item for a member
- **POST /cancel** - Cancel a booking
- **GET /api/members** - Get all members
- **GET /api/inventory** - Get all inventory items
- **GET /api/bookings** - Get all bookings

### API Examples

#### Book an Item

```bash
curl -X POST http://127.0.0.1:5000/book \
  -H "Content-Type: application/json" \
  -d '{"member_id": 1, "inventory_id": 1}'
```

#### Cancel a Booking

```bash
curl -X POST http://127.0.0.1:5000/cancel \
  -H "Content-Type: application/json" \
  -d '{"booking_reference": "UUID_REFERENCE_HERE"}'
```

## Database

The application uses SQLite for simplicity. The database file is created automatically when you run the application.

## License

MIT