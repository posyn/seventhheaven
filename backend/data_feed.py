# Data feed endpoints

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from .models import DataObject
from database import SessionLocal, DataObjectsTable

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/data_feed", response_model=List[DataObject])
def get_data_feed(limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    """
    Retrieve a list of DataObjects from the database, ordered by date_time descending.
    """
    data_objects = db.query(DataObjectsTable).order_by(DataObjectsTable.date_time.desc()).offset(offset).limit(limit).all()
    return data_objects

@router.get("/data_feed/{id}", response_model=DataObject)
def get_data_object(id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single DataObject by its ID.
    """
    data_object = db.query(DataObjectsTable).filter(DataObjectsTable.id == id).first()
    if data_object:
        return data_object
    else:
        raise HTTPException(status_code=404, detail="DataObject not found")
