from groq import Groq
from dotenv import load_dotenv
import os
import json
from tools import get_unread_count, get_unread_messages, search_email, read_full_email, delete_email, send_email

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
{
    "type": "function",
    "function": {
        "name": "search_email",
        "description": "A function that searches for an email or emails based on a query.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The question the user asks or information the user needs."
                }
            },
            "required": ["query"]
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "read_full_email",
        "description": "A function that reads the full content of an email. Which contains subject, sender and body.",
        "parameters": {
            "type": "object",
            "properties": {
                "email_id": {
                    "type": "string",
                    "description": "The unique identifier used to find the email."
                }
            },
            "required": ["email_id"]
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "delete_email",
        "description": "A function that deletes an email given the ID of the email to be deleted.",
        "parameters": {
            "type": "object",
            "properties": {
                "email_id": {
                    "type": "string",
                    "description": "The unique identifier used to find the email."
                }
            },
            "required": ["email_id"]
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "send_email",
        "description": "A function that sends an email. It needs 'to','subject', and 'body'.",
        "parameters": {
            "type": "object",
            "properties": {
                "to": {
                    "type": "string",
                    "description": "The email address of the person the message is being sent to."
                },
                "subject": {
                    "type": "string",
                    "description": "A short sentence or phrase that explains what the email is about."
                },
                "body": {
                    "type": "string",
                    "description": "The main content of the email. The message being sent."
                }
            },
            "required": ["to","subject","body"]
        }
    }
}
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
        "get_unread_count": get_unread_count,
        "search_email":search_email,
        "read_full_email":read_full_email,
        "delete_email":delete_email,
        "send_email":send_email
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
