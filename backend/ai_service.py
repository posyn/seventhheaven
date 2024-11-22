# AI summarization and sentiment analysis

# backend/app/services/ai_service.py

import os
import hashlib
import json
from datetime import datetime
from typing import List, Dict
from pydantic import BaseModel
from openai import OpenAI
from backend.app import SessionLocal, DataObjectsTable
from .models import DataObject
import hashlib
from .models import DataObject
from datetime import datetime

def process_data_snippet(market_data):
    try:
        headline = f"Market data for {market_data['ticker']}"
        summary = "Summary of market data..."  # Example - Replace with AI-generated summary
        interpretation = "Interpretation of market data..."  # Example - Replace with AI-generated interpretation

        return DataObject(
            headline=headline,
            date_time=datetime.now(),
            ticker=market_data["ticker"],
            industry="Finance",
            sentiment="neutral",  # Placeholder sentiment - should be generated through AI
            summary=summary,
            interpretation=interpretation,
            hash=hashlib.sha256(f"{market_data['ticker']}{datetime.now()}".encode()).hexdigest()
        )
    except Exception as e:
        print(f"Error processing data snippet: {e}")
        return None


# Load environment variables from .env file (for local development)
from dotenv import load_dotenv
load_dotenv()

# Retrieve NVIDIA API key from environment variables
NVAPI_KEY = os.environ.get('nvapi_key')
if not NVAPI_KEY:
    raise ValueError("No NVAPI_KEY found in environment variables.")

# Initialize OpenAI client for NVIDIA API
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=NVAPI_KEY
)

def generate_hash(content: str) -> str:
    """
    Generates a SHA-256 hash of the provided content string.
    """
    sha_signature = hashlib.sha256(content.encode('utf-8')).hexdigest()
    return sha_signature

def process_data_snippet(snippet: str, date_time: datetime):
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
    response = client.chat.completions.create(
        model="nvidia/llama-3.1-nemotron-70b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        top_p=1,
        max_tokens=1024,
        stream=False
    )

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
