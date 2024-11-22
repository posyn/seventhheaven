from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Load the database URL from the environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Ensure DATABASE_URL is defined
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set. Please set this in your environment variables.")

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)

# Session local is used for session management in FastAPI
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all the models to inherit
Base = declarative_base()

# Dependency to get a new database session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
