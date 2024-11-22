import React, { useEffect, useState } from 'react';
import axios from 'axios';

type TradeObject = {
  id?: number;
  ticker?: string;
  date_time?: string;
  entry_price?: number;
  stop_loss?: number;
  position_size?: number;
  price_targets?: { [key: string]: number };
  rsi?: number;
  macd?: { macd_line: number[]; signal_line: number[] };
  last_volume?: number;
  average_volume?: number;
  iv?: number;
  hash?: string;
  action?: string; // Added "action" to determine if it's a buy or sell action
};

const TradesFeed: React.FC = () => {
  const [trades, setTrades] = useState<TradeObject[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const result = await axios.get('/api/trades');
        setTrades(result.data.trades);
      } catch (error) {
        console.error("Error fetching trades", error);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="p-6 bg-gray-100 min-h-screen">
      <h1 className="text-3xl font-bold mb-4">Trades Feed</h1>
      <ul className="space-y-4">
        {trades.map((trade, index) => (
          <li key={index} className="p-4 border rounded-md shadow-sm bg-white">
            <h3 className="font-semibold text-lg">{trade.ticker} - {trade.action}</h3>
            <p><strong>Date & Time:</strong> {trade.date_time}</p>
            <p><strong>Entry Price:</strong> ${trade.entry_price}</p>
            <p><strong>Stop Loss:</strong> ${trade.stop_loss}</p>
            <p><strong>Position Size:</strong> {trade.position_size}</p>
            <p><strong>RSI:</strong> {trade.rsi}</p>
            <p><strong>Last Volume:</strong> {trade.last_volume}</p>
            <p><strong>Average Volume:</strong> {trade.average_volume}</p>
            <p><strong>Implied Volatility (IV):</strong> {trade.iv}</p>
            <p><strong>Price Targets:</strong></p>
            <ul className="ml-4">
              {trade.price_targets && Object.entries(trade.price_targets).map(([key, value]) => (
                <li key={key}>{key}: ${value}</li>
              ))}
            </ul>
            <p><strong>MACD:</strong></p>
            <ul className="ml-4">
              <li><strong>MACD Line:</strong> {trade.macd?.macd_line.join(', ')}</li>
              <li><strong>Signal Line:</strong> {trade.macd?.signal_line.join(', ')}</li>
            </ul>
            <p><strong>Hash:</strong> {trade.hash}</p>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default TradesFeed;
