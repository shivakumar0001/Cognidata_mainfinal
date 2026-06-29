from sqlalchemy import Column, Integer, String, Boolean
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    id              = Column(Integer, primary_key=True, index=True)
    email           = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role            = Column(String(50), default="user")
    name            = Column(String(255), nullable=True)
    active          = Column(Boolean, default=True)
    totp_secret     = Column(String(64), nullable=True)
    totp_enabled    = Column(Boolean, default=False)
