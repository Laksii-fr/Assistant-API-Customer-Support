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

async def update_assistant_details(assistant_id, name=None, instructions=None, tool_type=None, model_type=None):
    update_data = {}
    if name:
        update_data["name"] = name
    if instructions:
        update_data["instructions"] = instructions
    if tool_type:
        update_data["tools"] = [{"type": tool_type}]
    if model_type:
        update_data["model"] = model_type

    if not update_data:
        return None  # No updates to be made

    try:
        client = OpenAI()
        updated_assistant = client.beta.assistants.update(
            assistant_id,
            **update_data
        )
        return updated_assistant
    except Exception as e:
        print(f"Error updating assistant: {e}")
        return None
