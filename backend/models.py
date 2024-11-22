# TradeObject schema
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class TradeObject(BaseModel):
    id: Optional[int]
    ticker: Optional[str]
    date_time: Optional[datetime]
    entry_price: Optional[float]
    stop_loss: Optional[float]
    position_size: Optional[int]
    price_targets: Optional[Dict[str, float]]
    rsi: Optional[float]
    macd: Optional[Dict[str, float]]
    last_volume: Optional[int]
    average_volume: Optional[int]
    iv: Optional[float]
    action: Optional[str]  # 'buy' or 'sell'
    hash: Optional[str]

    class Config:
        orm_mode = True

# DataObject schema
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DataObject(BaseModel):
    id: Optional[int]
    headline: Optional[str]
    date_time: Optional[datetime]
    ticker: Optional[str]
    industry: Optional[str]
    sentiment: Optional[str]
    summary: Optional[str]
    interpretation: Optional[str]
    hash: Optional[str]

    class Config:
        orm_mode = True
