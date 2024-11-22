from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import TradeObject, DataObject
import os
import requests
from alpaca_trade_api.rest import REST
from polygon import RESTClient
import hashlib
from datetime import datetime, timedelta

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Create Alpaca and Polygon clients
alpaca_api_key = os.getenv("ALPACA_API_KEY")
alpaca_secret_key = os.getenv("ALPACA_SECRET_KEY")
polygon_api_key = os.getenv("POLYGON_API_KEY")

alpaca_client = REST(alpaca_api_key, alpaca_secret_key, base_url="https://paper-api.alpaca.markets")
polygon_client = RESTClient(polygon_api_key)

# Dependency to get a new database session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to create a unique hash for a TradeObject
def hash_trade_object(trade_object: TradeObject) -> str:
    try:
        trade_string = f"{trade_object.ticker}{trade_object.date_time}{trade_object.entry_price}{trade_object.stop_loss}{trade_object.position_size}{trade_object.price_targets}{trade_object.rsi}{trade_object.macd}{trade_object.last_volume}{trade_object.average_volume}{trade_object.iv}"
        return hashlib.sha256(trade_string.encode()).hexdigest()
    except Exception as e:
        print(f"Error hashing trade object: {str(e)}")
        return ""

# Endpoint to run the trading algorithm and save TradeObjects to the database
@app.post("/trade")
async def run_trading_algorithm(ticker: str, db: Session = Depends(get_db)):
    try:
        # Fetch historical market data from Polygon
        bars = polygon_client.get_aggs(
            ticker=ticker,
            multiplier=1,
            timespan="day",
            from_=datetime.now() - timedelta(days=365),
            to=datetime.now()
        )
        
        # Process market data and create TradeObject
        market_data = process_market_data(bars)
        trade_object = generate_trade_object(ticker, market_data)
        
        # If trade_object is generated, save it to the database
        if trade_object:
            # Hash the trade object
            trade_object.hash = hash_trade_object(trade_object)
            db.add(trade_object)
            db.commit()
            return {"status": "success", "trade_object": trade_object}
        
        return {"status": "no_trade"}
    except Exception as e:
        print(f"Error running trading algorithm for ticker {ticker}: {str(e)}")
        return {"status": "error", "message": str(e)}

# Endpoint to execute a trade through Alpaca
@app.post("/execute_trade")
async def execute_trade(trade_object: TradeObject):
    try:
        if trade_object.action == "buy":
            alpaca_client.submit_order(
                symbol=trade_object.ticker,
                qty=trade_object.position_size,
                side="buy",
                type="market",
                time_in_force="gtc"
            )
        elif trade_object.action == "sell":
            alpaca_client.submit_order(
                symbol=trade_object.ticker,
                qty=trade_object.position_size,
                side="sell",
                type="market",
                time_in_force="gtc"
            )
        
        return {"status": "trade_executed", "action": trade_object.action}
    except Exception as e:
        print(f"Error executing trade for ticker {trade_object.ticker}: {str(e)}")
        return {"status": "error", "message": str(e)}

# Helper function to process market data and create a TradeObject
def process_market_data(bars):
    # Process bars and create MarketData structure
    # (Implement market data processing here)
    pass

# Helper function to generate a TradeObject from market data
def generate_trade_object(ticker: str, market_data):
    # Implement trade signal generation logic here
    # Create and return a TradeObject instance
    pass
