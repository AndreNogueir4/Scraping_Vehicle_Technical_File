from .base import BaseRepository
from datetime import datetime


class VehicleRepository(BaseRepository):
    def __init__(self):
        super().__init__('vehicle')

    async def insert_vehicle(self, automaker, model, year, version, reference):
        model_clean = self.remove_accents(model.lower())

        if await self.vehicle_exists(automaker, model, year, version, reference):
            return None

        document = {
            'timestamp': datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
            'reference': reference,
            'automaker': automaker.lower(),
            'model': model_clean,
            'year': year,
            'version': version,
        }

        collection = await self.get_collection()
        await collection.insert_one(document)
        return document

    async def vehicle_exists(self, automaker, model, year, version, reference):
        model_clean = self.remove_accents(model.lower())

        query = {
            'automaker': automaker.lower(),
            'model': model_clean,
            'year': year,
            'version': version,
            'reference': reference
        }

        collection = await self.get_collection()
        document = await collection.find_one(query)
        return document is not None

    async def get_by_reference(self, reference):
        collection = await self.get_collection()
        cursor = collection.find({'reference': reference})
        return await cursor.to_list(length=None)