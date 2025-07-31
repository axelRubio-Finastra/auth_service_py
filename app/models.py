from sqlalchemy import Column, Integer, String, Boolean
from .database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)
    name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    role = Column(String, default='user')
    verification_token = Column(String, nullable=True)

