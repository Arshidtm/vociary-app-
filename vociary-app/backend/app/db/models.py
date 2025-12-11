# backend/app/db/models.py

from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, UniqueConstraint
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base

# Base class for the ORM models
Base = declarative_base()

# --- 1. User Model ---

class User(Base):
    """Represents a user of the AuraJournal system."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False) # For secure login (future feature)
    is_active = Column(Boolean, default=True)

    # Relationships
    diaries = relationship("Diary", back_populates="owner")
    entries = relationship("Entry", back_populates="user")


# --- 2. Diary Model ---

class Diary(Base):
    """Represents a specific journal/diary owned by a user (e.g., 'Work Log', 'Personal')"""
    __tablename__ = "diaries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    # Foreign Key
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    owner = relationship("User", back_populates="diaries")
    entries = relationship("Entry", back_populates="diary")


# --- 3. Entry Model ---

class Entry(Base):
    """Represents a single, dated entry (the core diary content)"""
    __tablename__ = "entries"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    entry_date = Column(Date, nullable=False)

    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"))
    diary_id = Column(Integer, ForeignKey("diaries.id"))

    # Relationships
    user = relationship("User", back_populates="entries")
    diary = relationship("Diary", back_populates="entries")

    # Constraint to enforce the core logic: 
    # A user can only have ONE entry for a specific date in a specific diary.
    __table_args__ = (
        UniqueConstraint('user_id', 'entry_date', 'diary_id', name='_user_date_diary_uc'),
    )