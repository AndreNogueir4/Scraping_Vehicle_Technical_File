from fastapi import HTTPException, Request, Depends, status
from fastapi.security import APIKeyHeader
from datetime import datetime
from db.mongo import users_collection, request_logs_collection

api_key_header = APIKeyHeader(name="X-API-Key")

async def get_current_user(api_key: str = Depends(api_key_header)):
    user = await users_collection.find_one({"api_key": api_key, "is_active": True})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API Key",
        )
    return user

async def log_request(request: Request, user_id: str, params: dict):
    log_data = {
        "endpoint": request.url.path,
        "params": params,
        "timestamp": datetime.now(),
        "user_id": user_id
    }
    await request_logs_collection.insert_one(log_data)
    await users_collection.update_one(
        {"_id": user_id},
        {"$set": {"last_used": datetime.now()}}
    )