import secrets
from fastapi import APIRouter, HTTPException, Request, status
from api.schemas.users import UserCreate, UserResponse
from src.db.mongo import users_collection, user_helper
from ..limiter import limiter
from datetime import datetime

router = APIRouter()

async def generate_api_key():
    return secrets.token_urlsafe(32)

@router.post('/', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit('5/minute')
async def create_user(request: Request, user_data: UserCreate):
    print('Chegou no endpoint')
    existing_user = await users_collection.find_one({
        '$or': [
            {'username': user_data.username},
            {'email': user_data.email}
        ]
    })
    print('Verificado se o usuario existe')
    if existing_user:
        print('Usuario ja existe')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Username or email already registered'
        )

    api_key = await generate_api_key()

    user_doc = {
        'username': user_data.username.lower(),
        'email': user_data.email.lower(),
        'api_key': api_key,
        'is_active': True,
        'is_admin': user_data.is_admin,
        'created_at': datetime.now(),
        'last_used': None
    }

    print('Tentando inserir')
    result = await users_collection.insert_one(user_doc)
    print('Inserido:', result.inserted_id)
    new_user = await users_collection.find_one({'_id': result.inserted_id})
    print('Usuario buscado', new_user)
    user_response = user_helper(new_user)
    print('Resposta montada', user_response)
    return user_response