# TradeObject schema
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class TradeObject(BaseModel):
    id: Optional[int]
    ticker: Optional[str]
    date_time: Optional[datetime]
    price: Optional[float]
    rsi: Optional[float]
    macd: Optional[Dict[str, float]]  # Assuming MACD is a dictionary
    last_volume: Optional[int]
    average_volume: Optional[int]
    iv: Optional[float]
    hash: Optional[str]

    class Config:
        orm_mode = True