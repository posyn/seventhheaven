import React, { useEffect, useState } from 'react';
import axios from 'axios';

type DataObject = {
  id?: number;
  headline?: string;
  date_time?: string;
  ticker?: string;
  industry?: string;
  sentiment?: string;
  summary?: string;
  interpretation?: string;
  hash?: string;
};

const DataFeed: React.FC = () => {
  const [dataFeed, setDataFeed] = useState<DataObject[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const result = await axios.get('/api/data_feed');
        setDataFeed(result.data.data);
      } catch (error) {
        console.error("Error fetching data feed", error);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="p-6 bg-gray-100 min-h-screen">
      <h1 className="text-3xl font-bold mb-4">Data Feed</h1>
      <ul className="space-y-4">
        {dataFeed.map((data, index) => (
          <li key={index} className="p-4 border rounded-md shadow-sm bg-white">
            <h3 className="font-semibold text-lg">{data.headline}</h3>
            <p><strong>Date & Time:</strong> {data.date_time}</p>
            <p><strong>Ticker:</strong> {data.ticker}</p>
            <p><strong>Industry:</strong> {data.industry}</p>
            <p><strong>Sentiment:</strong> {data.sentiment}</p>
            <p><strong>Summary:</strong> {data.summary}</p>
            <p><strong>Interpretation:</strong> {data.interpretation}</p>
            <p><strong>Hash:</strong> {data.hash}</p>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default DataFeed;
