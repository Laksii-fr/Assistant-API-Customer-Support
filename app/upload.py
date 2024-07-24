import os
from fastapi import UploadFile
from dotenv import load_dotenv
import openai
from openai import OpenAI

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

async def upload_file_to_openai(file) -> str:

    try:
        content = await file.read()

        response = client.files.create(file=content, purpose='assistants')

        file_id = response.id  # Use attribute access instead of indexing
        print(f"File uploaded to OpenAI with ID {file_id}")
        return file_id
    except Exception as e:
        print(f"Error uploading file to OpenAI: {e}")
        return None  # Ensure you handle this case in your calling code
    

async def create_vector_store_with_file(file_ids: list, config):
    assistant_name = config['company_name']
    try:
        vector_store = client.beta.vector_stores.create(
            name=assistant_name
        )
        vector_id = vector_store.id  # Use indexing to access the vector ID
        print(f"Vector ID : {vector_id}")
        for file_id in file_ids:
            file = client.beta.vector_stores.files.create_and_poll(
                vector_store_id=vector_id,
                file_id=file_id
                )
        print(f"Vector store created with ID {vector_id}")
        return vector_id
    except Exception as e:
        print(f"Error creating vector store: {e}")
        return None  # Ensure you handle this case in your calling code
