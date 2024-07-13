from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = "assistant_db"
COLLECTION_NAME = "assistant_data"
TCOLLECTION_NAME = "assistant_threads"



client = AsyncIOMotorClient(MONGODB_URI)
db = client[DATABASE_NAME]
assistant_collection = db[COLLECTION_NAME]
thread_collection = db[TCOLLECTION_NAME]

async def insert_assistant_data(assistant_name: str, assistant_instructions: str,assistant_link: str, assistant_id: str,Model_type: str, tool_type: str, thread_id: str,file_id: Optional[str] = None):
    """Insert assistant, thread, and optional file ID into MongoDB."""
    document = {
        "assistant_name": assistant_name,
        "assistant_instructions" : assistant_instructions,
        "link": assistant_link,
        "assistant_id": assistant_id,
        "Model_type" : Model_type,
        "assistant_tool" : tool_type,
        "thread_id": thread_id,
        "file_id": file_id
    }
    result = await assistant_collection.insert_one(document)
    return result.inserted_id

async def insert_assistant_threads(assistant_id: str, thread_id: str,file_id: Optional[str] = None):
    """Insert assistant, thread, and optional file ID into MongoDB."""
    document = {
        "assistant_id": assistant_id,
        "thread_id": thread_id,
        "file_id": file_id
    }
    print(document)
    result = await thread_collection.insert_one(document)
    return result.inserted_id

# async def update_assistant_data(assistant_id: str, thread_id: Optional[str] = None, file_id: Optional[str] = None):
#     """Update an existing assistant document with new thread or file ID."""
#     filter_query = {"assistant_id": assistant_id}
#     update_fields = {}
#     if thread_id:
#         update_fields["thread_id"] = thread_id
#     if file_id:
#         update_fields["file_id"] = file_id
#     update_query = {"$set": update_fields}

#     result = await assistant_collection.find_one_and_update(
#         filter_query,
#         update_query,
#         return_document=ReturnDocument.AFTER
#     )
#     return result

async def get_assistant_data(assistant_id: str):
    """Retrieve assistant data by assistant_id."""
    return await assistant_collection.find_one({"assistant_id": assistant_id})

async def delete_assistant_data(assistant_id: str):
    """Delete assistant data by assistant_id."""
    result = await thread_collection.delete_one({"assistant_id": assistant_id})
    return result.deleted_count

async def get_threads_for_assistant(assistant_id):
    cursor = db.assistant_threads.find({"assistant_id": assistant_id})
    threads = await cursor.to_list(length=100)
    return [{"thread_id": thread["thread_id"]} for thread in threads]

async def get_messages_for_thread(thread_id):
    cursor = db.messages.find({"thread_id": thread_id})
    messages = await cursor.to_list(length=100)
    return [{"content": msg["content"], "role": msg["role"], "time": msg["time"]} for msg in messages]

async def update_assistant_data(assistant_id, assistant_name=None, assistant_instructions=None, tool_type=None, model_type=None):
    update_fields = {}
    if assistant_name:
        update_fields["assistant_name"] = assistant_name
    if assistant_instructions:
        update_fields["assistant_instructions"] = assistant_instructions
    if tool_type:
        update_fields["assistant_tool"] = tool_type
    if model_type:
        update_fields["model_type"] = model_type

    if not update_fields:
        return None  # No updates to be made

    result = await assistant_collection.update_one(
        {"assistant_id": assistant_id},
        {"$set": update_fields}
    )
    return result.modified_count
