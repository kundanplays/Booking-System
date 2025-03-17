# Booking System

A Flask web application for managing inventory bookings.

## Features

- Upload member data via CSV (supports multiple formats)
- Upload inventory data via CSV (supports multiple formats)
- Book inventory items for members
- Cancel bookings
- Track booking history
- Enforce booking limits (maximum 2 active bookings per member)
- Track inventory availability and expiration dates
- Admin panel for system management with bulk operations

## Requirements

- Python 3.7 or higher
- Flask
- Flask-SQLAlchemy
- Werkzeug

## Installation

1. Clone the repository
   ```
   git clone https://github.com/kundanplays/Booking-System.git
   cd Booking-System
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

1. Initialize the database with sample data (optional)
   ```
   python init_db.py
   ```

2. Start the Flask development server
   ```
   python app.py
   ```

3. Open your browser and navigate to http://127.0.0.1:8080/

## CSV Data Format

The application accepts multiple CSV formats:

### Members CSV

#### Format 1 (Original)
```
first_name,last_name,email,phone
John,Doe,john.doe@example.com,123-456-7890
Jane,Smith,jane.smith@example.com,098-765-4321
```

#### Format 2 (Appendix 1)
```
name,surname,booking_count,date_joined
Sophie,Davis,1,2024-01-02T12:10:11
Emily,Johnson,0,2024-11-12T12:10:12
```

### Inventory CSV

#### Format 1 (Original)
```
name,description,total_count,remaining_count
Concert Tickets,VIP access to annual concert,100,100
Cooking Class,Gourmet cooking class with Chef Alex,20,20
```

#### Format 2 (Appendix 2)
```
title,description,remaining_count,expiration_date
Bali,Beautiful vacation package,5,19/11/2030
Madeira,Island getaway,4,20/11/2030
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
- **GET /admin** - Admin panel for system management

### API Examples

#### Book an Item

```bash
curl -X POST http://127.0.0.1:8080/book \
  -H "Content-Type: application/json" \
  -d '{"member_id": 1, "inventory_id": 1}'
```

#### Cancel a Booking

```bash
curl -X POST http://127.0.0.1:8080/cancel \
  -H "Content-Type: application/json" \
  -d '{"booking_reference": "UUID_REFERENCE_HERE"}'
```

## Database

The application uses SQLite for simplicity. The database file is created automatically when you run the application.

## License

MIT
