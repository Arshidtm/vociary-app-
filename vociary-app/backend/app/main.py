# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager

# Import configuration and setup files
from .core.settings import settings
from .db.database import init_db_async
from .api import endpoints # Import the API router module

from dotenv import load_dotenv
load_dotenv()

# --- 1. Database and Application Context Manager ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager that handles startup and shutdown events for the application.
    """
    print("Application Startup: Initializing services...")
    
    # 1. Run database initialization (creates tables if they don't exist)
    try:
        await init_db_async()
    except Exception as e:
        print(f"FATAL ERROR during DB startup: {e}")
        # In a production environment, you might log this and exit
        
    yield # Application continues running here

    print("Application Shutdown: Cleaning up...")
    # Add any shutdown code here (e.g., closing resource pools)


# --- 2. Application Initialization ---

app = FastAPI(
    title="AuraJournal AI Backend",
    version=settings.API_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan # Attach the context manager
)

# --- 3. CORS Middleware Configuration ---

# This allows your frontend (e.g., React on localhost:3000) to communicate with this backend.
app.add_middleware(
    CORSMiddleware,
    # settings.CORS_ORIGINS reads the FRONTEND_URL from your .env file
    allow_origins=settings.CORS_ORIGINS, 
    allow_credentials=True,
    allow_methods=["*"], # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"], # Allow all headers
)

# --- 4. Include API Routers ---

# All endpoints in endpoints.py will be prefixed with /api/v1/entries
app.include_router(endpoints.router, prefix=f"/api/{settings.API_VERSION}")


# --- 5. Root Endpoint (Optional sanity check) ---

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "AuraJournal Backend is running."}


# --- 6. Uvicorn Runner (Only for direct script execution) ---
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True, 
        log_level="info"
    )