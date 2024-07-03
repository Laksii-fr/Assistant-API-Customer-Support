import openai
from fastapi import UploadFile
import aiofiles
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

openai.api_key = os.getenv("OPENAI_API_KEY")
# print("1.1 Executed")
async def save_file(file: UploadFile) -> str:
    file_path = f"uploads/{file.filename}"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    return file_path
# print("1.2 Executed")
async def upload_file_to_openai(file_path: str) -> str:
    try:
        with open(file_path, 'rb') as f:
            response = client.files.create(file=f, purpose='fine-tune')
            file_id = response.id  # Use attribute access instead of indexing
        return file_id
    except Exception as e:
        print(f"Error uploading file to OpenAI: {e}")
        return None
# print("1.3 Executed")

async def create_thread(company_info: str, assistant, file_id: str) -> str:
    try:
        client = OpenAI()
        thread = client.beta.threads.create()
        thread_id = thread.id
        
        # Add initial message to the thread
        await add_message_to_thread(thread_id, company_info, file_id, assistant, role="assistant")
        
        return thread_id
    except Exception as e:
        print(f"Error creating thread: {e}")
        return None
# print("1.4 Executed")
async def add_message_to_thread(thread_id: str, content: str, file_id: str, assistant, role: str = "user") -> None:
    try:
        attachments = [{"file_id": file_id, "tools": [{"type": "file_search"}]}] if file_id else None
        client = OpenAI()
        assistant = client.beta.threads.messages.create(
            thread_id=thread_id,
            role=role,
            content=content,
            attachments=attachments
        )
    except Exception as e:
        print(f"Error adding message to thread: {e}")
#What code does phoenix have to enter to difuse the spike