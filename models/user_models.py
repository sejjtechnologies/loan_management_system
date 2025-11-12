# models/user_models.py

from sqlalchemy import Column, Integer, String, Text
from database import Base  # ✅ Shared Base from database.py

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password = Column(Text, nullable=False)  # hashed with Werkzeug or similar
    role = Column(String(50), default='user')
    profile_image = Column(Text)  # URL or path to image