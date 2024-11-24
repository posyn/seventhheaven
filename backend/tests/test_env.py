from dotenv import load_dotenv
import os

def test_polygon_key():
    # Load .env file
    load_dotenv()
    
    # Get the key
    key = os.getenv("POLYGON_API_KEY")
    
    print("Key exists:", bool(key))
    if key:
        print("Key length:", len(key))
        print("First few characters:", key[:4] + "..." if key else None)

if __name__ == "__main__":
    test_polygon_key()