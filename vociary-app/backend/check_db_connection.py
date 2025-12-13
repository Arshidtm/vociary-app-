import asyncio
import sys
import os

# Ensure we can import from app
sys.path.append(os.getcwd())

from app.db.database import async_engine
from sqlalchemy import text

async def check_connection():
    print("Testing database connection...")
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print(f"Connection Successful! Result: {result.scalar()}")
    except Exception as e:
        print(f"Connection Failed: {e}")
        # Print detailed connection info for debugging
        print(f"URL: {async_engine.url}")

if __name__ == "__main__":
    asyncio.run(check_connection())
