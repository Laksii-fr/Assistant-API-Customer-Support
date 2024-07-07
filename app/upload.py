import aiofiles
import os
from fastapi import UploadFile
from openai import OpenAI
from dotenv import load_dotenv
import openai


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
            response = client.files.create(file=f, purpose='fine-tune')
            file_id = response.id  # Use attribute access instead of indexing
        return file_id
    except Exception as e:
        print(f"Error uploading file to OpenAI: {e}")
        return None # type: ignore
