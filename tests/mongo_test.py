import asyncio
import pytest
from motor.motor_asyncio import AsyncIOMotorClient

@pytest.mark.asyncio
async def test_mongo():
    try:
        client = AsyncIOMotorClient('mongodb://localhost:27017', serverSelectionTimeoutMS=3000)
        await client.server_info()
        print('✅ MongoDB está conectado!')
    except Exception as e:
        print(f'❌ Falha ao conectar no MongoDB: {e}')

if __name__ == '__main__':
    asyncio.run(test_mongo())