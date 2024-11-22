# Trading-related endpoints
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from app.models.trade_object_model import TradeObject
from app.database import SessionLocal, TradeObjectsTable

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/trades", response_model=List[TradeObject])
def get_trades(limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    """
    Retrieve a list of TradeObjects from the database, ordered by date_time descending.
    """
    trade_objects = db.query(TradeObjectsTable).order_by(TradeObjectsTable.date_time.desc()).offset(offset).limit(limit).all()
    return trade_objects

@router.get("/trades/{id}", response_model=TradeObject)
def get_trade_object(id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single TradeObject by its ID.
    """
    trade_object = db.query(TradeObjectsTable).filter(TradeObjectsTable.id == id).first()
    if trade_object:
        return trade_object
    else:
        raise HTTPException(status_code=404, detail="TradeObject not found")
