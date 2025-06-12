from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from api.routes.vehicles import router as vehicle_router
from api.routes.users import router as users_router
from api.middleware.auth import get_current_user
from api.schemas.users import UserInDB
from api.limiter import limiter
from api.exceptions import rate_limit_exception_handler

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exception_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.get('/verify-api-key/', response_model=UserInDB)
@limiter.limit('10/minute')
async def verify_api_key(request: Request, current_user: UserInDB = Depends(get_current_user)):
    return current_user


app.include_router(vehicle_router, prefix='/vehicles', tags=['vehicles'])
app.include_router(users_router, prefix='/users', tags=['users'])

@app.get('/')
async def root():
    return {'message': 'Vehicle API is running'}