import unicodedata
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from bson.objectid import ObjectId

mongo_uri = 'mongodb://localhost:27017'
mongo_db_name = 'technical_sheet'
mongo_collection = 'vehicle'

client = AsyncIOMotorClient(mongo_uri)
db = client[mongo_db_name]
collection = db[mongo_collection]
logs_collection = db['logs']
vehicle_specs_collection = db['vehicle_specs']

def remove_accents(text):
    return ''.join(
        c for c in unicodedata.normalize('NFKD', text)
        if not unicodedata.combining(c)
    )

async def insert_vehicle(automaker, model, year, version, reference):
    """ Insere um novo documento no MongoDB com referência ao site de origem """
    from logger.logger import get_logger
    logger = get_logger()

    model_clean = remove_accents(model.lower())

    exists = await vehicle_exists(automaker, model, year, version, reference)
    if exists:
        logger.info(f'Veículo já existe no banco: {automaker} {model} {year} ({reference})')
        return None

    document = {
        'timestamp': datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
        'reference': reference,
        'automaker': automaker.lower(),
        'model': model_clean,
        'year': year,
        'version': version,
    }
    await collection.insert_one(document)
    logger.info(f'Documento inserido: {automaker} {model_clean} {year} ({reference})')
    return document

async def vehicle_exists(automaker, model, year, version, reference):
    """ Verifica se já existe um documento igual no MongoDB, incluindo a referência"""
    model_clean = remove_accents(model.lower())

    query = {
        'automaker': automaker.lower(),
        'model': model_clean,
        'year': year,
        'version': version,
        'reference': reference
    }
    document = await collection.find_one(query)
    return document is not None

async def find_vehicle_by_id(doc_id):
    """ Busca um documento pelo seu _id """
    from logger.logger import get_logger
    logger = get_logger()

    try:
        document = await collection.find_one({'_id': ObjectId(doc_id)})
        return document
    except Exception as e:
        logger.error(f'Erro ao buscar documento: {e}')
        return None

async def update_vehicle(doc_id, update_fields):
    from logger.logger import get_logger
    logger = get_logger()

    try:
        result = await collection.update_one(
            {'_id': ObjectId(doc_id)},
            {'$set': update_fields}
        )
        logger.info(f'Documento atualizado, modificados: {result.modified_count}')
        return result.modified_count
    except Exception as e:
        logger.error(f'Erro ao atualizar documento: {e}')
        return 0

async def insert_log(log_entry, reference=None):
    """ Insere um log no MongoDB """
    from logger.logger import get_logger
    logger = get_logger()

    log_entry['timestamp'] = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    log_entry['reference'] = reference
    await logs_collection.insert_one(log_entry)

async def insert_vehicle_specs(technical_data):
    """ Insere um documento completo na collection vehicle_specs """
    from logger.logger import get_logger
    logger = get_logger()

    try:
        await vehicle_specs_collection.insert_one(technical_data)
        logger.info(f'Documento inserido na vehicle_specs')
        return True
    except Exception as e:
        logger.error(f'Erro ao inserir em vehicle_specs: {e}')
        return None

async def get_vehicles_by_reference(reference):
    """ Retorna todos os documentos da collection vehicle com base na referencia """
    from logger.logger import get_logger
    logger = get_logger()

    try:
        cursor = collection.find({'reference': reference})
        documents = await cursor.to_list(length=None)
        logger.info(f'{len(documents)} documentos encontrados com referência: {reference}')
        return documents
    except Exception as e:
        logger.error(f'Erro ao buscar veículos por referência ({reference}): {e}')
        return []