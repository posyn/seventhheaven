from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON
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

# TradeObject Table
class TradeObjectsTable(Base):
    __tablename__ = "trade_objects"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True)
    date_time = Column(DateTime, index=True)
    entry_price = Column(Float)
    stop_loss = Column(Float)
    position_size = Column(Integer)
    price_targets = Column(JSON)  # Stores a dictionary of price targets
    rsi = Column(Float)
    macd = Column(JSON)  # Stores a dictionary for macd values
    last_volume = Column(Integer)
    average_volume = Column(Integer)
    iv = Column(Float)
    action = Column(String)  # 'buy' or 'sell'
    hash = Column(String, unique=True, index=True)

# DataObject Table
class DataObjectsTable(Base):
    __tablename__ = "data_objects"

    id = Column(Integer, primary_key=True, index=True)
    headline = Column(String)
    date_time = Column(DateTime)
    ticker = Column(String, index=True)
    industry = Column(String)
    sentiment = Column(String)
    summary = Column(String)
    interpretation = Column(String)
    hash = Column(String, unique=True, index=True)

# Create all tables in the database
Base.metadata.create_all(bind=engine)
