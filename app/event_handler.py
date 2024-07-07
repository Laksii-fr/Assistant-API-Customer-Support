from openai import AssistantEventHandler
import os
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

class EventHandler(AssistantEventHandler):
    def on_text_created(self, text) -> None:
        print(f"\nassistant > ", end="", flush=True)
      
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
