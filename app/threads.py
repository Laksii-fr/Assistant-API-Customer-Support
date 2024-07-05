from openai import OpenAI

from app.event_handler import EventHandler
import os
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI()

async def create_thread(company_info: str, assistant, file_id: str) -> str:
    try:
        if not assistant:
            raise ValueError("Invalid assistant configuration")
        
        thread = client.beta.threads.create()
        thread_id = thread.id
        
        # Add initial message to the thread
        await add_message_to_thread(thread_id, company_info, file_id, assistant, role="assistant")
        
        return thread_id
    except Exception as e:
        print(f"Error creating thread: {e}")
        return None

async def add_message_to_thread(thread_id: str, content: str, file_id: str, assistant, role: str = "user") -> str:
    try:
        attachments = [{"file_id": file_id, "tools": [{"type": "file_search"}]}] if file_id else None
        if not assistant:
            raise ValueError("Invalid assistant configuration")

        message = client.beta.threads.messages.create(
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
            assistant_id=assistant.id,
            instructions="Answer the user's query based on the company information {company_info}",
            event_handler=CaptureEventHandler(),
        ) as stream:
            stream.until_done()

        return response_text
    except Exception as e:
        print(f"Error adding message to thread: {e}")
        return None
