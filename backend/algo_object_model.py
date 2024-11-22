from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

# Assuming you already have a class for TechnicalIndicators defined elsewhere.
class TechnicalIndicators(BaseModel):
    rsi: Optional[float]
    macd: Optional[Dict[str, float]]  # e.g., {'macd_line': value, 'signal_line': value}
    atr: Optional[float]
    bollinger_bands: Optional[Dict[str, float]]  # e.g., {'upper': value, 'lower': value, 'middle': value}

# AlgoObject schema for tracking algorithmic trades and backtesting
class Position(BaseModel):
    entry_price: float
    entry_date: datetime
    exit_price: Optional[float] = None
    exit_date: Optional[datetime] = None
    quantity: int
    profit_loss: Optional[float] = None
    stop_loss: float
    trade_object_id: int  # Reference to TradeObject

    class Config:
        from_attributes = True  # Updated for Pydantic v2


class AlgoObject(BaseModel):
    id: Optional[int] = None
    ticker: str
    date_time: datetime
    action: str  # 'BUY', 'SELL', 'HOLD'
    position: Optional[Position] = None
    indicators_snapshot: Optional[TechnicalIndicators] = None
    cumulative_profit_loss: float
    backtest_start_date: Optional[datetime] = None  # For historical analysis
    backtest_end_date: Optional[datetime] = None
    paper_trade: bool  # True if paper trading, False if backtest
    trade_object_id: Optional[int] = None  # Reference to TradeObject that triggered this algo action
    hash: Optional[str] = None

    class Config:
        from_attributes = True  # Updated for Pydantic v2


# Optional: Strategy Performance Tracking
class StrategyPerformance(BaseModel):
    id: Optional[int] = None
    start_date: datetime
    end_date: datetime
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    avg_profit_per_trade: float
    max_drawdown: float
    sharpe_ratio: Optional[float] = None
    strategy_signals_weights: Dict[str, float]  # Weight/effectiveness of each signal
    hash: Optional[str] = None

    class Config:
        from_attributes = True  # Updated for Pydantic v2
