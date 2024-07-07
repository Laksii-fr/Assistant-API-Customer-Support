from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = "assistant_db"
COLLECTION_NAME = "assistant_data"

async def create_database_and_collection():
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DATABASE_NAME]

    # Check if the collection exists
    collection_names = await db.list_collection_names()
    if COLLECTION_NAME not in collection_names:
        print(f"Creating collection: {COLLECTION_NAME}")
        await db.create_collection(COLLECTION_NAME)
    else:
        print(f"Collection {COLLECTION_NAME} already exists")

# Example function to run this script
if __name__ == "__main__":
    import asyncio
    asyncio.run(create_database_and_collection())
