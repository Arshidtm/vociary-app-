# backend/app/db/database.py (ASYNC POSTGRES CONFIGURATION)

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from ..core.settings import settings  # Import settings for secure URL
from .models import Base  # Import the Base class from our SQLAlchemy models

# --- Database URL ---
# The URL must use the 'postgresql+asyncpg' or 'postgresql+psycopg' dialect for async support.
# We will use 'postgresql+psycopg' as the modern, recommended driver with SQLAlchemy.
SQLALCHEMY_DATABASE_URL = settings.SQLALCHEMY_DATABASE_URL.replace(
    "postgresql://", "postgresql+psycopg://"
)

# --- Async Engine Configuration ---
# pool_pre_ping=True helps maintain connection reliability
async_engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, 
    echo=settings.DEBUG, # Log SQL queries if in debug mode
    pool_pre_ping=True
)

# --- Async Session Local ---
# This binds the session to the async engine. 
AsyncSessionLocal = sessionmaker(
    async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False  # Good practice to allow objects to be used after commit
)

# --- Async Dependency Function for FastAPI ---
async def get_db_async() -> AsyncSession:
    """
    An asynchronous generator function for FastAPI dependency injection.
    It yields an async session and ensures it is closed afterwards.
    """
    async with AsyncSessionLocal() as session:
        yield session

# --- Initialization Function ---
async def init_db_async():
    """
    Creates the database tables defined by the Base metadata asynchronously.
    """
    print("Attempting to connect to PostgreSQL and create tables asynchronously...")
    try:
        async with async_engine.begin() as conn:
            # Drop tables for clean start (OPTIONAL: remove in production)
            # await conn.run_sync(Base.metadata.drop_all) 
            
            # Create all tables defined in Base
            await conn.run_sync(Base.metadata.create_all)
        print("PostgreSQL tables created successfully.")
    except Exception as e:
        print(f"ERROR: Could not connect to PostgreSQL or create tables. Error: {e}")
        # Re-raise the exception to prevent the application from starting with a bad connection
        raise