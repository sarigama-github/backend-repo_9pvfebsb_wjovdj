import os
from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "appdb")

_client = AsyncIOMotorClient(DATABASE_URL)
db: AsyncIOMotorDatabase = _client[DATABASE_NAME]


def _with_timestamps(data: Dict[str, Any]) -> Dict[str, Any]:
    now = datetime.utcnow()
    return {**data, "created_at": now, "updated_at": now}


async def create_document(collection_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
    payload = _with_timestamps(data)
    result = await db[collection_name].insert_one(payload)
    payload["_id"] = result.inserted_id
    return payload


async def get_documents(
    collection_name: str,
    filter_dict: Optional[Dict[str, Any]] = None,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    filter_dict = filter_dict or {}
    cursor = db[collection_name].find(filter_dict).limit(limit)
    docs: List[Dict[str, Any]] = []
    async for doc in cursor:
        docs.append(doc)
    return docs
