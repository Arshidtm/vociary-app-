import asyncio
from sqlalchemy import text
from app.db.database import get_db_async
from app.db import models

async def debug_users():
    print("--- CONNECTING TO DATABASE ---")
    async for session in get_db_async():
        print("--- FETCHING USERS ---")
        try:
            result = await session.execute(text("SELECT id, username, email FROM users"))
            users = result.fetchall()
            print(f"Found {len(users)} users:")
            for u in users:
                print(f"ID: {u.id} | Username: {u.username} | Email: {u.email}")
            
            # Check Sequence
            print("\n--- CHECKING SEQUENCE ---")
            # Assuming table is 'users' and column is 'id', usually sequence is 'users_id_seq'
            try:
                # Get max id
                max_id = 0
                if users:
                    max_id = max(u.id for u in users)
                
                print(f"Max ID in table: {max_id}")

                # Reset sequence
                print(f"--- RESETTING SEQUENCE TO {max_id + 1} ---")
                await session.execute(text(f"SELECT setval('users_id_seq', {max_id + 1}, false)"))
                await session.commit()
                print("Sequence reset successfully.")
                
            except Exception as e:
                print(f"Error checking/resetting sequence: {e}")

        except Exception as e:
            print(f"Error fetching users: {e}")
        
        break # Only need one session

if __name__ == "__main__":
    asyncio.run(debug_users())
