# Vehicle Parking Management System 🚗

A Flask-based web application for managing vehicle parking operations. It supports two user roles—**Admin** and **User**—with full dashboards for booking, monitoring, and managing parking lots and spots in real-time.

---

## 🔧 Features

### 👨‍💼 Admin
- Login with pre-defined admin credentials
- Create, edit, or delete parking lots (only if all spots are free)
- View spot-wise occupancy in a visual grid
- View details of occupied spots including vehicle number, user, and timestamps
- See a list of all registered users
- Dashboard charts summarizing parking lot status

### 🙋 User
- Register and log in
- Book a spot in a chosen parking lot (auto-assigned)
- Mark status as "occupied" when parked, "released" when vacated
- View personal parking history and dashboard summaries

---

## 🛠️ Tech Stack

- **Backend:** Flask, SQLAlchemy, SQLite
- **Frontend:** HTML, CSS, Jinja2, Bootstrap (or Custom CSS)
- **Charts:** Chart.js
- **Authentication:** Flask session-based (without Flask-Login)

---

## 📁 Folder Structure

/parking/
│
├── app.py # Main Flask application
├── requirements.txt # List of dependencies
│
├── /templates/ # HTML templates
│ ├── login.html
│ ├── register.html
│ ├── user_dashboard.html
│ ├── spot_status.html
│ └── /admin/
│ ├── dashboard.html
│ ├── add_lot.html
│ └── user.html
│
├── /static/ # Static files (CSS, images)
│ ├── /css/
│ │ └── style.css
│ └── /images/
│ └── logo.png
│
├── /models/
│ └── models.py # All database models
│
├── /controllers/ # Route controllers (Blueprints)
│ ├── auth_controller.py # Login/registration
│ ├── admin_controller.py # Admin routes
│ └── user_controller.py # User routes









Image


<img width="1919" height="1023" alt="Screenshot 2025-07-22 104650" src="https://github.com/user-attachments/assets/e451ae5b-7c8c-4a40-a618-45efefa90dd3" />
