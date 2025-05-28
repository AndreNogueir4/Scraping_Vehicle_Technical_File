from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

mongo_uri = 'mongodb://localhost:27017'
mongo_db_name = 'technical_sheet_test'
mongo_collection = 'vehicle'

client = AsyncIOMotorClient(mongo_uri)
db = client[mongo_db_name]
vehicle_collection = db[mongo_collection]
vehicle_specs_collection = db['vehicle_specs']


async def vehicle_exists(automaker, model, version, year):
    query = {
        'automaker': automaker,
        'model': model,
        'version': version,
        'year': year
    }
    document = await vehicle_collection.find_one(query)
    return document is not None

async def insert_vehicle(automaker, model, version, year, consult_link, reference):
    exists = await vehicle_exists(automaker, model, version, year)
    if exists:
        print(f'Documento ja existe: {automaker}, {model}, {version}, {year}')
        return None

    date = datetime.now().strftime('%d-%m-%Y %H:%M:%S')

    document = {
        'automaker': automaker,
        'model': model,
        'version': version,
        'year': year,
        'consult_link': consult_link,
        'reference': reference,
        'date': date
    }
    result = await vehicle_collection.insert_one(document)
    return result.inserted_id