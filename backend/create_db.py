"""Script to create the database if it doesn't exist."""

import asyncio
import asyncpg


async def create_database():
    # Connect to default postgres database
    conn = await asyncpg.connect(
        host="localhost",
        port=5433,
        user="postgres",
        password="Ti123!@#",
        database="postgres",
    )
    
    try:
        # Check if webconsig database exists
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = 'webconsig'"
        )
        
        if not exists:
            # Create the database (cannot be done inside a transaction)
            await conn.execute("CREATE DATABASE webconsig")
            print("✅ Database 'webconsig' created successfully")
        else:
            print("✅ Database 'webconsig' already exists")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(create_database())
