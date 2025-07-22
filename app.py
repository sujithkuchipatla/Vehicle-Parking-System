from flask import Flask
from models.models import db, initialize_admin
from flask import Flask, redirect, url_for

from controllers.auth_controller import auth_bp
from controllers.admin_controller import admin_bp
from controllers.user_controller import user_bp

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'sujith_rohan_reddy'  # For session

# Initialize DB
db.init_app(app)

# Create DB and admin
with app.app_context():
    db.create_all()
    initialize_admin()

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp)
app.register_blueprint(user_bp, url_prefix='/user')


# app.py

@app.route('/')
def home():
    return redirect(url_for('auth.login'))


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
