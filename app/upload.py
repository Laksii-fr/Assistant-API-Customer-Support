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
    print("Executed 1.2.1")
    file_path = f"uploads/{file.filename}"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    print("Executed 1.2.2")
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    print(f"File saved at {file_path}")
    return file_path

async def upload_file_to_openai(file_path: str) -> str:
    print("Executed 1.2.3")
    try:
        with open(file_path, 'rb') as f:
            print("Executed 1.2.4")
            response = client.files.create(file=f, purpose='fine-tune')
            file_id = response.id  # Use attribute access instead of indexing
        print(f"File uploaded to OpenAI with ID {file_id}")
        return file_id
    except Exception as e:
        print(f"Error uploading file to OpenAI: {e}")
        return None  # Ensure you handle this case in your calling code