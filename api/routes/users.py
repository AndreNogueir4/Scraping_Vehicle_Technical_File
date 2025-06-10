import secrets
from fastapi import APIRouter, HTTPException, status
from api.schemas.users import UserCreate, UserResponse
from db.mongo import users_collection, user_helper
from datetime import datetime

router = APIRouter()

async def generate_api_key():
    return secrets.token_urlsafe(32)

@router.post('/', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate):
    existing_user = await users_collection.find_one({'$or': [{'username': user_data.username},
                                                             {'email': user_data.email}]})
    if existing_user:
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
        'created_at': datetime.now(),
        'last_used': None
    }

    result = await users_collection.insert_one(user_doc)
    new_user = await users_collection.find_one({'_id': result.inserted_id})
    return user_helper(new_user)