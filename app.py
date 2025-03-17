from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import csv
import os
from datetime import datetime, date
import uuid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///booking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'some_secret_key'
MAX_BOOKINGS = 2

db = SQLAlchemy(app)

# Add context processors for templates
@app.context_processor
def utility_processor():
    return {
        'now': datetime.now,
        'MAX_BOOKINGS': MAX_BOOKINGS
    }

# Models
class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    booking_count = db.Column(db.Integer, default=0)
    date_joined = db.Column(db.DateTime)
    bookings = db.relationship('Booking', backref='member', lazy=True)

    def __repr__(self):
        return f"<Member {self.first_name} {self.last_name}>"

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    total_count = db.Column(db.Integer, default=0)
    remaining_count = db.Column(db.Integer, default=0)
    expiration_date = db.Column(db.Date)
    bookings = db.relationship('Booking', backref='inventory', lazy=True)

    def __repr__(self):
        return f"<Inventory {self.name}>"

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_reference = db.Column(db.String(36), unique=True, nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<Booking {self.booking_reference}>"

# Helper functions
def parse_date(date_str):
    """Parse date from various formats"""
    if not date_str:
        return None
    
    # Try ISO format (2024-01-02T12:10:11)
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except ValueError:
        pass
    
    # Try DD/MM/YYYY format
    try:
        day, month, year = date_str.split('/')
        return date(int(year), int(month), int(day))
    except (ValueError, TypeError):
        pass
    
    return None

# Routes
@app.route('/')
def index():
    members = Member.query.all()
    inventory = Inventory.query.all()
    bookings = Booking.query.all()
    return render_template('index.html', members=members, inventory=inventory, bookings=bookings)

@app.route('/upload', methods=['GET', 'POST'])
def upload_csv():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file:
            flash('No file selected', 'error')
            return redirect(url_for('index'))
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process the file based on its name
        if 'member' in filename.lower():
            with open(filepath, 'r') as f:
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
            
            db.session.commit()
            flash('Members data uploaded successfully', 'success')
        
        elif 'inventory' in filename.lower():
            with open(filepath, 'r') as f:
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
            
            db.session.commit()
            flash('Inventory data uploaded successfully', 'success')
        
        return redirect(url_for('index'))
    
    return render_template('upload.html')

@app.route('/book', methods=['POST'])
def book_item():
    data = request.get_json()
    member_id = data.get('member_id')
    inventory_id = data.get('inventory_id')
    
    if not member_id or not inventory_id:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    member = Member.query.get(member_id)
    inventory = Inventory.query.get(inventory_id)
    
    if not member or not inventory:
        return jsonify({'error': 'Member or inventory not found'}), 404
    
    # Check if member has reached booking limit
    active_bookings = Booking.query.filter_by(member_id=member_id, is_active=True).count()
    if active_bookings >= MAX_BOOKINGS:
        return jsonify({'error': f'Member has reached maximum booking limit of {MAX_BOOKINGS}'}), 400
    
    # Check if inventory has remaining items
    if inventory.remaining_count <= 0:
        return jsonify({'error': 'No items remaining in inventory'}), 400
    
    # Check if item is expired
    if inventory.expiration_date and inventory.expiration_date < date.today():
        return jsonify({'error': 'This item has expired and is no longer available'}), 400
    
    # Create booking
    booking_reference = str(uuid.uuid4())
    booking = Booking(
        booking_reference=booking_reference,
        member_id=member_id,
        inventory_id=inventory_id
    )
    
    # Update inventory count
    inventory.remaining_count -= 1
    
    # Update member booking count
    member.booking_count = (member.booking_count or 0) + 1
    
    db.session.add(booking)
    db.session.commit()
    
    return jsonify({
        'message': 'Booking successful',
        'booking_reference': booking_reference
    }), 201

@app.route('/cancel', methods=['POST'])
def cancel_booking():
    data = request.get_json()
    booking_reference = data.get('booking_reference')
    
    if not booking_reference:
        return jsonify({'error': 'Missing booking reference'}), 400
    
    booking = Booking.query.filter_by(booking_reference=booking_reference, is_active=True).first()
    
    if not booking:
        return jsonify({'error': 'Active booking not found'}), 404
    
    # Cancel booking
    booking.is_active = False
    
    # Return item to inventory
    inventory = Inventory.query.get(booking.inventory_id)
    inventory.remaining_count += 1
    
    # Update member booking count
    member = Member.query.get(booking.member_id)
    if member.booking_count and member.booking_count > 0:
        member.booking_count -= 1
    
    db.session.commit()
    
    return jsonify({'message': 'Booking cancelled successfully'}), 200

@app.route('/api/members')
def get_members():
    members = Member.query.all()
    members_list = [{
        'id': member.id,
        'first_name': member.first_name,
        'last_name': member.last_name,
        'email': member.email,
        'phone': member.phone,
        'booking_count': member.booking_count,
        'date_joined': member.date_joined.isoformat() if member.date_joined else None
    } for member in members]
    return jsonify(members_list)

@app.route('/api/inventory')
def get_inventory():
    inventory_items = Inventory.query.all()
    inventory_list = [{
        'id': item.id,
        'name': item.name,
        'description': item.description,
        'total_count': item.total_count,
        'remaining_count': item.remaining_count,
        'expiration_date': item.expiration_date.isoformat() if item.expiration_date else None
    } for item in inventory_items]
    return jsonify(inventory_list)

@app.route('/api/bookings')
def get_bookings():
    bookings = Booking.query.all()
    bookings_list = [{
        'id': booking.id,
        'booking_reference': booking.booking_reference,
        'booking_date': booking.booking_date.isoformat(),
        'member_id': booking.member_id,
        'inventory_id': booking.inventory_id,
        'is_active': booking.is_active
    } for booking in bookings]
    return jsonify(bookings_list)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8080) 