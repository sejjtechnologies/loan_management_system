# database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# PostgreSQL credentials
DB_USER = "postgres"
DB_PASSWORD = "sejjtechnologies"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "moneylend_db"

# Connection URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SQLAlchemy engine and session
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

# Base class for models
Base = declarative_base()