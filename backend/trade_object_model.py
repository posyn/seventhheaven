from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Tuple
from datetime import datetime

class Greeks(BaseModel):
    delta: Optional[float] = Field(None, description="Probability of price movement")
    gamma: Optional[float] = Field(None, description="Rate of change in delta")
    theta: Optional[float] = Field(None, description="Time decay indicator")
    vega: Optional[float] = Field(None, description="Volatility sensitivity")

class MACD(BaseModel):
    macd_line: Optional[float]
    signal_line: Optional[float]
    histogram: Optional[float]
    is_bullish_crossover: Optional[bool] = Field(None, description="MACD line crosses above signal")
    above_zero_line: Optional[bool] = Field(None, description="MACD above zero indicating momentum")
    histogram_increasing: Optional[bool] = Field(None, description="Increasing distance between MACD and signal")

class RSI(BaseModel):
    value: Optional[float]
    is_oversold: Optional[bool] = Field(None, description="RSI below 30")
    crossed_above_30: Optional[bool] = Field(None, description="Recently crossed above 30")
    bullish_swing: Optional[bool] = Field(None, description="Bullish swing pattern detected")
    trend_strength: Optional[float] = Field(None, description="Strength of current trend")

class Volume(BaseModel):
    current: Optional[int]
    average: Optional[float]
    ratio: Optional[float] = Field(None, description="Current volume / average volume")
    is_high: Optional[bool] = Field(None, description="Volume > 200% average")
    trend: Optional[str] = Field(None, description="increasing/decreasing")

class PriceTargets(BaseModel):
    entry: Optional[float]
    stop_loss: Optional[float] = Field(None, description="25% below entry")
    target_1: Optional[float] = Field(None, description="First profit target")
    target_2: Optional[float] = Field(None, description="Second profit target")
    target_3: Optional[float] = Field(None, description="Final profit target")
    risk_reward_ratio: Optional[float]

class FiftyTwoWeekMetrics(BaseModel):
    low: Optional[float]
    high: Optional[float]
    current_distance_from_low: Optional[float] = Field(None, description="% above 52-week low")
    reversal_signals: Optional[bool] = Field(None, description="Bullish reversal patterns near low")

class TechnicalIndicators(BaseModel):
    macd: Optional[MACD]
    rsi: Optional[RSI]
    volume: Optional[Volume]
    implied_volatility: Optional[float]
    greeks: Optional[Greeks]
    fifty_two_week: Optional[FiftyTwoWeekMetrics]
    bollinger_bands: Optional[Dict[str, float]]
    moving_averages: Optional[Dict[str, float]]

class PositionInfo(BaseModel):
    size: Optional[int]
    value: Optional[float]
    risk_amount: Optional[float]
    margin_requirement: Optional[float]
    max_loss: Optional[float]
    expected_profit: Optional[float]
    holding_period: Optional[str] = Field(None, description="Expected holding timeframe (6-12 months)")

class TradeObject(BaseModel):
    id: Optional[int]
    ticker: Optional[str]
    date_time: Optional[datetime]
    
    # Price Information
    entry_price: Optional[float]
    current_price: Optional[float]
    last_update_time: Optional[datetime]
    
    # Analysis
    indicators: Optional[TechnicalIndicators]
    price_targets: Optional[PriceTargets]
    position: Optional[PositionInfo]
    
    # Trade Status
    status: Optional[str] = Field(None, description="open/closed/pending")
    entry_signals: Optional[Dict[str, bool]] = Field(
        None, 
        description="Which conditions triggered entry"
    )
    exit_signals: Optional[Dict[str, bool]] = Field(
        None, 
        description="Current exit conditions status"
    )
    
    # Related Data
    related_data_ids: Optional[List[int]] = Field(
        None, 
        description="Links to related DataObjects"
    )
    
    # Performance
    profit_loss: Optional[float]
    profit_loss_percent: Optional[float]
    trade_duration: Optional[float] = Field(
        None, 
        description="Duration in days since entry"
    )
    
    # Charts
    chart_data: Optional[Dict[str, List[float]]] = Field(
        None,
        description="Historical price and indicator data for charts"
    )
    
    hash: Optional[str]

    class Config:
        orm_mode = True

    def check_entry_conditions(self) -> bool:
        """Check if all entry conditions are met"""
        if not self.indicators:
            return False

        conditions = {
            # MACD Conditions
            'macd_bullish_cross': self.indicators.macd.is_bullish_crossover,
            'macd_above_zero': self.indicators.macd.above_zero_line,
            'macd_increasing': self.indicators.macd.histogram_increasing,
            
            # RSI Conditions
            'rsi_oversold': self.indicators.rsi.is_oversold,
            'rsi_cross_above_30': self.indicators.rsi.crossed_above_30,
            'rsi_bullish_swing': self.indicators.rsi.bullish_swing,
            
            # Volume Conditions
            'high_volume': self.indicators.volume.is_high,
            
            # 52-Week Conditions
            'near_52_week_low': self.indicators.fifty_two_week.reversal_signals,
            
            # Greeks & IV Conditions
            'favorable_greeks': all([
                self.indicators.greeks.delta > 0.7,
                self.indicators.greeks.gamma > 0.05,
                abs(self.indicators.greeks.theta) < 0.02,
                self.indicators.greeks.vega > 0.1
            ])
        }
        
        return all(conditions.values())

    def check_exit_conditions(self) -> Tuple[bool, str]:
        """Check if any exit conditions are met"""
        if not self.indicators or not self.price_targets:
            return False, "Missing indicators or price targets"

        # Stop loss hit
        if self.current_price <= self.price_targets.stop_loss:
            return True, "Stop loss triggered"

        # Target reached
        if self.current_price >= self.price_targets.target_1:
            return True, "Price target reached"

        # Volume decline
        if (self.indicators.volume.ratio < 0.5 and 
            self.indicators.volume.trend == "decreasing"):
            return True, "Volume declining significantly"

        # Bearish reversal
        if (not self.indicators.macd.above_zero_line and 
            not self.indicators.macd.is_bullish_crossover):
            return True, "Bearish reversal detected"

        return False, "No exit conditions met"

    class Config:
        orm_mode = True