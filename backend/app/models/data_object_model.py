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