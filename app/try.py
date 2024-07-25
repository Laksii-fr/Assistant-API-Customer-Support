from openai import OpenAI
import os

import openai
openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()


assistant = client.beta.assistants.create(
  name="Financial Analyst Assistant",
  instructions="You are an expert financial analyst. Use you knowledge base to answer questions about audited financial statements.",
  model="gpt-4o",
  tools=[{"type": "file_search"}],
) 


vector_store = client.beta.vector_stores.create(name="Financial Statements")
 

file_paths = ["static/css/styles.css"]
file = client.files.create(
  file=open("static/css/styles.css", "rb"),
  purpose='assistants'
)
file_streams = [open(path, "rb") for path in file_paths]

file_id = file.id

file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
  vector_store_id=vector_store.id, files=file_streams
)


assistant = client.beta.assistants.update(
  assistant_id=assistant.id,
  tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)

