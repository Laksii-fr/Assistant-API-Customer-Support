from fastapi import FastAPI, UploadFile, Form, File, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse
from openai import OpenAI, AssistantEventHandler
from typing_extensions import override
from app.helpers.helpers import save_file, upload_file_to_openai, create_thread, add_message_to_thread
import markdown2
import re

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Global dictionary to store assistant configurations
assistant_config = {}

class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text) -> None:
        print(f"\nassistant > ", end="", flush=True)
      
    @override
    def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)
      
    def on_tool_call_created(self, tool_call):
        print(f"\nassistant > {tool_call.type}\n", flush=True)
  
    def on_tool_call_delta(self, delta, snapshot):
        if delta.type == 'file_search':
            print(f"\n{delta.file_search.input}\n", flush=True)
            if delta.file_search.outputs:
                print(f"\n\noutput >", flush=True)
                for output in delta.file_search.outputs:
                    if output.type == "text":
                        print(f"\n{output.text}", flush=True)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})

@app.post("/submit", response_class=RedirectResponse)
async def handle_form(
    request: Request,
    company_name: str = Form(...),
    company_link: str = Form(...),
    assistant_instructions: str = Form(...),
    tool_type: str = Form(...),
    file_type: str = Form(...),
    file_input: UploadFile = File(...)
):
    # Save the uploaded file locally
    file_path = await save_file(file_input)

    # Upload the file to OpenAI and get the file ID
    file_id = await upload_file_to_openai(file_path)
    
    if not file_id:
        return RedirectResponse(url="/error", status_code=302)
    
    global company_info

    company_info = f"Company Name: {company_name}, Company Link: {company_link}, File Type: {file_type}, File ID: {file_id}"

    # Update the global assistant configuration
    assistant_config['tool_sel'] = tool_type
    assistant_config['assistant_instructions'] = assistant_instructions
    assistant_config['company_info'] = company_info

    # Create the assistant
    assistant = create_assistant()

    # Create a new thread
    thread_id = await create_thread(company_info, assistant, file_id)

    # Store the thread ID and file ID in the session
    request.session['thread_id'] = thread_id
    request.session['file_id'] = file_id

    print(f"Company: {company_name}, Link: {company_link}, File Type: {file_type}, File Name: {file_input.filename}, OpenAI File ID: {file_id}, Thread ID: {thread_id}")

    return RedirectResponse(url="/chatbot", status_code=302)


def create_assistant():
    """Factory function to create an assistant based on the current configuration."""
    if 'tool_sel' not in assistant_config or 'assistant_instructions' not in assistant_config:
        raise ValueError("Assistant configuration is not set properly")

    tool_sel = assistant_config['tool_sel']
    assistant_instructions = assistant_config['assistant_instructions']
    company_info = assistant_config.get('company_info', '')

    client = OpenAI()
    assistant = client.beta.assistants.create(
        name="Company Assistant",
        instructions=assistant_instructions + f", Company Information: {company_info}",
        tools=[{"type": tool_sel}],  # Use the selected tool type
        model="gpt-3.5-turbo",
    )
    return assistant


@app.get("/chatbot", response_class=HTMLResponse)
async def chatbot_page(request: Request):
    return templates.TemplateResponse("chatbot.html", {"request": request})

@app.post("/process")
async def process_message(request: Request):
    data = await request.json()
    user_message = data['msg']

    thread_id = request.session.get('thread_id')
    file_id = request.session.get('file_id')

    if not thread_id or not file_id:
        return {"response": "Thread or file not available. Please try again later."}

    # Create the assistant using the factory function
    assistant = create_assistant()

    # Add the user's message to the thread
    await add_message_to_thread(thread_id, user_message, file_id, assistant)

    response_text = ""
    event_handler = EventHandler()

    class CaptureEventHandler(EventHandler):
        @override
        def on_text_delta(self, delta, snapshot):
            nonlocal response_text
            response_text += delta.value

    client = OpenAI()
    with client.beta.threads.runs.stream(
        thread_id=thread_id,
        assistant_id=assistant.id,
        instructions="Answer the user's query based on the company information {company_info}",
        event_handler=CaptureEventHandler(),
    ) as stream:
        stream.until_done()

    response_html = markdown2.markdown(response_text)
    return {"response": response_html}
