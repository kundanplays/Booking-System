from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import csv
import os
from datetime import datetime, date
import uuid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///booking_new.db'
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
    
    print(f"Trying to parse date: {date_str}")
    
    # Try ISO format (2024-01-02T12:10:11)
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except (ValueError, TypeError) as e:
        print(f"ISO parse error: {e}")
        pass
    
    # Try DD/MM/YYYY format
    try:
        day, month, year = date_str.split('/')
        return date(int(year), int(month), int(day))
    except (ValueError, TypeError) as e:
        print(f"DD/MM/YYYY parse error: {e}")
        pass
    
    # Try YYYY-MM-DD format
    try:
        year, month, day = date_str.split('-')
        return date(int(year), int(month), int(day))
    except (ValueError, TypeError) as e:
        print(f"YYYY-MM-DD parse error: {e}")
        pass
    
    # Try to parse with dateutil as a last resort
    try:
        from dateutil import parser
        return parser.parse(date_str)
    except (ImportError, ValueError, TypeError) as e:
        print(f"dateutil parse error: {e}")
        pass
    
    print(f"Could not parse date: {date_str}")
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
                
                # Debug headers
                print(f"CSV Headers: {headers}")

                # Detect format type
                # if 'name' in headers and 'surname' in headers:
                    # Appendix 1 format
                for row in csv_reader:
                    print(f"Processing row: {row}")  # Debug
                    print(row)
                    # Convert booking_count to integer or default to 0
                    try:
                        booking_count = int(row.get('booking_count', 0)) if row.get('booking_count', '').strip() else 0
                    except ValueError:
                        booking_count = 0
                        print(f"Invalid booking_count value: {row.get('booking_count')}")

                    # Parse date
                    date_joined = parse_date(row.get('date_joined'))
                    if not date_joined and row.get('date_joined'):
                        print(f"Failed to parse date: {row.get('date_joined')}")

                    member = Member(
                        first_name=row.get('name', '').strip(),
                        last_name=row.get('surname', '').strip(),
                        booking_count=booking_count,
                        date_joined=date_joined
                    )
                    db.session.add(member)
                # else:
                #     # Original format
                #     for row in csv_reader:
                #         print(f"Processing row: {row}")  # Debug
                #         member = Member(
                #             first_name=row.get('name', '').strip(),
                #             last_name=row.get('last_name', '').strip(),
                #             email=row.get('email', '').strip(),
                #             phone=row.get('phone', '').strip()
                #         )
                #         db.session.add(member)
            
            db.session.commit()
            flash('Members data uploaded successfully', 'success')
        
        elif 'inventory' in filename.lower():
            with open(filepath, 'r') as f:
                csv_reader = csv.DictReader(f)
                headers = csv_reader.fieldnames
                
                # Detect format type
                # if 'title' in headers:
                    # Appendix 2 format
                for row in csv_reader:
                    # For this format, we'll set total_count same as remaining_count initially
                    remaining_count = int(row.get('remaining_count', 0)) if row.get('remaining_count', '').strip() else 0

                    inventory = Inventory(
                        name=row.get('title', '').strip(),
                        description=row.get('description', '').strip(),
                        remaining_count=remaining_count,
                        # total_count=remaining_count,  # Setting total same as remaining for this format
                        expiration_date=parse_date(row.get('expiration_date'))
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

@app.route('/admin')
def admin_panel():
    """Admin panel to manage all aspects of the booking system."""
    members = Member.query.all()
    inventory = Inventory.query.all()
    bookings = Booking.query.all()
    
    # Count statistics
    stats = {
        'total_members': len(members),
        'total_inventory': len(inventory),
        'total_bookings': len(bookings),
        'active_bookings': len([b for b in bookings if b.is_active]),
        'available_items': sum(item.remaining_count for item in inventory),
        'expired_items': len([i for i in inventory if i.expiration_date and i.expiration_date < date.today()])
    }
    
    return render_template(
        'admin.html', 
        members=members, 
        inventory=inventory, 
        bookings=bookings, 
        stats=stats
    )

@app.route('/admin/delete_member/<int:member_id>', methods=['POST'])
def delete_member(member_id):
    """Delete a member and their bookings."""
    member = Member.query.get(member_id)
    if member:
        # First check if member has active bookings
        active_bookings = Booking.query.filter_by(member_id=member_id, is_active=True).all()
        
        # Return inventory items
        for booking in active_bookings:
            inventory = Inventory.query.get(booking.inventory_id)
            if inventory:
                inventory.remaining_count += 1
        
        # Delete all bookings for this member
        Booking.query.filter_by(member_id=member_id).delete()
        
        # Delete the member
        db.session.delete(member)
        db.session.commit()
        flash(f'Member {member.first_name} {member.last_name} deleted successfully', 'success')
    else:
        flash('Member not found', 'error')
    
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete_inventory/<int:inventory_id>', methods=['POST'])
def delete_inventory(inventory_id):
    """Delete an inventory item and cancel related bookings."""
    inventory = Inventory.query.get(inventory_id)
    if inventory:
        # Cancel all active bookings for this inventory
        active_bookings = Booking.query.filter_by(inventory_id=inventory_id, is_active=True).all()
        for booking in active_bookings:
            booking.is_active = False
            member = Member.query.get(booking.member_id)
            if member and member.booking_count and member.booking_count > 0:
                member.booking_count -= 1
        
        # Delete the inventory item
        db.session.delete(inventory)
        db.session.commit()
        flash(f'Inventory item {inventory.name} deleted successfully', 'success')
    else:
        flash('Inventory item not found', 'error')
    
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete_multiple_members', methods=['POST'])
def delete_multiple_members():
    """Delete multiple members and their bookings."""
    member_ids = request.form.getlist('member_ids')
    
    if not member_ids:
        flash('No members selected', 'error')
        return redirect(url_for('admin_panel'))
    
    count = 0
    for member_id in member_ids:
        member = Member.query.get(int(member_id))
        if member:
            # First check if member has active bookings
            active_bookings = Booking.query.filter_by(member_id=member_id, is_active=True).all()
            
            # Return inventory items
            for booking in active_bookings:
                inventory = Inventory.query.get(booking.inventory_id)
                if inventory:
                    inventory.remaining_count += 1
            
            # Delete all bookings for this member
            Booking.query.filter_by(member_id=member_id).delete()
            
            # Delete the member
            db.session.delete(member)
            count += 1
    
    db.session.commit()
    flash(f'{count} members deleted successfully', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete_multiple_inventory', methods=['POST'])
def delete_multiple_inventory():
    """Delete multiple inventory items and cancel related bookings."""
    inventory_ids = request.form.getlist('inventory_ids')
    
    if not inventory_ids:
        flash('No inventory items selected', 'error')
        return redirect(url_for('admin_panel'))
    
    count = 0
    for inventory_id in inventory_ids:
        inventory = Inventory.query.get(int(inventory_id))
        if inventory:
            # Cancel all active bookings for this inventory
            active_bookings = Booking.query.filter_by(inventory_id=inventory_id, is_active=True).all()
            for booking in active_bookings:
                booking.is_active = False
                member = Member.query.get(booking.member_id)
                if member and member.booking_count and member.booking_count > 0:
                    member.booking_count -= 1
            
            # Delete the inventory item
            db.session.delete(inventory)
            count += 1
    
    db.session.commit()
    flash(f'{count} inventory items deleted successfully', 'success')
    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8000)