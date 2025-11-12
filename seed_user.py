from models.user_models import User, Base
from database import SessionLocal, engine
from werkzeug.security import generate_password_hash

# Create tables if not already created
Base.metadata.create_all(bind=engine)

# Define users to seed
users_to_seed = [
    {
        "first_name": "Sejj",
        "last_name": "Tech",
        "email": "sejjtechnologies@gmail.com",
        "password": "sejjtech",
        "role": "Admin"
    },
    {
        "first_name": "kato",
        "last_name": "Brian",
        "email": "kato@gmail.com",
        "password": "cashier123",
        "role": "Cashier"
    },
    {
        "first_name": "franklin",
        "last_name": "Aryatujuna",
        "email": "franklin@gmail.com",
        "password": "fieldwork456",
        "role": "Field Officer"
    }
]

# Insert users if they don't already exist
session = SessionLocal()
inserted = 0

for u in users_to_seed:
    existing = session.query(User).filter_by(email=u["email"]).first()
    if existing:
        print(f"⚠️ User with email {u['email']} already exists. Skipping.")
        continue

    hashed_pw = generate_password_hash(u["password"])
    user = User(
        first_name=u["first_name"],
        last_name=u["last_name"],
        email=u["email"],
        password=hashed_pw,
        role=u["role"]
    )
    session.add(user)
    inserted += 1

session.commit()
session.close()

print(f"✅ {inserted} new user(s) inserted successfully.")