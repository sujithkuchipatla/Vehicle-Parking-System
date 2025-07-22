from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from models.models import db, User, ParkingLot, ParkingSpot ,ReserveSpot

admin_bp = Blueprint('admin', __name__, template_folder='../templates')

# Middleware: allow only admins
def admin_only(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get('user_role') != 'admin':
            flash("Access denied. Admins only!", "danger")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return wrapper






# Route: Admin Dashboard

@admin_bp.route('/dashboard')
@admin_only
def dashboard():
    lots = ParkingLot.query.all()
    total_lots = len(lots)
    total_spots = ParkingSpot.query.count()
    occupied_spots = ParkingSpot.query.filter_by(status='O').count()
    available_spots = ParkingSpot.query.filter_by(status='A').count()

    # Prepare lot data with spot and reservation info
    lot_data = []
    for lot in lots:
        spot_details = []
        occupied_count = 0

        for spot in lot.spots:
            latest_reservation = ReserveSpot.query.filter_by(spot_id=spot.id).order_by(ReserveSpot.parking_timestamp.desc()).first()
            if spot.status == 'O':
                occupied_count += 1
            spot_details.append({
                'spot': spot,
                'reservation': latest_reservation
            })

        # Append lot and spots with extra 'occupied_count'
        lot_data.append({
            'lot': lot,
            'spots': spot_details,
            'occupied_count': occupied_count,
            'max_spots': lot.max_spots
        })

    pie_data = {
        'labels': ['Occupied', 'Available'],
        'values': [occupied_spots, available_spots]
    }

    return render_template('admin/dashboard.html',
                           lot_data=lot_data,
                           total_lots=total_lots,
                           total_spots=total_spots,
                           occupied=occupied_spots,
                           available=available_spots,
                           pie_data=pie_data)






# Route: Add Parking Lot
@admin_bp.route('/add_lot', methods=['GET', 'POST'])
@admin_only

def add_lot():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        pin = request.form['pin_code']
        price = float(request.form['price'])
        total_spots = int(request.form['spots'])

        lot = ParkingLot(
            prime_location_name=name,
            address=address,
            pin_code=pin,
            price=price,
            max_spots=total_spots
        )
        db.session.add(lot)
        db.session.commit()

        # Auto-create parking spots
        for i in range(total_spots):
            spot = ParkingSpot(lot_id=lot.id, status='A')
            db.session.add(spot)

        db.session.commit()
        flash("New parking lot added with spots!", "success")
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/add_lot.html')




@admin_bp.route('/lot/edit/<int:lot_id>', methods=['GET', 'POST'])
@admin_only


def edit_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)

    if request.method == 'POST':
        lot.prime_location_name = request.form['prime_location_name']
        lot.address = request.form['address']
        lot.pin_code = request.form['pin_code']
        lot.price = float(request.form['price'])

        new_total_spots = int(request.form['max_spots'])
        current_total_spots = len(lot.spots)

        if new_total_spots > current_total_spots:
            # Add new spots
            for _ in range(new_total_spots - current_total_spots):
                new_spot = ParkingSpot(lot_id=lot.id, status='A')
                db.session.add(new_spot)
        elif new_total_spots < current_total_spots:
            # Delete only unoccupied spots
            extra_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').limit(current_total_spots - new_total_spots).all()
            if len(extra_spots) < (current_total_spots - new_total_spots):
                flash("Cannot reduce to that many spots. Some spots are still occupied.", "danger")
                return redirect(url_for('admin.edit_lot', lot_id=lot_id))

            for spot in extra_spots:
                db.session.delete(spot)

        lot.max_spots = new_total_spots
        db.session.commit()
        flash("Parking lot updated successfully!", "success")
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/edit_lot.html', lot=lot)






# Route: Delete Parking Lot
@admin_bp.route('/delete_lot/<int:lot_id>')
@admin_only

def delete_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    occupied = ParkingSpot.query.filter_by(lot_id=lot_id, status='O').first()
    if occupied:
        flash("Cannot delete! Some spots are still occupied.", "warning")
        return redirect(url_for('admin.dashboard'))

    ParkingSpot.query.filter_by(lot_id=lot_id).delete()
    db.session.delete(lot)
    db.session.commit()

    flash("Parking lot and its spots removed.", "info")
    return redirect(url_for('admin.dashboard'))


# Route: Delete Parking Spot
@admin_bp.route('/delete_spot/<int:spot_id>', methods=['POST'])
@admin_only
def delete_spot(spot_id):
    spot = ParkingSpot.query.get_or_404(spot_id)

    if spot.status == 'O':
        flash("Cannot delete an occupied spot.", "warning")
        return redirect(url_for('admin.dashboard'))

    db.session.delete(spot)
    db.session.commit()

    flash("Parking spot deleted successfully.", "info")
    return redirect(url_for('admin.dashboard'))




# Route: View Users
@admin_bp.route('/users')
@admin_only
def registered_users():
    users = User.query.filter_by(role='user').all()
    return render_template('admin/users.html', users=users)





@admin_bp.route('/spots/status')


def spot_status():
    lots = ParkingLot.query.all()

    # Preload parking spots and their latest reservation (if any)
    all_lot_data = []
    for lot in lots:
        spot_data = []
        for spot in lot.spots:
            # Get latest reservation
            reservation = ReserveSpot.query.filter_by(spot_id=spot.id).order_by(ReserveSpot.parking_timestamp.desc()).first()
            spot_data.append({
                'id': spot.id,
                'status': spot.status,
                'reservation': reservation  # can be None
            })

        all_lot_data.append({
            'lot': lot,
            'spots': spot_data
        })

    return render_template('spot_status.html', lot_data=all_lot_data)


@admin_bp.route('/vehicle/<int:reservation_id>')

def view_vehicle_details(reservation_id):
    reservation = ReserveSpot.query.get_or_404(reservation_id)
    user = reservation.user
    return render_template('admin/vehicle_details.html', reservation=reservation, user=user)


@admin_bp.route('/spot/<int:spot_id>')
@admin_only

def view_spot(spot_id):
    spot = ParkingSpot.query.get_or_404(spot_id)
    reservation = ReserveSpot.query.filter_by(spot_id=spot_id).order_by(ReserveSpot.parking_timestamp.desc()).first()
    return render_template('admin/view_spot.html', spot=spot, reservation=reservation)


@admin_bp.route('/summary')
@admin_only
def summary():
    # Fetch required data from DB
    lots = ParkingLot.query.all()
    summary_data = []

    for lot in lots:
        total_spots = lot.max_spots
        occupied = sum(1 for s in lot.spots if s.status == 'O')
        available = total_spots - occupied
        revenue = sum(r.parking_cost for s in lot.spots for r in s.reservations)

        summary_data.append({
            'location': lot.prime_location_name,
            'occupied': occupied,
            'available': available,
            'revenue': revenue
        })

    return render_template('admin/summary.html', data=summary_data )
