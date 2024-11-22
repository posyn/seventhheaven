# Database module

import os
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, JSON, MetaData, Table, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
load_dotenv()

# Retrieve the DATABASE_URL from environment variables
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError("No DATABASE_URL found in environment variables.")

# Initialize the database connection
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define the DataObjects table
class DataObjectsTable(Base):
    __tablename__ = 'data_objects'

    id = Column(Integer, primary_key=True, index=True)
    headline = Column(String)
    date_time = Column(DateTime)
    ticker = Column(String)
    industry = Column(String)
    sentiment = Column(String)
    summary = Column(String)
    interpretation = Column(String)
    hash = Column(String(64), unique=True, index=True)  # SHA-256 hash

def create_tables():
    Base.metadata.create_all(bind=engine)


# Define the TradeObjects table
class TradeObjectsTable(Base):
    __tablename__ = 'trade_objects'

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String)
    date_time = Column(DateTime)
    price = Column(Float)
    rsi = Column(Float)
    macd = Column(JSON)  # Assuming MACD is stored as a JSON object
    last_volume = Column(Integer)
    average_volume = Column(Integer)
    iv = Column(Float)
    hash = Column(String)

# Create engine and session for interacting with the database
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Function to create tables
def create_tables():
    Base.metadata.create_all(bind=engine)
