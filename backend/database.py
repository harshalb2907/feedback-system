# backend/database.py
# SQLite database setup using SQLAlchemy ORM

from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# -------------------------------------------------------
# Database Configuration
# -------------------------------------------------------
# SQLite file will be created at: brain-checker-project/feedback.db
DATABASE_URL = "sqlite:///./feedback.db"

# Create the SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite with FastAPI
)

# Session factory — used to interact with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()


# -------------------------------------------------------
# Feedback Model (maps to 'feedback' table)
# -------------------------------------------------------
class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False)
    branch = Column(String(50), nullable=False)       # pune / nashik / thane
    rating = Column(Integer, nullable=False)          # 1 to 5
    service = Column(String(200), nullable=True)      # Service or test taken
    message = Column(Text, nullable=True)             # Complaint text or AI review
    type = Column(String(20), nullable=False)         # 'review' or 'complaint'
    timestamp = Column(DateTime, default=datetime.utcnow)


# -------------------------------------------------------
# Create all tables in the database
# -------------------------------------------------------
def init_db():
    """Create the database tables if they don't already exist."""
    Base.metadata.create_all(bind=engine)


# -------------------------------------------------------
# Dependency: Get DB session (used in FastAPI routes)
# -------------------------------------------------------
def get_db():
    """Yield a database session and ensure it's closed after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
