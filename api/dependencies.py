from fastapi import Header, HTTPException
from src.db.mongo import users_collection

async def get_admin_user(x_api_key: str = Header(...)):
    key_doc = users_collection.find_one({'api_key': x_api_key})
    if not key_doc or not key_doc.get('is_admin', False):
        raise HTTPException(status_code=403, detail='Access Denied: Invalid API Key or No Permission')
    return key_doc