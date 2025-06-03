from pymongo import MongoClient
from datetime import datetime

mongo_uri = 'mongodb://localhost:27017'
mongo_db_name = 'technical_sheet_test'
mongo_collection = 'vehicle'

client = MongoClient(mongo_uri)
db = client[mongo_db_name]
vehicle_collection = db[mongo_collection]
vehicle_specs_collection = db['vehicle_specs']

def vehicle_exists(automaker, model, version, year):
    query = {
        'automaker': automaker,
        'model': model,
        'version': version,
        'year': year
    }
    return vehicle_collection.find_one(query) is not None

def insert_vehicle(automaker, model, version, year, consult_link, reference):
    if vehicle_exists(automaker, model, version, year):
        print(f'Document ja existe: {automaker}, {model}, {version}, {year}')
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
    result = vehicle_collection.insert_one(document)
    return result.inserted_id

def get_vehicles_by_auto_referer(automaker, reference):
    return list(db['vehicle'].find({
        'automaker': automaker,
        'reference': reference
    }))

def insert_technical_sheet(technical_data):
    db['vehicle_specs'].insert_one(technical_data)