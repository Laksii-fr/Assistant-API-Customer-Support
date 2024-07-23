from openai import OpenAI
import os
import openai
from app.helpers.openai_helpers import create_files
from fastapi import UploadFile

openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

def create_assistant(config):
    if 'tool_sel' not in config or 'assistant_instructions' not in config:
        raise ValueError("Assistant configuration is not set properly")
    
    tool_sel = config['tool_sel']
    Model_sel = config['Model_sel']
    assistant_instructions = config['assistant_instructions']
    company_name = config['company_name'] 

    try:
        assistant = client.beta.assistants.create(
            name=company_name,
            instructions=assistant_instructions,
            tools=[{"type": tool_sel}],  # Use the selected tool type
            model=Model_sel,
        )
        return assistant
    except Exception as e:
        print(f"Error creating assistant: {e}")
        return None

async def create_assistant_with_file(files: list[UploadFile], config):
    company_name = config['company_name']
    tool_sel = config['tool_sel']
    model_sel = config['Model_sel']
    assistant_instructions = config['assistant_instructions']
    
    print("Starting the process of creating an assistant with files")
    try:
        print("Uploading files")
        files_list = await create_files(files)
        print(f"Files uploaded successfully: {files_list}")
    except ValueError as e:
        print(f"File upload error: {e}")
        return None
    file_ids = [element["fileId"] for element in files_list]
    print(f"File IDs extracted: {file_ids}")
    try:
        print("Creating assistant with OpenAI API")
        client = OpenAI()
        assistant = client.beta.assistants.create(
            name=company_name,
            instructions=assistant_instructions,
            tools=[{"type": tool_sel}],
            model=model_sel,
            file_ids=file_ids,
        )
        print(f"Assistant created successfully: {assistant}")
        return assistant
    except Exception as e:
        print(f"Error creating assistant with files: {e}")
        return None

async def update_assistant_details(assistant_id, name=None, instructions=None, tool_type=None, model_type=None):
    update_data = {}
    if name:
        update_data["name"] = name
    if instructions:
        update_data["instructions"] = instructions
    if tool_type:
        update_data["tools"] = [{"type": tool_type}]
    if model_type:
        update_data["model"] = model_type

    if not update_data:
        return None  # No updates to be made

    try:
        updated_assistant = client.beta.assistants.update(
            assistant_id,
            **update_data
        )
        return updated_assistant
    except Exception as e:
        print(f"Error updating assistant: {e}")
        return None
