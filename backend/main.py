# Entry point for the backend server
from fastapi import FastAPI
from app.api.routes import api_router
from app.database import create_tables
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Seventh Heaven API")

# Include API routes
app.include_router(api_router)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables upon startup
@app.on_event("startup")
async def startup_event():
    create_tables()