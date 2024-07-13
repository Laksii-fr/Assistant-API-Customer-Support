from openai import OpenAI
from app.event_handler import EventHandler
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

async def create_thread(company_info: str, assistant_id: str, file_id: str = None) -> str:
    """Create a new thread and add the initial message."""
    try:
        thread = client.beta.threads.create()
        thread_id = thread.id
        
        # Add initial message to the thread
        await add_message_to_thread(thread_id, company_info, assistant_id, file_id, role="assistant")
        
        return thread_id
    except Exception as e:
        print(f"Error creating thread: {e}")
        return None
    
async def add_message_to_thread(thread_id: str, content: str, assistant_id: str, file_id: str = None, role: str = "user") -> str:
    """Add a message to the thread and handle responses."""
    try:
        # Define attachments only if file_id is provided
        attachments = [{"file_id": file_id, "tools": [{"type": "file_search"}]}] if file_id else None
        response = client.beta.threads.messages.create(
            thread_id=thread_id,
            role=role,
            content=content,
            attachments=attachments
        )

        response_text = ""
        event_handler = EventHandler()

        class CaptureEventHandler(EventHandler):
            def on_text_delta(self, delta, snapshot):
                nonlocal response_text
                response_text += delta.value

        with client.beta.threads.runs.stream(
            thread_id=thread_id,
            assistant_id=assistant_id,  # Correctly use the assistant ID
            instructions=f"Answer the user's query based on the company information {content}",
            event_handler=CaptureEventHandler(),
        ) as stream:
            stream.until_done()

        return response_text
    except Exception as e:
        print(f"Error adding message to thread: {e}")
        return None
