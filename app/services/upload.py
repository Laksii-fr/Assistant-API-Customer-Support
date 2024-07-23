import aiofiles
import os
import asyncio


from fastapi import UploadFile
from dotenv import load_dotenv
import openai
from openai import OpenAI


openai.api_key = os.getenv("OPENAI_API_KEY")

load_dotenv()
client = OpenAI()

async def save_file(file: UploadFile) -> str:
    file_path = f"uploads/{file.filename}"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    return file_path

async def upload_file_to_openai(file_path: str) -> str:
    try:
        with open(file_path, 'rb') as f:
            response = client.files.create(file=f, purpose='assistants')
            file_id = response.id  # Use attribute access instead of indexing
        return file_id
    except Exception as e:
        return None  # Ensure you handle this case in your calling code

async def create_file(file: UploadFile):

        client = OpenAI()
        contents = await file.read()
        created_file = client.files.create(file=contents, purpose="assistants")

        file_object = {
                "fileId": created_file.id,
                "fileName": file.filename,
                "fileSize": file.size,
                "fileType": file.content_type,
        }
        return file_object