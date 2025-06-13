import asyncio
import pytest
from motor.motor_asyncio import AsyncIOMotorClient

@pytest.mark.asyncio
async def test_mongo():
    try:
        client = AsyncIOMotorClient('mongodb://localhost:27017', serverSelectionTimeoutMS=3000)
        await client.server_info()
        return [client]
    except Exception as e:
        return [e]

if __name__ == '__main__':
    asyncio.run(test_mongo())