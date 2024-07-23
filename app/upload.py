import os
from fastapi import UploadFile
from dotenv import load_dotenv
import openai
from openai import OpenAI

openai.api_key = os.getenv("OPENAI_API_KEY")
load_dotenv()
client = OpenAI()


async def upload_file_to_openai(file: UploadFile) -> str:
    print("Executed 1.2.1")
    try:
        content = await file.read()
        print("Executed 1.2.2")
        response = client.files.create(file=content, purpose='assistants')
        print("Executed 1.2.3")
        file_id = response.id  # Use attribute access instead of indexing
        print(f"File uploaded to OpenAI with ID {file_id}")
        return file_id
    except Exception as e:
        print(f"Error uploading file to OpenAI: {e}")
        return None  # Ensure you handle this case in your calling code
    