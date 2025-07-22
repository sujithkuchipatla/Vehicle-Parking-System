from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.models import db, User, ParkingLot, ParkingSpot, ReserveSpot
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

# -----------------------
# REGISTER
# -----------------------
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')  # stored as-is (no hashing)
        name = request.form.get('name')
        address = request.form.get('address')
        pin_code = request.form.get('pin_code')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered.', 'warning')
            return redirect(url_for('auth.register'))

        new_user = User(
            email=email,
            password=password,  # no hashing for demo
            name=name,
            address=address,
            pin_code=pin_code
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

# -----------------------
# LOGIN
# -----------------------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and user.password == password:  # no password check
            session['user_id'] = user.id
            session['user_role'] = user.role
            flash('Login successful!', 'success')
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('user.dashboard'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')

# -----------------------
# LOGOUT
# -----------------------
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('auth.login'))

# -----------------------
# BOOK PARKING SPOT
# -----------------------
@auth_bp.route('/book_spot/<int:lot_id>')
def book_spot(lot_id):
    user_id = session.get('user_id')
    if not user_id:
        flash('Please login first.', 'warning')
        return redirect(url_for('auth.login'))

    spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()
    if not spot:
        flash('No available spots in this lot.', 'warning')
        return redirect(url_for('user.dashboard'))

    spot.status = 'O'
    reservation = ReserveSpot(
        spot_id=spot.id,
        user_id=user_id,
        parking_timestamp=datetime.now()
    )
    db.session.add(reservation)
    db.session.commit()

    flash('Spot booked successfully.', 'success')
    return redirect(url_for('user.dashboard'))

# -----------------------
# RELEASE PARKING SPOT
# -----------------------
@auth_bp.route('/release_spot/<int:reservation_id>')
def release_spot(reservation_id):
    user_id = session.get('user_id')
    if not user_id:
        flash('Please login first.', 'warning')
        return redirect(url_for('auth.login'))

    reservation = ReserveSpot.query.get(reservation_id)
    if not reservation or reservation.user_id != user_id:
        flash('Invalid reservation.', 'danger')
        return redirect(url_for('user.dashboard'))

    if reservation.leaving_timestamp is not None:
        flash('Spot already released.', 'info')
        return redirect(url_for('user.dashboard'))

    reservation.leaving_timestamp = datetime.now()
    duration = (reservation.leaving_timestamp - reservation.parking_timestamp).total_seconds() / 3600
    reservation.cost = round(duration * 20, 2)  # ₹20/hour
    reservation.spot.status = 'A'

    db.session.commit()

    flash('Spot released successfully.', 'success')
    return redirect(url_for('user.dashboard'))
