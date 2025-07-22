# /controllers/user_controller.py

from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from models.models import db, ParkingLot, ParkingSpot, ReserveSpot, User
from datetime import datetime
from sqlalchemy.orm import joinedload
from sqlalchemy import and_

user_bp = Blueprint('user', __name__, template_folder='../templates')


@user_bp.route('/dashboard')
def dashboard():
    if session.get('user_role') != 'user':
        flash("Please login as a user to access the dashboard.", "warning")
        return redirect(url_for('auth.login'))

    user_id = session.get('user_id')
    user = User.query.get(user_id)

    lots = ParkingLot.query.options(joinedload(ParkingLot.spots)).all()
    reservations = ReserveSpot.query.filter_by(user_id=user_id).order_by(ReserveSpot.parking_timestamp.desc()).all()

    # Format timestamps
    for res in reservations:
        res.parking_time_str = res.parking_timestamp.strftime('%Y-%m-%d %H:%M') if res.parking_timestamp else ''
        res.leaving_time_str = res.leaving_timestamp.strftime('%Y-%m-%d %H:%M') if res.leaving_timestamp else ''

    return render_template(
        'user_dashboard.html',
        lots=lots,
        reservations=reservations,
        current_user=user,
        now=datetime.now().strftime('%Y-%m-%d %H:%M')
    )

@user_bp.route('/book_form/<int:lot_id>', methods=['GET'])
def show_book_form(lot_id):
    if session.get('user_role') != 'user':
        flash("Unauthorized. Please login as user.", "danger")
        return redirect(url_for('auth.login'))

    lot = ParkingLot.query.get_or_404(lot_id)

    # Fetch first available spot directly from DB
    available_spot = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').first()

    if not available_spot:
        flash("No available spots in this lot.", "danger")
        return redirect(url_for("user.dashboard"))

    # Pass user_id from session to template
    return render_template("book_spot.html", lot=lot, spot=available_spot, user_id=session.get('user_id'))


@user_bp.route('/book_spot/<int:lot_id>', methods=['POST'])

def book_spot(lot_id):
    if session.get('user_role') != 'user':
        flash("Unauthorized. Please login as user.", "danger")
        return redirect(url_for('auth.login'))

    vehicle_no = request.form.get("vehicle_no")
    user_id = session.get('user_id')

    # Find the first available spot in the lot
    spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()

    if not spot:
        flash("No available spots in this lot.", "danger")
        return redirect(url_for("user.dashboard"))

    # Create reservation
    reservation = ReserveSpot(
        user_id=user_id,
        spot_id=spot.id,
        parking_timestamp=datetime.now(),
        leaving_timestamp=None,
        vehicle_no=vehicle_no,
        parking_cost=0
    )

    # Mark spot as occupied
    spot.status = 'O'

    db.session.add(reservation)
    db.session.commit()

    flash(f"Spot {spot.id} in Lot {lot_id} booked successfully.", "success")
    return redirect(url_for("user.dashboard"))


@user_bp.route('/release_spot/<int:reservation_id>', methods=['GET', 'POST'])
def release_spot(reservation_id):
    if session.get('user_role') != 'user':
        flash("Unauthorized. Please login as user.", "danger")
        return redirect(url_for('auth.login'))

    reservation = ReserveSpot.query.get_or_404(reservation_id)

    if request.method == 'POST':
        now = datetime.now()
        reservation.leaving_timestamp = now

        # Calculate duration and cost (e.g., ₹10 per hour)
        duration_hrs = (now - reservation.parking_timestamp).total_seconds() / 3600
        cost = round(duration_hrs * 10, 2)
        reservation.parking_cost = cost

        # Update the spot status to Available
        spot = ParkingSpot.query.get(reservation.spot_id)
        spot.status = 'A'

        db.session.commit()
        flash("Spot released successfully.", "info")
        return redirect(url_for('user.dashboard'))

    return render_template(
        'release_spot.html',
        reservation=reservation,
        current_time=datetime.now()
    )


@user_bp.route('/summary')
def summary():
    if session.get('user_role') != 'user':
        flash("Unauthorized. Please login as user.", "danger")
        return redirect(url_for('auth.login'))

    user_id = session.get('user_id')

    # Count how many times each parking lot was used by the user
    usage_summary = (
        db.session.query(ParkingLot.prime_location_name, db.func.count(ReserveSpot.id))
        .join(ParkingSpot, ParkingLot.id == ParkingSpot.lot_id)
        .join(ReserveSpot, ParkingSpot.id == ReserveSpot.spot_id)
        .filter(ReserveSpot.user_id == user_id)
        .group_by(ParkingLot.prime_location_name)
        .all()
    )

    labels = [row[0] for row in usage_summary]
    values = [row[1] for row in usage_summary]

    return render_template('user_summary.html', labels=labels, values=values)
