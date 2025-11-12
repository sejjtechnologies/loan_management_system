from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models.user_models import User
from models.client_model import Client, Loan
from database import engine
import os
import uuid
import secrets
from datetime import datetime

admin_routes = Blueprint("admin_routes", __name__)

UPLOAD_FOLDER = "static/users"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@admin_routes.route("/admin/manage_users")
def manage_users():
    with Session(engine) as db:
        users = db.query(User).order_by(User.id.asc()).all()
        return render_template("admin_manage_users.html", users=users)


@admin_routes.route("/admin/edit_user/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    with Session(engine) as db:
        user = db.query(User).get(user_id)

        if request.method == "POST":
            user.first_name = request.form.get("first_name")
            user.last_name = request.form.get("last_name")
            user.email = request.form.get("email")

            original_role = user.role
            user.role = request.form.get("role")

            current_password = request.form.get("current_password")
            new_password = request.form.get("password")

            if new_password:
                is_self = session.get("user_id") == user.id
                if original_role == "Admin" and is_self:
                    if not current_password or not check_password_hash(user.password, current_password):
                        flash("Incorrect current password. Password not updated.", "danger")
                        return redirect(url_for("admin_routes.edit_user", user_id=user.id))
                user.password = generate_password_hash(new_password)

            file = request.files.get("profile_image")
            if file and file.filename:
                if user.profile_image and os.path.exists(user.profile_image.replace("/", os.sep)):
                    os.remove(user.profile_image.replace("/", os.sep))

                filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                user.profile_image = f"static/users/{filename}"

            db.commit()
            flash("User updated successfully.", "success")
            return redirect(url_for("admin_routes.manage_users"))

        return render_template("admin_edit_user.html", user=user)


@admin_routes.route("/admin/delete_user/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    with Session(engine) as db:
        user = db.query(User).get(user_id)
        if user:
            if user.profile_image and os.path.exists(user.profile_image.replace("/", os.sep)):
                os.remove(user.profile_image.replace("/", os.sep))

            db.delete(user)
            db.commit()
            flash("User deleted successfully.", "success")
        else:
            flash("User not found.", "danger")
        return redirect(url_for("admin_routes.manage_users"))


@admin_routes.route("/admin/create_user", methods=["GET", "POST"])
def create_user():
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        role = request.form.get("role")
        password = request.form.get("password")
        file = request.files.get("profile_image")

        with Session(engine) as db:
            existing_user = db.query(User).filter_by(email=email).first()
            if existing_user:
                flash("A user with that email already exists.", "danger")
                return redirect(url_for("admin_routes.create_user"))

            if not password:
                password = secrets.token_urlsafe(10)

            profile_image_path = None
            if file and file.filename:
                filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                profile_image_path = f"static/users/{filename}"

            new_user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                role=role,
                password=generate_password_hash(password),
                profile_image=profile_image_path,
            )
            db.add(new_user)
            db.commit()
            flash("User account created successfully.", "success")
            return redirect(url_for("admin_routes.manage_users"))

    return render_template("admin_create-user.html")


@admin_routes.route("/add_client", methods=["GET", "POST"])
def add_client():
    if request.method == "POST":
        with Session(engine) as db:
            client = Client(
                first_name=request.form.get("first_name"),
                second_name=request.form.get("second_name"),
                address=request.form.get("address"),
                date_of_birth=datetime.strptime(request.form.get("dob"), "%Y-%m-%d"),
                occupation=request.form.get("occupation"),
                phone=request.form.get("phone")
            )
            db.add(client)
            db.commit()
            flash("Client added successfully!", "success")
            return redirect("/cashier_dashboard")
    return render_template("admin_add_client.html")


@admin_routes.route("/view_clients")
def view_clients():
    with Session(engine) as db:
        clients = db.query(Client).order_by(Client.first_name.asc()).all()

        # ✅ Build unpaid loan map with actual loan objects
        unpaid_loans = {}
        for client in clients:
            loan = db.query(Loan).filter_by(client_id=client.id, is_fully_paid=False).first()
            if loan:
                unpaid_loans[client.id] = loan

        return render_template("view_all_clients.html", clients=clients, unpaid_loans=unpaid_loans)