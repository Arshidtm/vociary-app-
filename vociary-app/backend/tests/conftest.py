# backend/tests/conftest.py

import pytest
import asyncio
from typing import AsyncGenerator
from fastapi import Depends

# 1. Imports for Testing
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncConnection
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, drop_database, database_exists # For utility

# 2. Imports from Application
from app.main import app # The main FastAPI application instance
from app.db.database import get_db_async # The production dependency to override
from app.db.models import Base # The base model for creating tables
from app.core.settings import settings 
from app.services import ai_service # To mock the AI calls

from dotenv import load_dotenv
load_dotenv()


# --- Configuration for Test Database ---
# Create a separate, unique database URL for testing (e.g., in-memory SQLite for speed)
# SQLite is often faster for unit tests, but we'll use a TEST_POSTGRES_URL for robustness if possible.
# For simplicity and speed here, we'll use an in-memory SQLite, but the process is similar for a test Postgres DB.

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:" 
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)

# --- 3. FIXTURES for Async Setup ---

# This ensures pytest can handle async test functions (Required for async clients)
@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

# --- 4. FIXTURE for Database Connection & Transaction Isolation ---

@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    """Create and drop tables for the whole test session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Teardown: not strictly necessary for :memory: SQLite, but good practice
    yield 

@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Creates a new session and transaction for each test, rolling back on exit.
    This provides transaction isolation for perfect, independent tests.
    """
    async with test_engine.connect() as connection:
        # Begin a transaction and link the session to it
        async with connection.begin() as transaction:
            AsyncTestingSessionLocal = sessionmaker(
                connection, 
                class_=AsyncSession, 
                expire_on_commit=False,
                autocommit=False,
                autoflush=False
            )
            async with AsyncTestingSessionLocal() as session:
                yield session
                # The key to isolation: Rollback the transaction after the test
                await transaction.rollback() 


# --- 5. DEPENDENCY OVERRIDE (The magic) ---

# async def override_get_db_async(session: AsyncSession = Depends(db_session)):
#     """Override the production DB dependency to use the test session fixture."""
#     yield session

# --- 6. FIXTURE for the Test Client ---

# --- 6. FIXTURE for the Test Client ---
@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Configures an HTTPX AsyncClient with the application and overrides the DB dependency.
    """
    
    # Imports needed inside the fixture for the override
    from app.db.database import get_db_async 
    from app.main import app 
    from app.services import ai_service 

    # 1. Temporarily override the dependency (THE CRITICAL FIX)
    
    # Define an async generator function that yields the test session object 
    # provided by the transactional fixture (db_session).
    async def override_get_db():
        yield db_session 

    # Apply the override
    app.dependency_overrides[get_db_async] = override_get_db 

    # 2. Mock external services (AI Service) for deterministic testing

    original_transcribe = ai_service.get_transcription
    original_generate = ai_service.generate_initial_entry
    
    async def mock_transcribe(audio_file):
        return "The presentation was great. I also ate a delicious sandwich for lunch."

    async def mock_generate(transcript):
        return f"Refined entry based on: {transcript}"

    ai_service.get_transcription = mock_transcribe
    ai_service.generate_initial_entry = mock_generate

    # 3. Create the Async Client
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test" # Dummy base URL for internal testing
    ) as client:
        yield client

    # 4. Teardown: Clear overrides and restore mocks
    app.dependency_overrides = {}
    ai_service.get_transcription = original_transcribe
    ai_service.generate_initial_entry = original_generate