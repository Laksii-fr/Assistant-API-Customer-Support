from openai import OpenAI
import os
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

def create_assistant(config):
    if 'tool_sel' not in config or 'assistant_instructions' not in config:
        raise ValueError("Assistant configuration is not set properly")

    tool_sel = config['tool_sel']
    Model_sel = config['Model_sel']
    assistant_instructions = config['assistant_instructions']
    company_info = config.get('company_info', '')

    try:
        client = OpenAI()
        assistant = client.beta.assistants.create(
            name="Company Assistant",
            instructions=assistant_instructions + f", Company Information: {company_info}",
            tools=[{"type": tool_sel}],  # Use the selected tool type
            model=Model_sel,
        )
        return assistant
    except Exception as e:
        print(f"Error creating assistant: {e}")
        return None  # Ensure you handle this case in your calling code
