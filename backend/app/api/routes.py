# API route definitions
from fastapi import APIRouter

from app.api.data_feed import router as data_feed_router
from app.api.trades import router as trades_router

api_router = APIRouter()
api_router.include_router(data_feed_router, tags=["data_feed"])
api_router.include_router(trades_router, tags=["trades"])