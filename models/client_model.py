from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, Boolean
from database import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    second_name = Column(String, nullable=False)
    address = Column(String)
    date_of_birth = Column(Date)
    occupation = Column(String)
    phone = Column(String, nullable=False)


class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    principal = Column(Float, nullable=False)
    interest_rate = Column(Float, default=0.20)
    total_amount = Column(Float, nullable=False)
    daily_payment = Column(Float, nullable=False)
    start_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    missed_days = Column(Integer, default=0)
    penalty = Column(Float, default=0.0)
    is_fully_paid = Column(Boolean, default=False)

    guarantor_name = Column(String, nullable=False)
    guarantor_phone = Column(String, nullable=False)
    guarantor_address = Column(String)
    guarantor_nin = Column(String, nullable=False)
    guarantor_occupation = Column(String)

    security = Column(String)  # ✅ New column added


class LoanPayment(Base):
    __tablename__ = "loan_payments"

    id = Column(Integer, primary_key=True)
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=False)
    amount_paid = Column(Float, nullable=False)
    payment_date = Column(Date, nullable=False)
