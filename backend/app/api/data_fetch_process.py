# Fetch data from polygon

import os
import time
from datetime import datetime
import requests
from app.services.ai_service import process_and_save_data_snippets
from app.database import create_tables

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Retrieve Polygon API keys from environment variables
POLYGON_API_KEY = os.environ.get('polygon_api_key')
if not POLYGON_API_KEY:
    raise ValueError("No POLYGON_API_KEY found in environment variables.")

def fetch_news_articles(limit=50, after=None):
    url = 'https://api.polygon.io/v2/reference/news'
    params = {
        'limit': limit,
        'order': 'descending',  # Fetch newest articles first
        'sort': 'published_utc',
        'apiKey': POLYGON_API_KEY
    }
    if after:
        params['published_utc.gt'] = after.strftime("%Y-%m-%dT%H:%M:%SZ")

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        articles = data.get('results', [])
        snippets = []
        for article in articles:
            content = article.get('description') or article.get('title') or ''
            date_time_str = article.get('published_utc')
            date_time = datetime.strptime(date_time_str, "%Y-%m-%dT%H:%M:%SZ") if date_time_str else datetime.utcnow()
            snippets.append({
                'content': content,
                'date_time': date_time
            })
        return snippets
    else:
        print(f"Error fetching news: {response.status_code} - {response.text}")
        return []

def main():
    # Create database tables if they don't exist
    create_tables()
    
    last_processed_time = None  # Keep track of the last processed article time

    while True:
        print(f"Fetching news articles at {datetime.utcnow()}...")
        snippets = fetch_news_articles(limit=50, after=last_processed_time)
        if snippets:
            print(f"Processing {len(snippets)} articles...")
            process_and_save_data_snippets(snippets)
            # Update the last processed time to the most recent article's time
            last_processed_time = snippets[0]['date_time']  # Newest article
        else:
            print("No new articles to process.")
        
        # Optional: Short sleep to prevent overwhelming the API
        time.sleep(1)  # Sleep for 1 second

if __name__ == '__main__':
    main()
