import os
import requests
import json
import time

# Load your Polygon API key from environment variables
POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')

# Base URLs
TICKERS_URL = f'https://api.polygon.io/v3/reference/tickers?market=stocks&active=true&apiKey={POLYGON_API_KEY}'
RSI_URL_TEMPLATE = 'https://api.polygon.io/v1/indicators/rsi/{ticker}?timespan=day&adjusted=true&window=14&series_type=close&order=desc&limit=1&apiKey={POLYGON_API_KEY}'

# Directory to save JSON files
OUTPUT_DIR = 'tickers_with_rsi_below_40'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_all_tickers():
    tickers = []
    next_url = TICKERS_URL
    while next_url:
        response = requests.get(next_url)
        data = response.json()
        if 'results' in data:
            tickers.extend([item['ticker'] for item in data['results']])
        # Handle pagination
        next_url = data['next_url'] if 'next_url' in data else None
        if next_url:
            next_url += f'&apiKey={POLYGON_API_KEY}'
        # Respect API rate limits
        time.sleep(0.25)  # Adjust sleep time as needed
    return tickers

def get_rsi_for_ticker(ticker):
    url = RSI_URL_TEMPLATE.format(ticker=ticker, api_key=POLYGON_API_KEY)
    response = requests.get(url)
    data = response.json()
    if 'results' in data and 'values' in data['results']:
        rsi_value = data['results']['values'][0]['value']
        return rsi_value
    else:
        return None

def save_ticker_data(ticker, data):
    filename = f"{OUTPUT_DIR}/{ticker}.json"
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def main():
    tickers = get_all_tickers()
    print(f"Total tickers retrieved: {len(tickers)}")

    tickers_with_low_rsi = []

    for index, ticker in enumerate(tickers):
        try:
            rsi = get_rsi_for_ticker(ticker)
            if rsi is not None and rsi < 40:
                print(f"{ticker}: RSI = {rsi}")
                # Save the ticker data as JSON
                ticker_data = {
                    'ticker': ticker,
                    'rsi': rsi
                }
                save_ticker_data(ticker, ticker_data)
                tickers_with_low_rsi.append(ticker)
            # Optional: Progress indicator
            if index % 100 == 0:
                print(f"Processed {index} tickers...")
            # Respect API rate limits
            time.sleep(0.25)  # Adjust sleep time as needed
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue

    print(f"Total tickers with RSI below 40: {len(tickers_with_low_rsi)}")

if __name__ == '__main__':
    main()
