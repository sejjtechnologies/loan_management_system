from flask import Blueprint, render_template, request, redirect, flash
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from models.client_model import Client, Loan, LoanPayment
from database import engine

loan_routes = Blueprint("loan_routes", __name__)

@loan_routes.route("/give_loan", methods=["GET", "POST"])
def give_loan():
    client_id = request.args.get("client_id") or request.form.get("client_id")

    if not client_id:
        flash("Client ID is missing.", "danger")
        return redirect("/view_clients")

    with Session(engine) as db:
        client = db.query(Client).filter_by(id=int(client_id)).first()
        if not client:
            flash("Client not found.", "danger")
            return redirect("/view_clients")

        unpaid_loan = db.query(Loan).filter_by(client_id=client.id, is_fully_paid=False).first()
        if unpaid_loan:
            flash("Loan denied: Client still has an unpaid balance.", "danger")
            return redirect("/view_clients")

        if request.method == "POST":
            try:
                principal = float(request.form.get("principal"))
                if principal <= 0:
                    raise ValueError("Loan amount must be positive.")

                start_date = datetime.strptime(request.form.get("start_date"), "%Y-%m-%d")
                due_date = start_date + timedelta(days=30)

                interest = principal * 0.20
                total_amount = principal + interest
                daily_payment = round(total_amount / 30, 2)

                loan = Loan(
                    client_id=client.id,
                    principal=principal,
                    interest_rate=0.20,
                    total_amount=total_amount,
                    daily_payment=daily_payment,
                    start_date=start_date,
                    due_date=due_date,
                    guarantor_name=request.form.get("guarantor_name"),
                    guarantor_phone=request.form.get("guarantor_phone"),
                    guarantor_address=request.form.get("guarantor_address"),
                    guarantor_nin=request.form.get("guarantor_nin"),
                    guarantor_occupation=request.form.get("guarantor_occupation"),
                    security=request.form.get("security"),
                    is_fully_paid=False
                )
                db.add(loan)
                db.commit()
                flash("Loan issued successfully!", "success")
                return redirect("/view_clients")

            except Exception as e:
                flash(f"Error: {str(e)}", "danger")
                return render_template("give_loan.html", client=client)

        return render_template("give_loan.html", client=client)


@loan_routes.route("/pay_loan/<int:loan_id>", methods=["GET", "POST"])
def pay_loan(loan_id):
    with Session(engine) as db:
        loan = db.query(Loan).filter_by(id=loan_id).first()
        if not loan:
            flash("Loan not found.", "danger")
            return redirect("/view_clients")

        client = db.query(Client).filter_by(id=loan.client_id).first()
        payments = db.query(LoanPayment).filter_by(loan_id=loan.id).all()
        total_paid = sum(p.amount_paid for p in payments)
        balance = max(loan.total_amount - total_paid, 0)
        remaining_days = max((loan.due_date - datetime.today().date()).days, 0)

        if request.method == "POST":
            try:
                amount = float(request.form.get("amount"))
                if amount <= 0:
                    raise ValueError("Payment must be greater than zero.")

                payment = LoanPayment(
                    loan_id=loan.id,
                    amount_paid=amount,
                    payment_date=datetime.today().date()
                )
                db.add(payment)

                total_paid += amount
                if total_paid >= loan.total_amount:
                    loan.is_fully_paid = True

                db.commit()
                flash("Payment recorded successfully.", "success")
                return redirect("/view_clients")

            except Exception as e:
                flash(f"Error: {str(e)}", "danger")

        return render_template("pay_loan.html",
                               loan=loan,
                               client=client,
                               total_paid=total_paid,
                               balance=balance,
                               remaining_days=remaining_days)


@loan_routes.route("/edit_loan/<int:loan_id>", methods=["GET", "POST"])
def edit_loan(loan_id):
    with Session(engine) as db:
        loan = db.query(Loan).filter_by(id=loan_id).first()
        if not loan:
            flash("Loan not found.", "danger")
            return redirect("/view_clients")

        if request.method == "POST":
            try:
                principal = float(request.form.get("principal"))
                start_date = datetime.strptime(request.form.get("start_date"), "%Y-%m-%d")
                due_date = datetime.strptime(request.form.get("due_date"), "%Y-%m-%d")
                is_fully_paid = request.form.get("is_fully_paid") == "true"

                interest = principal * loan.interest_rate
                total_amount = principal + interest
                daily_payment = round(total_amount / 30, 2)

                loan.principal = principal
                loan.total_amount = total_amount
                loan.daily_payment = daily_payment
                loan.start_date = start_date
                loan.due_date = due_date
                loan.is_fully_paid = is_fully_paid

                loan.guarantor_name = request.form.get("guarantor_name")
                loan.guarantor_phone = request.form.get("guarantor_phone")
                loan.guarantor_address = request.form.get("guarantor_address")
                loan.guarantor_nin = request.form.get("guarantor_nin")
                loan.guarantor_occupation = request.form.get("guarantor_occupation")
                loan.security = request.form.get("security")

                db.commit()
                flash("Loan updated successfully.", "success")
                return redirect("/view_clients")

            except Exception as e:
                flash(f"Error: {str(e)}", "danger")

        return render_template("edit_loan.html", loan=loan)


@loan_routes.route("/edit_client/<int:client_id>", methods=["GET", "POST"])
def edit_client(client_id):
    with Session(engine) as db:
        client = db.query(Client).filter_by(id=client_id).first()
        if not client:
            flash("Client not found.", "danger")
            return redirect("/view_clients")

        if request.method == "POST":
            try:
                client.first_name = request.form.get("first_name")
                client.second_name = request.form.get("second_name")
                client.phone = request.form.get("phone")
                client.address = request.form.get("address")
                client.occupation = request.form.get("occupation")
                dob = request.form.get("dob")
                if dob:
                    client.date_of_birth = datetime.strptime(dob, "%Y-%m-%d")

                db.commit()
                flash("Client details updated successfully.", "success")
                return redirect("/view_clients")

            except Exception as e:
                flash(f"Error: {str(e)}", "danger")

        return render_template("edit_client.html", client=client)