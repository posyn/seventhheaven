# AI summarization and sentiment analysis
# backend/app/services/ai_service.py

import os
import hashlib
import json
from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel
from dotenv import load_dotenv
from backend.app import SessionLocal, DataObjectsTable
from .models import DataObject
from openai import OpenAI  # Assuming OpenAI client is valid for NVIDIA integration

# Load environment variables from .env file (for local development)
load_dotenv()

# Retrieve NVIDIA API key from environment variables
NVAPI_KEY = os.getenv('nvapi_key')
if not NVAPI_KEY:
    raise ValueError("No NVAPI_KEY found in environment variables.")

# Initialize OpenAI client for NVIDIA API (assuming OpenAI library works for this integration)
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=NVAPI_KEY
)

# Utility to generate hash
def generate_hash(content: str) -> str:
    """
    Generates a SHA-256 hash of the provided content string.
    """
    sha_signature = hashlib.sha256(content.encode('utf-8')).hexdigest()
    return sha_signature

# Function to process a market data snippet using the AI model
def process_data_snippet(snippet: str, date_time: datetime) -> Optional[DataObject]:
    """
    This function processes market data, summarizing it with AI and providing interpretation, sentiment, etc.
    Args:
        snippet (str): The market data snippet to be processed.
        date_time (datetime): The date and time of the data snippet.
    
    Returns:
        Optional[DataObject]: A DataObject with all relevant information or None if an error occurs.
    """
    # Prepare the prompt for the AI model
    prompt = f"""
    Data Snippet:
    {snippet}

    Instructions:
    1. Generate a summary (3-5 sentences).
    2. Generate an interpretation (2-4 sentences).
    3. Create a headline (>10 words).
    4. Identify related industries and tickers.
    5. Determine the sentiment (bullish, neutral, bearish) for each ticker/industry.

    Please provide the outputs in the following JSON format:
    {{
        "headline": "...",
        "summary": "...",
        "interpretation": "...",
        "tickers": ["..."],
        "industries": ["..."],
        "sentiments": {{
            "ticker_or_industry": "bullish/bearish/neutral",
            ...
        }}
    }}
    """

    # Call the AI model
    try:
        response = client.chat.completions.create(
            model="llama-3.1-nemotron-70b-instruct",  # Use the model specified by you
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            top_p=1,
            max_tokens=1024,
            stream=False
        )
    except Exception as e:
        print(f"Error calling AI model: {e}")
        return None

    # Extract the AI's response
    ai_content = response.choices[0].message['content']

    # Parse the AI's response as JSON
    try:
        ai_output = json.loads(ai_content)
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"AI Response: {ai_content}")
        return None

    # Combine fields to create a unique content string for hashing
    content_to_hash = (
        (ai_output.get('headline', '').strip().lower()) +
        (ai_output.get('summary', '').strip().lower()) +
        (ai_output.get('interpretation', '').strip().lower()) +
        ','.join([ticker.strip().upper() for ticker in ai_output.get('tickers', [])]) +
        ','.join([industry.strip().lower() for industry in ai_output.get('industries', [])]) +
        ','.join([f"{k.strip().upper()}:{v.strip().lower()}" for k, v in ai_output.get('sentiments', {}).items()])
    )

    # Generate the hash
    data_hash = generate_hash(content_to_hash)

    # Create DataObject instance
    data_object = DataObject(
        headline=ai_output.get('headline'),
        date_time=date_time,
        ticker=", ".join(ai_output.get('tickers', [])),
        industry=", ".join(ai_output.get('industries', [])),
        sentiment=", ".join([f"{k}: {v}" for k, v in ai_output.get('sentiments', {}).items()]),
        summary=ai_output.get('summary'),
        interpretation=ai_output.get('interpretation'),
        hash=data_hash
    )

    return data_object

# Example usage of the AI processing function (for testing purposes)
if __name__ == "__main__":
    example_snippet = "The stock price of ABC Inc. rose by 5% today after announcing its quarterly earnings, which exceeded expectations by 20%."
    date_time = datetime.now()
    result = process_data_snippet(example_snippet, date_time)
    if result:
        print(result.dict())
    else:
        print("Failed to generate a DataObject.")