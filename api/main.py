from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from api.routes.vehicles import router as vehicle_router
from api.routes.users import router as users_router
from api.middleware.auth import get_current_user
from api.schemas.users import UserInDB

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.get('/verify-api-key/', response_model=UserInDB)
async def verify_api_key(current_user: UserInDB = Depends(get_current_user)):
    return current_user

app.include_router(vehicle_router, prefix='/vehicles', tags=['vehicles'])
app.include_router(users_router, prefix='/users', tags=['users'])

@app.get('/')
async def root():
    return {'message': 'Vehicle API is running'}