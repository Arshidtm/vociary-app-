
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def test_connection():
    try:
        from app.core.settings import settings
        from urllib.parse import quote_plus
        
        # Manually construct URL with encoded password to test fix
        encoded_password = quote_plus(settings.DB_PASSWORD)
        encoded_user = quote_plus(settings.DB_USER)
        
        # Reconstruct URL safely
        url = (
            f"postgresql+asyncpg://{encoded_user}:{encoded_password}@"
            f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
        )
        
        print(f"\n--- Testing Connection to {url.replace(encoded_password, '******')} ---")
        engine = create_async_engine(url)
        
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT current_user;"))
            user = result.scalar()
            print(f"SUCCESS! Connected. Current Database User: {user}")
            
    except Exception as e:
        print(f"CONNECTION FAILED: {e}")

if __name__ == "__main__":
    try:
        from app.core.settings import settings
        print("--- Loaded Settings ---")
        print(f"DB_USER: '{settings.DB_USER}'")
        print(f"DB_PASSWORD: '{settings.DB_PASSWORD}'") 
        print(f"DB_HOST: '{settings.DB_HOST}'")
        print(f"DB_PORT: '{settings.DB_PORT}'")
        print(f"DB_NAME: '{settings.DB_NAME}'")
    except Exception as e:
        print(f"Error loading settings: {e}")

    # Run the async test
    asyncio.run(test_connection())
