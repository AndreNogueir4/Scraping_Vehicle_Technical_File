from typing import Dict, Optional
from bson.objectid import ObjectId
from logger import get_logger
from src.db.connection import MongoDBConnection

logger = get_logger('technical_specs_repo')

class TechnicalSpecsRepository:
    def __init__(self):
        self.collection_name = 'technical_specs'
        self._collection = None

    async def _get_collection(self):
        if not self._collection:
            db = await MongoDBConnection.get_db()
            self._collection = db[self.collection_name]
        return self._collection

    async def find_by_vehicle_id(self, vehicle_id: str) -> Optional[Dict]:
        try:
            collection = await self._get_collection()

            if isinstance(vehicle_id, str):
                vehicle_id = ObjectId(vehicle_id)

            return await collection.find_one({'vehicle_id': vehicle_id})
        except Exception as e:
            logger.error(f'Erro ao buscar ficha técnica: {str(e)}', exc_info=True)
            return None

    async def upsert(self, query: Dict, data: Dict) -> bool:
        try:
            collection = await self._get_collection()

            if 'vehicle_id' in query and isinstance(query['vehicle_id'], str):
                query['vehicle_id'] = ObjectId(query['vehicle_id'])

            result = await collection.update_one(
                query,
                {'$set': data},
                upsert=True
            )

            if result.upserted_id or result.modified_count > 0:
                logger.debug(f'Ficha técnica {"inserida" if result.upserted_id else "atualizada"}')
                return True
            return False

        except Exception as e:
            logger.error(f'Erro ao upsert ficha técnica: {str(e)}', exc_info=True)
            return False

    async def get_specifications(self, vehicle_id: str) -> Optional[Dict]:
        try:
            collection = await self._get_collection()

            if isinstance(vehicle_id, str):
                vehicle_id = ObjectId(vehicle_id)

            doc = await collection.find_one(
                {'vehicle_id': vehicle_id},
                {'specifications': 1, '_id': 0}
            )
            return doc.get('specifications') if doc else None

        except Exception as e:
            logger.error(f'Erro ao buscar especificações: {str(e)}', exc_info=True)
            return None

    async def get_equipment(self, vehicle_id: str) -> Optional[list]:
        try:
            collection = await self._get_collection()

            if isinstance(vehicle_id, str):
                vehicle_id = ObjectId(vehicle_id)

            doc = await collection.find_one(
                {'vehicle_id': vehicle_id},
                {'equipment': 1, '_id': 0}
            )
            return doc.get('equipment') if doc else None
        except Exception as e:
            logger.error(f'Erro ao buscar equipamentos: {str(e)}', exc_info=True)
            return None

    async def delete_by_vehicle_id(self, vehicle_id: str) -> bool:
        try:
            collection = await self._get_collection()

            if isinstance(vehicle_id, str):
                vehicle_id = ObjectId(vehicle_id)

            result = await collection.delete_one({'vehicle_id': vehicle_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f'Erro ao remover ficha técnica: {str(e)}', exc_info=True)
            return False

    async def create_indexes(self):
        try:
            collection = await self._get_collection()
            await collection.create_index('vehicle_id', unique=True)
            logger.info('Índices criados para technical_specs')
        except Exception as e:
            logger.error(f'Erro ao criar índices: {str(e)}', exc_info=True)