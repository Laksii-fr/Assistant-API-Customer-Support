import os
import boto3
import requests
from fastapi import UploadFile
from dotenv import load_dotenv
import openai
from openai import OpenAI
import uuid
import tempfile

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

# Initialize Boto3 S3 client
s3_client = boto3.client('s3')
BUCKET_NAME = "sentinal-customer-care"  # Replace with your S3 bucket name
REGION_NAME = "eu-north-1"  # Replace with your S3 bucket region

async def upload_file_to_s3(file: UploadFile) -> str:
    new_filename = uuid.uuid4().hex + "." + file.filename.rsplit('.', 1)[1].lower()
    try:
        s3_client.upload_fileobj(file.file, BUCKET_NAME, new_filename)
        s3_url = f"https://{BUCKET_NAME}.s3.{REGION_NAME}.amazonaws.com/{new_filename}"
        print(f"File uploaded to S3 at {s3_url}")
        return s3_url
    except Exception as e:
        print(f"Error uploading file to S3: {e}")
        return None

async def upload_file_to_openai(s3_url: str) -> str:
    try:
        # Download the file from S3
        response = requests.get(s3_url)
        response.raise_for_status()  # Ensure the request was successful

        # Use a temporary file to store the downloaded content
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(response.content)
            temp_file_path = temp_file.name

        # Upload the file to OpenAI
        with open(temp_file_path, 'rb') as temp_file:
            openai_response = client.files.create(file=temp_file, purpose='fine-tune')
            file_id = openai_response['id']
            print(f"File uploaded to OpenAI with ID {file_id}")

        # Clean up the temporary file
        os.remove(temp_file_path)

        return file_id
    except Exception as e:
        print(f"Error uploading file to OpenAI: {e}")
        return None
