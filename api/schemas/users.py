from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    api_key: str
    is_active: bool
    created_at: datetime
    last_used: datetime | None = None

class UserCreate(UserBase):
    username: str
    email: str

class UserInDB(UserBase):
    id: str
    api_key: str
    created_at: datetime
    last_used: Optional[datetime] = None

class RequestLog(BaseModel):
    endpoint: str
    params: dict
    timestamp: datetime
    user_id: str