from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from models.user_models import User
from sqlalchemy.orm import Session
from database import engine

user_routes = Blueprint("user_routes", __name__)

@user_routes.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    with Session(engine) as session:
        user = session.query(User).filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            # Determine redirect path based on role
            if user.role.lower() == "admin":
                redirect_path = "/admin_dashboard"
            elif user.role.lower() == "cashier":
                redirect_path = "/cashier_dashboard"
            elif user.role.lower() == "field officer":
                redirect_path = "/field_officer_dashboard"
            else:
                redirect_path = "/unauthorized"

            return jsonify({
                "message": "Login successful",
                "redirect": redirect_path,
                "user": {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "role": user.role,
                },
            })
        else:
            return jsonify({"error": "Invalid credentials"}), 401

@user_routes.route("/logout", methods=["POST"])
def logout():
    # In a real app, you'd clear session or token here
    return jsonify({"message": "Logout successful", "redirect": "/"})