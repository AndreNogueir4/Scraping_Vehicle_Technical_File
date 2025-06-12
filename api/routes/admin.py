from fastapi import APIRouter, Depends, HTTPException, Path, Query
from bson import ObjectId
from datetime import datetime, timedelta
from api.schemas.users import UserResponse, RequestLog
from api.dependencies import get_admin_user
from src.db.mongo import users_collection, request_logs_collection

router = APIRouter()

@router.get('/users', response_model=list[UserResponse])
async def list_users(admin_user: dict = Depends(get_admin_user)):
    users = users_collection.find()
    return [
        UserResponse(
            id=str(user['_id']),
            username=user['username'],
            email=user['email'],
            api_key=user['api_key'],
            is_active=user.get('is_active', True),
            is_admin=user.get('is_admin', False),
            created_at=user['created_at'],
            last_used=user.get('last_used'),
        )
        for user in users
    ]

@router.patch('/users/{user_id}/deactivate', response_model=UserResponse)
async def deactivate_user(user_id: str = Path(..., title='ID do usuário'),
                          admin_user: dict = Depends(get_admin_user)):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail='ID de usuário inválido')

    user = users_collection.find_one({'_id': ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail='Usuário não encontrado')

    users_collection.update_one({'_id': ObjectId(user_id)}, {'$set': {'is_active': False}})
    user = users_collection.find_one({'_id': ObjectId(user_id)})

    return UserResponse(
        id=str(user['_id']),
        username=user['username'],
        email=user['email'],
        api_key=user['api_key'],
        is_active=user.get('is_active', True),
        is_admin=user.get('is_admin', False),
        created_at=user['created_at'],
        last_used=user.get('last_used'),
    )

@router.patch('/users/{user_id}/activate', response_model=UserResponse)
async def activate_user(user_id: str = Path(..., title='ID do usuário'),
                          admin_user: dict = Depends(get_admin_user)):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail='ID de usuário inválido')

    user = users_collection.find_one({'_id': ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail='Usuário não encontrado')

    users_collection.update_one({'_id': ObjectId(user_id)}, {'$set': {'is_active': True}})
    user = users_collection.find_one({'_id': ObjectId(user_id)})

    return UserResponse(
        id=str(user['_id']),
        username=user['username'],
        email=user['email'],
        api_key=user['api_key'],
        is_active=user.get('is_active', True),
        is_admin=user.get('is_admin', False),
        created_at=user['created_at'],
        last_used=user.get('last_used'),
    )

@router.get('/logs', response_model=list[RequestLog])
async def get_request_logs(date: str | None = Query(None, description='Data no formato YYYY-MM-DD'),
                           admin_user: dict = Depends(get_admin_user)):
    query = {}

    if date:
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=400, detail='Data inválida. Use o formato YYYY-MM-DD')

        start = datetime(date_obj.year, date_obj.month, date_obj.day)
        end = start + timedelta(days=1)

        query['timestamp'] = {'$gte': start, '$lt': end}

    logs = request_logs_collection.find(query).sort('timestamp', -1)

    return [
        RequestLog(
            endpoint=log['endpoint'],
            params=log.get('params', {}),
            timestamp=log['timestamp'],
            user_id=str(log['user_id']),
        )
        for log in logs
    ]