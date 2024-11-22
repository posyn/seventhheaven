import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

// Define types for EquityCurvePoint and Trade
type EquityCurvePoint = {
  date: string;
  value: number;
};

type Trade = {
  ticker: string;
  action: string;
  entry_price: number;
  position_size: number;
  date_time: string;
};

// Dashboard Component
const Dashboard: React.FC = () => {
  const [capital, setCapital] = useState<number>(0);
  const [equityCurve, setEquityCurve] = useState<EquityCurvePoint[]>([]);
  const [sp500Data, setSp500Data] = useState<EquityCurvePoint[]>([]);
  const [nasdaqData, setNasdaqData] = useState<EquityCurvePoint[]>([]);
  const [trades, setTrades] = useState<Trade[]>([]);
  const [tickers, setTickers] = useState<string[]>([]);

  // Fetch data for Dashboard
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch trades data
        const tradesResult = await axios.get('/api/trades');
        const tradesData = tradesResult.data.trades;
        setTrades(tradesData);
        setCapital(tradesResult.data.capital);

        // Extract tickers from TradeObjects
        const uniqueTickers = Array.from(new Set(tradesData.map((trade: Trade) => trade.ticker)));
        setTickers(uniqueTickers);

        // Fetch paper trading equity curve data
        const equityResult = await axios.get('/api/equity_curve');
        setEquityCurve(equityResult.data.equityCurve);

        // Fetch market indices data for comparison
        const sp500Result = await axios.get('/api/market_data/sp500'); // Assuming endpoint exists
        setSp500Data(sp500Result.data.marketData);

        const nasdaqResult = await axios.get('/api/market_data/nasdaq'); // Assuming endpoint exists
        setNasdaqData(nasdaqResult.data.marketData);
      } catch (error) {
        console.error("Error fetching data", error);
      }
    };
    fetchData();
  }, []);

  // Trigger full backend process for all tickers in trades
  useEffect(() => {
    const triggerFullProcessForAllTickers = async () => {
      try {
        for (const ticker of tickers) {
          await axios.post('/api/run_full_process', { ticker });
          console.log(`Full process triggered successfully for ticker: ${ticker}`);
        }
      } catch (error) {
        console.error("Error triggering full process", error);
      }
    };

    if (tickers.length > 0) {
      triggerFullProcessForAllTickers();
    }
  }, [tickers]);

  // Chart data for comparison between paper trading and market indices
  const chartData = {
    labels: equityCurve.map((point) => point.date),
    datasets: [
      {
        label: 'Algorithm Equity Curve',
        data: equityCurve.map((point) => point.value),
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 2,
        fill: false,
      },
      {
        label: 'S&P 500',
        data: sp500Data.map((point) => point.value),
        borderColor: 'rgba(255, 99, 132, 1)',
        borderWidth: 2,
        fill: false,
      },
      {
        label: 'NASDAQ',
        data: nasdaqData.map((point) => point.value),
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 2,
        fill: false,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Paper Trading Performance vs Market Indices',
      },
    },
  };

  return (
    <div className="p-6 bg-gray-100 min-h-screen">
      <h1 className="text-3xl font-bold mb-4">Dashboard</h1>

      <p className="text-lg mb-2">Total Capital: ${capital}</p>

      {/* Line Chart for paper trading vs market indices */}
      <div className="mt-8 bg-white p-6 rounded-md shadow-md">
        <Line data={chartData} options={chartOptions} />
      </div>

      {/* List of trades */}
      <div className="mt-8 bg-white p-6 rounded-md shadow-md">
        <h2 className="text-2xl font-bold mb-4">Trade History</h2>
        <ul className="space-y-4">
          {trades.map((trade, index) => (
            <li key={index} className="p-4 border rounded-md shadow-sm bg-gray-50">
              <p><strong>Ticker:</strong> {trade.ticker}</p>
              <p><strong>Action:</strong> {trade.action}</p>
              <p><strong>Entry Price:</strong> ${trade.entry_price}</p>
              <p><strong>Position Size:</strong> {trade.position_size}</p>
              <p><strong>Date:</strong> {trade.date_time}</p>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default Dashboard;
