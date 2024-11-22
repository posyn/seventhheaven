from fastapi import APIRouter
from .data_feed import router as data_feed_router
from .trading_algo import router as trading_algo_router

api_router = APIRouter()

api_router.include_router(data_feed_router, prefix="/data_feed", tags=["data_feed"])
api_router.include_router(trading_algo_router, prefix="/trading_algo", tags=["trading_algo"])
