from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = "assistant_db"
COLLECTION_NAME = "assistant_data"

client = AsyncIOMotorClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

async def insert_assistant_data(assistant_id: str, thread_id: str, file_id: Optional[str] = None):
    """Insert assistant, thread, and optional file ID into MongoDB."""
    document = {
        "assistant_id": assistant_id,
        "thread_id": thread_id,
        "file_id": file_id
    }
    result = await collection.insert_one(document)
    return result.inserted_id

async def update_assistant_data(assistant_id: str, thread_id: Optional[str] = None, file_id: Optional[str] = None):
    """Update an existing assistant document with new thread or file ID."""
    filter_query = {"assistant_id": assistant_id}
    update_fields = {}
    if thread_id:
        update_fields["thread_id"] = thread_id
    if file_id:
        update_fields["file_id"] = file_id
    update_query = {"$set": update_fields}

    result = await collection.find_one_and_update(
        filter_query,
        update_query,
        return_document=ReturnDocument.AFTER
    )
    return result

async def get_assistant_data(assistant_id: str):
    """Retrieve assistant data by assistant_id."""
    return await collection.find_one({"assistant_id": assistant_id})

async def delete_assistant_data(assistant_id: str):
    """Delete assistant data by assistant_id."""
    result = await collection.delete_one({"assistant_id": assistant_id})
    return result.deleted_count
