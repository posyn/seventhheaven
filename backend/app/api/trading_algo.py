# Trading algorithms
from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from polygon import RESTClient
from dataclasses import dataclass
from scipy.stats import norm
from .models import TradeObject, TechnicalIndicators, MACD, Greeks

@dataclass
class MarketData:
    close_prices: List[float]
    high_prices: List[float]
    low_prices: List[float]
    volumes: List[int]
    rsi: List[float]
    macd: Dict[str, List[float]]
    iv: float
    greeks: Greeks
    fifty_two_week_low: float
    bollinger_bands: Dict[str, List[float]]
    atr: List[float]
    polygon_data: Dict[str, float]  # Data from Polygon relevant to the ticker

class EnhancedTradingAlgorithm:
    def __init__(self, polygon_key: str, initial_capital: float = 100000):
        self.client = RESTClient(polygon_key)
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.risk_per_trade = 0.02  # 2% risk per trade
        self.position_sizing_atr_multiplier = 2
        
        # Technical parameters
        self.rsi_period = 14
        self.macd_periods = (12, 26, 9)
        self.bollinger_period = 20
        self.atr_period = 14
        self.volume_threshold = 2.0

    def calculate_bollinger_bands(self, prices: List[float]) -> Dict[str, List[float]]:
        try:
            df = pd.Series(prices)
            sma = df.rolling(window=self.bollinger_period).mean()
            std = df.rolling(window=self.bollinger_period).std()
            upper = sma + (std * 2)
            lower = sma - (std * 2)
            return {
                'middle': sma.tolist(),
                'upper': upper.tolist(),
                'lower': lower.tolist()
            }
        except Exception as e:
            print(f"Error calculating Bollinger Bands: {str(e)}")
            return {'middle': [], 'upper': [], 'lower': []}

    def calculate_atr(self, high: List[float], low: List[float], close: List[float]) -> List[float]:
        try:
            high_low = np.array(high) - np.array(low)
            high_close = np.abs(np.array(high) - np.array(close[:-1]))
            low_close = np.abs(np.array(low) - np.array(close[:-1]))
            
            ranges = np.vstack([high_low, high_close, low_close])
            true_range = np.max(ranges, axis=0)
            
            atr = pd.Series(true_range).rolling(window=self.atr_period).mean()
            return atr.tolist()
        except Exception as e:
            print(f"Error calculating ATR: {str(e)}")
            return []

    def calculate_position_size(self, current_price: float, stop_loss: float, market_data: MarketData) -> int:
        try:
            risk_amount = self.current_capital * self.risk_per_trade
            risk_per_share = current_price - stop_loss
            position_size = risk_amount / risk_per_share
            
            # Adjust based on volatility (ATR)
            atr = market_data.atr[-1]
            volatility_adjusted_size = position_size * (atr / current_price)
            
            # Adjust based on volume constraints
            avg_volume = sum(market_data.volumes[-20:]) / 20
            volume_constraint = avg_volume * 0.01  # Don't take more than 1% of average volume
            
            return min(int(volatility_adjusted_size), int(volume_constraint))
        except Exception as e:
            print(f"Error calculating position size: {str(e)}")
            return 0

    def calculate_price_targets(self, entry_price: float, market_data: MarketData) -> Dict[str, float]:
        try:
            atr = market_data.atr[-1]
            bb = market_data.bollinger_bands
            
            # Multiple target levels based on different criteria
            targets = {
                'atr_target': entry_price + (atr * 3),  # 3 ATR target
                'bb_target': bb['upper'][-1],  # Upper Bollinger Band
                'fibonacci_target': entry_price + ((entry_price - market_data.fifty_two_week_low) * 1.618),  # Fibonacci extension
                'risk_reward_target': entry_price + ((entry_price - market_data.fifty_two_week_low) * 2)  # 2R target
            }
            
            # Weight the targets based on market conditions
            weighted_target = (
                targets['atr_target'] * 0.3 +
                targets['bb_target'] * 0.3 +
                targets['fibonacci_target'] * 0.2 +
                targets['risk_reward_target'] * 0.2
            )
            
            targets['weighted_target'] = weighted_target
            return targets
        except Exception as e:
            print(f"Error calculating price targets: {str(e)}")
            return {}

    def check_sell_conditions(self, trade_object: TradeObject, market_data: MarketData) -> Tuple[bool, str]:
        try:
            current_price = market_data.close_prices[-1]
            
            # Stop loss check
            if current_price <= trade_object.stop_loss:
                return True, "Stop loss triggered"

            # Target reached check
            if current_price >= trade_object.price_targets['weighted_target']:
                return True, "Price target reached"

            # RSI overbought
            if market_data.rsi[-1] > 70:
                return True, "RSI overbought"

            # MACD bearish crossover
            if (market_data.macd['macd_line'][-2] > market_data.macd['signal_line'][-2] and
                market_data.macd['macd_line'][-1] < market_data.macd['signal_line'][-1]):
                return True, "MACD bearish crossover"

            # Volume drop
            current_volume = market_data.volumes[-1]
            avg_volume = sum(market_data.volumes[-20:]) / 20
            if current_volume < (avg_volume * 0.5):
                return True, "Volume declining significantly"

            # Bollinger Band squeeze exit
            bb = market_data.bollinger_bands
            if current_price > bb['upper'][-1]:
                return True, "Price above upper Bollinger Band"

            # Trailing stop based on ATR
            trailing_stop = current_price - (market_data.atr[-1] * 2)
            if trailing_stop > trade_object.stop_loss:
                trade_object.stop_loss = trailing_stop

            return False, ""
        except Exception as e:
            print(f"Error checking sell conditions: {str(e)}")
            return False, "Error"

    async def backtest(self, ticker: str, start_date: datetime, end_date: datetime) -> Dict:
        try:
            trades = []
            equity_curve = [self.initial_capital]
            current_position = None
            
            # Fetch historical data
            bars = self.client.get_aggs(
                ticker=ticker,
                multiplier=1,
                timespan="day",
                from_=start_date,
                to=end_date
            )
            
            for i in range(len(bars)-1):
                # Create market data slice
                market_data = self.prepare_market_data(bars[:i+1])
                
                if current_position is None:
                    # Check for entry
                    trade_object = self.generate_trade_object(ticker, market_data)
                    if trade_object:
                        position_size = self.calculate_position_size(
                            trade_object.entry_price,
                            trade_object.stop_loss,
                            market_data
                        )
                        trade_object.position_size = position_size
                        trade_object.polygon_data = market_data.polygon_data  # Add Polygon data to TradeObject
                        current_position = trade_object
                        trades.append({
                            'type': 'entry',
                            'price': trade_object.entry_price,
                            'size': position_size,
                            'date': bars[i].timestamp
                        })
                else:
                    # Check for exit
                    should_sell, reason = self.check_sell_conditions(current_position, market_data)
                    if should_sell:
                        profit_loss = (bars[i].close - current_position.entry_price) * current_position.position_size
                        self.current_capital += profit_loss
                        equity_curve.append(self.current_capital)
                        trades.append({
                            'type': 'exit',
                            'price': bars[i].close,
                            'size': current_position.position_size,
                            'profit_loss': profit_loss,
                            'reason': reason,
                            'date': bars[i].timestamp
                        })
                        current_position = None

            return {
                'trades': trades,
                'equity_curve': equity_curve,
                'final_capital': self.current_capital,
                'total_return': (self.current_capital - self.initial_capital) / self.initial_capital,
                'sharpe_ratio': self.calculate_sharpe_ratio(equity_curve),
                'max_drawdown': self.calculate_max_drawdown(equity_curve)
            }
        except Exception as e:
            print(f"Error during backtest for ticker {ticker}: {str(e)}")
            return {}

    def calculate_sharpe_ratio(self, equity_curve: List[float]) -> float:
        try:
            returns = pd.Series(equity_curve).pct_change().dropna()
            return np.sqrt(252) * (returns.mean() / returns.std())
        except Exception as e:
            print(f"Error calculating Sharpe Ratio: {str(e)}")
            return 0.0

    def calculate_max_drawdown(self, equity_curve: List[float]) -> float:
        try:
            peak = equity_curve[0]
            max_dd = 0
            
            for value in equity_curve:
                if value > peak:
                    peak = value
                dd = (peak - value) / peak
                max_dd = max(max_dd, dd)
                
            return max_dd
        except Exception as e:
            print(f"Error calculating Max Drawdown: {str(e)}")
            return 0.0

    def fetch_polygon_data(self, ticker: str) -> Dict[str, float]:
        try:
            # Example: Fetch relevant financial metrics, news, and corporate actions
            financials_url = f"https://api.polygon.io/vX/reference/financials/{ticker}"
            news_url = f"https://api.polygon.io/v2/reference/news?ticker={ticker}"
            corporate_actions_url = f"https://api.polygon.io/vX/reference/corporate-actions/{ticker}"
            params = {'apiKey': self.client.api_key}

            financials = requests.get(financials_url, params=params).json()
            news = requests.get(news_url, params=params).json()
            corporate_actions = requests.get(corporate_actions_url, params=params).json()

            # Process and structure relevant data
            polygon_data = {
                'financials': financials,
                'news': news,
                'corporate_actions': corporate_actions
            }

            return polygon_data
        except Exception as e:
            print(f"Error fetching Polygon data for ticker {ticker}: {str(e)}")
            return {}

    async def run(self, ticker: str) -> Optional[TradeObject]:
        try:
            bars = self.client.get_aggs(
                ticker=ticker,
                multiplier=1,
                timespan="day",
                from_=datetime.now() - timedelta(days=365),
                to=datetime.now()
            )
            
            polygon_data = self.fetch_polygon_data(ticker)  # Fetch additional Polygon data
            market_data = self.prepare_market_data(bars)
            market_data.polygon_data = polygon_data  # Add Polygon data to MarketData
            
            trade_object = self.generate_trade_object(ticker, market_data)
            
            if trade_object:
                trade_object.position_size = self.calculate_position_size(
                    trade_object.entry_price,
                    trade_object.stop_loss,
                    market_data
                )
                trade_object.price_targets = self.calculate_price_targets(
                    trade_object.entry_price,
                    market_data
                )
                trade_object.polygon_data = market_data.polygon_data  # Add Polygon data to TradeObject
            
            return trade_object
            
        except Exception as e:
            print(f"Error processing ticker {ticker}: {str(e)}")
            return None
