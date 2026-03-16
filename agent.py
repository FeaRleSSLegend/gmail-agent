from groq import Groq
from dotenv import load_dotenv
import os
import json
from tools import get_unread_count, get_unread_messages

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

tools = [
    {
    "type": "function",
    "function": {
        "name": "get_unread_messages",
        "description": "Returns a list of dictionaries containing the subject, sender, snippet and id of the last 10 unread emails",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "get_unread_count",
        "description": "A function that fetches the total number of unread messages.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
},
]

def run_agent(query: str):
    # Set Up the messages
    messages = [
        {"role": "system", "content": "You are a personal email assistant with access to the user's Gmail account. Help the user manage their emails by reading, summarizing, and providing information about their inbox."},
        {"role":"user", "content": f"User Question: {query}."}
    ]

    # The list of available tools
    available_tools = {
        "get_unread_messages": get_unread_messages,
        "get_unread_count": get_unread_count
    }

    # The loop to run the agent
    while True:
        # Get a response from the model
        response = client.chat.completions.create(
            messages=messages,
            model="moonshotai/kimi-k2-instruct-0905",
            tools=tools
        )


        # Check if groq is done responnding or has more to do
        if response.choices[0].finish_reason == "tool_calls": # Groq's response to this is usually "tool_calls or stop"
            # Add groq's response to messages so it remembers what it was meant to do
            messages.append(response.choices[0].message)

            # Loop through each function the LLM called and call it
            for tool_call in response.choices[0].message.tool_calls:
                name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)


                # Calling the function based on the tool_call
                result = available_tools[name](**arguments)

                # Append to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": name,
                    "content": str(result)
                })
             
        else:
            print(response.choices[0].message.content)
            break
