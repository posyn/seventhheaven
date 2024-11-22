# main.py in /Users/collin/seventhheaven/

from fastapi import FastAPI
from .routes import api_router

app = FastAPI()

# Include the central router that aggregates all routes
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
