import os
from fastapi import UploadFile
from dotenv import load_dotenv
import openai
from openai import OpenAI
import io

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

async def upload_file_to_openai(file: UploadFile, vector_store_id: str) -> str:
    try:
        # Read the file content in binary mode
        content = await file.read()

        # Create the file in OpenAI
        _file_ = client.files.create(file=content, purpose='assistants')

        # Prepare the file as an in-memory file-like object
        file_like = io.BytesIO(content)
        file_like.name = file.filename  # Give the file-like object a name attribute

        # Create an iterable of file-like objects
        files = [file_like]

        file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store_id, files=files
        )

        # Retrieve the file ID
        file_id = _file_.id  # Use attribute access instead of indexing
        print(f"File uploaded to OpenAI with ID {file_id}")

        return file_id

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    

async def create_vector_store(config):
    assistant_name = config['company_name']
    vector_store = client.beta.vector_stores.create(
        name=assistant_name
    )
    vector_store_ids = vector_store.id

    return vector_store_ids

