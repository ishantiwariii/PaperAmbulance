from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True) # Setting nullable=True as Auth is handled by Clerk
    clerk_id = Column(String, unique=True, index=True, nullable=False) # Maps to 'sub' in JWT
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    profile = relationship("Profile", back_populates="user", uselist=False)
    form_history = relationship("FormHistory", back_populates="user")

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Internal link
    user_id_str = Column(String, unique=True, index=True, nullable=False) # Clerk 'sub' link
    
    # Store encrypted data or structured profile fields in JSONB format
    data = Column(JSON, nullable=True)
    
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="profile")

class FormHistory(Base):
    __tablename__ = "form_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Internal link
    user_id_str = Column(String, nullable=False) # Clerk 'sub' link
    site_url = Column(String, nullable=False)
    filled_at = Column(DateTime(timezone=True), server_default=func.now())
    field_count = Column(Integer, default=0)

    user = relationship("User", back_populates="form_history")

class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, index=True)
    user_id_str = Column(String, ForeignKey("users.clerk_id"), nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)

    user = relationship("User", backref="sessions")
