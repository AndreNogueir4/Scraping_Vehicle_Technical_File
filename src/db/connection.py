import os
from motor.motor_asyncio import AsyncIOMotorClient

class MongoDBConnection:
    def __init__(self):
        self._client = None
        self._db = None

    async def connect(self, uri=None, db_name=None):
        uri = uri or os.getenv('MONGO_URI', 'mongodb://localhost:27017')
        db_name = db_name or os.getenv('MONGO_DB_NAME', 'technical_sheet')

        self._client = AsyncIOMotorClient(uri)
        self._db = self._client[db_name]

    async def get_db(self):
        if not self._db:
            await self.connect()
        return self._db

    async def close(self):
        if self._client:
            self._client.close()

mongo_connection = MongoDBConnection()