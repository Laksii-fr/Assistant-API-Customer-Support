from fastapi import FastAPI, UploadFile, Form, File, Request, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from openai import OpenAI, AssistantEventHandler
from typing_extensions import override
from helpers import save_file, upload_file_to_openai, create_thread, add_message_to_thread
import markdown2
import re
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")



# print("1 Executed")

# Ensure these lines are commented out or removed if not used
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



# print("2 Executed")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/submit", response_class=RedirectResponse)
async def handle_form(
    request: Request,
    company_name: str = Form(...),
    company_link: str = Form(...),
    file_type: str = Form(...),
    file_input: UploadFile = File(...)
):
    # Save the uploaded file locally
    file_path = await save_file(file_input)
    
    # Upload the file to OpenAI and get the file ID
    file_id = await upload_file_to_openai(file_path)
    
    if not file_id:
        return RedirectResponse(url="/error", status_code=302)
    
    company_info = f"Company Name: {company_name}, Company Link: {company_link}, File Type: {file_type}, File ID: {file_id}"
    
    # Create a new thread
    thread_id = await create_thread(company_info, assistant, file_id)
    
    # Store the thread ID and file ID in the session
    request.session['thread_id'] = thread_id
    request.session['file_id'] = file_id
    
    # Log the uploaded file info
    print(f"Company: {company_name}, Link: {company_link}, File Type: {file_type}, File Name: {file_input.filename}, OpenAI File ID: {file_id} , Thread ID : {thread_id}")
    
    return RedirectResponse(url="/chatbot", status_code=302)

# print("3 Executed")

# Initialize OpenAI client and assistant
client = OpenAI()
assistant = client.beta.assistants.create(
    name="Company Assistant",
    instructions="You are a helpful assistant. You will Answer the user query based on this Company information {company_info}. You should not answer anthing by yourself you must only use the information provided my user",
    tools=[{"type": "file_search"}],  # Use the file_search tool
    model="gpt-4o",
)

@app.get("/chatbot", response_class=HTMLResponse)
async def chatbot_page(request: Request):
    return templates.TemplateResponse("chatbot.html", {"request": request})

# print("4 Executed")

import markdown2

@app.post("/process")
async def process_message(request: Request):
    data = await request.json()
    user_message = data['msg']
    
    # Get the thread ID and file ID from the session
    thread_id = request.session.get('thread_id')
    file_id = request.session.get('file_id')
    
    if not thread_id or not file_id:
        return {"response": "Thread or file not available. Please try again later."}
    
    # Add the user's message to the thread
    await add_message_to_thread(thread_id, user_message, file_id, assistant)
    
    # Stream the response and capture it
    response_text = ""
    event_handler = EventHandler()
    
    class CaptureEventHandler(EventHandler):
        @override
        def on_text_delta(self, delta, snapshot):
            nonlocal response_text
            response_text += delta.value
    
    with client.beta.threads.runs.stream(
        thread_id=thread_id,
        assistant_id=assistant.id,
        instructions="Answer the user's query based the company information {company_info}",
        event_handler=CaptureEventHandler(),
    ) as stream:
        stream.until_done()
    
    # Convert the response to HTML using markdown2
    # print(response_text)
    response_html = markdown2.markdown(response_text)
    
    return {"response": response_html}
