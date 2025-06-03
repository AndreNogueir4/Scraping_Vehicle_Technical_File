from bson.objectid import ObjectId
import unicodedata
from datetime import datetime

class BaseRepository:
    def __init__(self, collection_name):
        self.collection_name = collection_name
        self._collection = None

    async def get_collection(self):
        if not self._collection:
            db = await mongo_connection.get_db()
            self._collection = db[self.collection_name]
        return self._collection

    @staticmethod
    def remove_accents(text):
        return ''.join(
            c for c in unicodedata.normalize('NFKD', text)
            if not unicodedata.combining(c)
        )

    async def find_by_id(self, doc_id):
        try:
            collection = await self.get_collection()
            return await collection.find_one({'_id': ObjectId(doc_id)})
        except Exception:
            return None

    async def update(self, doc_id, update_fields):
        try:
            collection = await self.get_collection()
            result = await collection.update_one(
                {'_id': ObjectId(doc_id)},
                {'$set': update_fields}
            )
            return result.modified_count
        except Exception:
            return 0