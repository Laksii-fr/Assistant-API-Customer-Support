from fastapi import FastAPI, UploadFile, Form, File, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse
from app.database import insert_assistant_data
from app.assistant import create_assistant
from app.upload import save_file, upload_file_to_openai
from app.threads import create_thread , add_message_to_thread

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Global dictionary to store assistant configurations
assistant_config = {}

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
    Model_type : str = Form(...),
    file_input: UploadFile = File(...)
):
    global company_info
    file_id = None

    if tool_type != "code_interpreter":
        # Save the uploaded file locally
        if file_input:
            file_path = await save_file(file_input)
            # Upload the file to OpenAI and get the file ID
            file_id = await upload_file_to_openai(file_path)

        if not file_id:
            return RedirectResponse(url="/error", status_code=302)

    company_info = f"Company Name: {company_name}, Company Link: {company_link}"

    # Include file ID in company info if available
    if file_id:
        company_info += f", File ID: {file_id}"

    assistant_config['tool_sel'] = tool_type
    assistant_config['Model_sel'] = Model_type
    assistant_config['assistant_instructions'] = assistant_instructions
    assistant_config['company_info'] = company_info

    try:
        assistant = create_assistant(assistant_config)
        assistant_id = assistant.id  # Capture the assistant ID
    except Exception as e:
        print(f"Error creating assistant: {e}")
        return RedirectResponse(url="/error", status_code=302)

    # Create a new thread
    try:
        thread_id = await create_thread(company_info, assistant_id, file_id)
    except Exception as e:
        print(f"Error creating thread: {e}")
        return RedirectResponse(url="/error", status_code=302)

    # Insert IDs into the database
    try:
        await insert_assistant_data(company_name,company_link,assistant_id, thread_id, file_id)
    except Exception as e:
        print(f"Error inserting data into MongoDB: {e}")
        return RedirectResponse(url="/error", status_code=302)

    # Store the thread ID in the session
    request.session['thread_id'] = thread_id
    request.session['assistant_id'] = assistant_id  # Store assistant_id
    request.session['file_id'] = file_id  # Store file_id only if not None

    print(f"Company: {company_name}, Link: {company_link}, File Name: {file_input.filename if file_input else 'N/A'}, OpenAI File ID: {file_id if file_id else 'N/A'}, Thread ID: {thread_id}")

    return RedirectResponse(url="/chatbot", status_code=302)

@app.get("/chatbot", response_class=HTMLResponse)
async def chatbot_page(request: Request):
    return templates.TemplateResponse("chatbot.html", {"request": request})

@app.post("/process")
async def process_message(request: Request):
    data = await request.json()
    user_message = data['msg']

    thread_id = request.session.get('thread_id')
    assistant_id = request.session.get('assistant_id')  # Retrieve assistant_id
    file_id = request.session.get('file_id')  # file_id can be None

    if not thread_id:
        return {"response": "Thread not available. Please try again later."}

    # Add the user's message to the thread
    try:
        response_text = await add_message_to_thread(thread_id, user_message, assistant_id, file_id)
    except Exception as e:
        print(f"Error adding message to thread: {e}")
        return {"response": "Error processing message."}

    return {"response": response_text}
