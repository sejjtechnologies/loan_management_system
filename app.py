from flask import Flask, render_template
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Import database and models
from database import engine
from models.user_models import Base
from models.client_model import Client  # ✅ Ensure Client table is registered

# Import routes
from routes.user_routes import user_routes
from routes.admin_routes import admin_routes
from routes.give_loan_routes import loan_routes  # ✅ Register Give Loan routes

app = Flask(__name__)

# Set secret key for session and flash support
app.secret_key = os.getenv("SECRET_KEY", "e4f9c3a2d8b14f6a9c3e7f1a2b6d4c8f")

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Register Blueprints
app.register_blueprint(user_routes)
app.register_blueprint(admin_routes)
app.register_blueprint(loan_routes)  # ✅ Register Give Loan blueprint

# Home route
@app.route("/")
def home():
    return render_template("home.html")

# Admin dashboard route
@app.route("/admin_dashboard")
def admin_dashboard():
    return render_template("admin_dashboard.html")

# Cashier dashboard route
@app.route("/cashier_dashboard")
def cashier_dashboard():
    return render_template("cashier_dashboard.html")

# Field Officer dashboard route
@app.route("/field_officer_dashboard")
def field_officer_dashboard():
    return render_template("field_officer_dashboard.html")

# Loan dashboard route
@app.route("/loan_dashboard")
def loan_dashboard():
    return render_template("loan_dashboard.html")

if __name__ == "__main__":
    app.run(debug=True)