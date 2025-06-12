from fastapi import APIRouter, Depends, Request, HTTPException
from typing import List
from api.schemas.vehicles import Vehicle, VehicleList
from api.schemas.users import UserInDB
from src.db.mongo import vehicle_specs_collection, vehicle_helper
from api.middleware.auth import get_current_user, log_request
from ..limiter import limiter

router = APIRouter()

@router.get('/{sheet_code}', response_model=Vehicle)
@limiter.limit('10/minute')
async def get_vehicle_by_sheet_code(sheet_code: str, request: Request,
                                    current_user: UserInDB = Depends(get_current_user)):
    await log_request(request, current_user['_id'], {'sheet_code': sheet_code})
    vehicle = await vehicle_specs_collection.find_one({'sheet_code': sheet_code})
    if vehicle:
        return vehicle_helper(vehicle)
    raise HTTPException(status_code=404, detail=f'Vehicle with sheet_code {sheet_code} not found')

@router.get('/automaker/{automaker}', response_model=List[VehicleList])
@limiter.limit('10/minute')
async def get_vehicles_by_automaker(automaker: str, request: Request,
                                    current_user: UserInDB = Depends(get_current_user)):
    await log_request(request, current_user['_id'], {'automaker': automaker})
    vehicles = []
    async for vehicle in vehicle_specs_collection.find({'automaker': automaker}):
        vehicles.append({
            'sheet_code': vehicle['sheet_code'],
            'automaker': vehicle['automaker'],
            'model': vehicle['model'],
            'version': vehicle['version'],
            'year': vehicle['year']
        })
    if vehicles:
        return vehicles
    raise HTTPException(status_code=404, detail=f'No vehicles found for automaker {automaker}')