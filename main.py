from fastapi import FastAPI, UploadFile, Form, File, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse

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
    file_input: UploadFile = File(...)
):
    file_path = await save_file(file_input)
    file_id = await upload_file_to_openai(file_path)

    if not file_id:
        return RedirectResponse(url="/error", status_code=302)

    global company_info

    company_info = f"Company Name: {company_name}, Company Link: {company_link}, File ID: {file_id}"
    assistant_config['tool_sel'] = tool_type
    assistant_config['assistant_instructions'] = assistant_instructions
    assistant_config['company_info'] = company_info

    assistant = create_assistant(assistant_config)
    if not assistant:
        return RedirectResponse(url="/error", status_code=302)

    thread_id = await create_thread(company_info, assistant, file_id)
    if not thread_id:
        return RedirectResponse(url="/error", status_code=302)

    request.session['thread_id'] = thread_id
    request.session['file_id'] = file_id

    print(f"Company: {company_name}, Link: {company_link}, File Name: {file_input.filename}, OpenAI File ID: {file_id}, Thread ID: {thread_id}")

    return RedirectResponse(url="/chatbot", status_code=302)


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
    assistant = create_assistant(assistant_config)

    # Add the user's message to the thread
    response_text = await add_message_to_thread(thread_id, user_message, file_id, assistant)

    return {"response": response_text}
