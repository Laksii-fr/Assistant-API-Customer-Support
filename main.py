from fastapi import FastAPI, UploadFile, Form, File, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse, JSONResponse
from app.database import insert_assistant_data, insert_assistant_threads, get_threads_for_assistant, get_messages_for_thread, update_assistant_data, get_all_assistants
from app.assistant import create_assistant, update_assistant_details
from app.upload import upload_file_to_openai
from app.threads import create_thread, add_message_to_thread , save_message ,get_all_thread_history,prettify_all_response
from typing import List
from datetime import datetime

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
    Model_type: str = Form(...),
    file_inputs: List[UploadFile] = File(None)
):
    global company_info
    file_ids = []

    print(f"Received tool_type: {tool_type}")
    if tool_type != "code_interpreter":
        print("Executed 1")
        print(f"file_inputs: {file_inputs}")
        # Upload the files to OpenAI
        if file_inputs:
            print("Executed 1.1")
            for file_input in file_inputs:
                print(f"Processing file: {file_input.filename}")
                print("Executed 1.2")
                file_id = await upload_file_to_openai(file_input)
                print("Executed 1.3")
                if file_id:
                    file_ids.append(file_id)
                print(f"File ID: {file_id}")

        if not file_ids:
            print("No file IDs generated")
            return RedirectResponse(url="/error", status_code=302)

    company_info = f"Company Name: {company_name}, Company Link: {company_link}"

    # Include file IDs in company info if available
    if file_ids:
        company_info += f", File IDs: {', '.join(file_ids)}"

    assistant_config['tool_sel'] = tool_type
    assistant_config['Model_sel'] = Model_type
    assistant_config['assistant_instructions'] = assistant_instructions
    assistant_config['assistant_tool'] = assistant_instructions
    assistant_config['company_info'] = company_info

    try:
        assistant = create_assistant(assistant_config)
        assistant_id = assistant.id  # Capture the assistant ID
    except Exception as e:
        print(f"Error creating assistant: {e}")
        return RedirectResponse(url="/error", status_code=302)

    # Create a new thread
    try:
        thread_id = await create_thread(company_info, assistant_id, file_ids)
    except Exception as e:
        print(f"Error creating thread: {e}")
        return RedirectResponse(url="/error", status_code=302)

    # Insert IDs into the database
    try:
        await insert_assistant_data(company_name, assistant_instructions, company_link, assistant_id, Model_type, tool_type, file_ids)
        await insert_assistant_threads(assistant_id, thread_id, file_ids)
    except Exception as e:
        print(f"Error inserting data into MongoDB: {e}")
        return RedirectResponse(url="/error", status_code=302)

    # Store the thread ID in the session
    request.session['thread_id'] = thread_id
    request.session['assistant_id'] = assistant_id  # Store assistant_id
    request.session['file_ids'] = file_ids  # Store file_ids

    print(f"Company: {company_name}, Link: {company_link}, File Names: {[file_input.filename for file_input in file_inputs] if file_inputs else 'N/A'}, OpenAI File IDs: {file_ids if file_ids else 'N/A'}, Thread ID: {thread_id}")

    return RedirectResponse(url="/chatbot", status_code=302)

@app.get("/chatbot", response_class=HTMLResponse)
async def chatbot_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.post("/process")
async def process_message(request: Request):
    data = await request.json()
    user_message = data['msg']

    thread_id = request.session.get('thread_id')
    assistant_id = request.session.get('assistant_id')  # Retrieve assistant_id
    file_ids = request.session.get('file_ids')  # file_ids can be None

    now = datetime.now()
    time_str = now.strftime("%H:%M")

    if not thread_id:
        return {"response": "Thread not available. Please try again later."}

    # Add the user's message to the thread
    try:
        response_text = await add_message_to_thread(thread_id, user_message, assistant_id, file_ids)
        await save_message(thread_id, "user", user_message, time_str)
        await save_message(thread_id, "bot", response_text, time_str)
    except Exception as e:
        print(f"Error adding message to thread: {e}")
        return {"response": "Error processing message."}

    return {"response": response_text}

@app.post("/new_thread")
async def new_thread(request: Request):
    assistant_id = request.session.get('assistant_id')
    file_ids = request.session.get('file_ids')

    if not assistant_id:
        return JSONResponse({"error": "Assistant not available. Please try again later."}, status_code=400)

    # Create a new thread
    try:
        company_info = assistant_config.get('company_info', 'Company Information')
        thread_id = await create_thread(company_info, assistant_id, file_ids)
        await insert_assistant_threads(assistant_id, thread_id, file_ids)
        request.session['thread_id'] = thread_id
    except Exception as e:
        print(f"Error creating new thread: {e}")
        return JSONResponse({"error": "Error creating new thread."}, status_code=500)

    return JSONResponse({"thread_id": thread_id}, status_code=200)

@app.get("/threads")
async def get_threads(request: Request):
    assistant_id = request.session.get('assistant_id')
    if not assistant_id:
        return JSONResponse({"error": "Assistant not available."}, status_code=400)

    try:
        threads = await get_threads_for_assistant(assistant_id)
    except Exception as e:
        print(f"Error retrieving threads: {e}")
        return JSONResponse({"error": "Error retrieving threads."}, status_code=500)

    return JSONResponse({"threads": threads}, status_code=200)

@app.get("/load_thread/{thread_id}")
async def load_thread(thread_id: str):
    try:
        messages = await get_all_thread_history(thread_id)  # Retrieve messages for the thread
        prettified_messages = prettify_all_response(messages)  # Prettify messages if needed
    except Exception as e:
        print(f"Error loading thread: {e}")
        return JSONResponse({"error": "Error loading thread."}, status_code=500)

    return JSONResponse({"messages": prettified_messages}, status_code=200)

# Update existing Assistant 

@app.get("/update_assistant", response_class=HTMLResponse)
async def update_assistant_page(request: Request):
    assistants = await get_all_assistants()
    return templates.TemplateResponse("update_assistant.html", {"request": request, "assistants": assistants})

@app.post("/update_assistant", response_class=RedirectResponse)
async def update_assistant(
    request: Request,
    assistant_id: str = Form(...),
    assistant_name: str = Form(None),
    assistant_instructions: str = Form(None),
    tool_type: str = Form(None),
    Model_type: str = Form(None)
):
    try:
        updated_assistant = await update_assistant_details(assistant_id, assistant_name, assistant_instructions, tool_type, Model_type)
        if updated_assistant:
            await update_assistant_data(assistant_id, assistant_name, assistant_instructions, tool_type, Model_type)
        else:
            raise ValueError("Failed to update assistant using OpenAI API")
    except Exception as e:
        print(f"Error updating assistant: {e}")
        return RedirectResponse(url="/error", status_code=302)

    return RedirectResponse(url="/", status_code=302)
