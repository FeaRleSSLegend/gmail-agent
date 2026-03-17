from gmail_auth import get_gmail_service
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
import base64
import re

service = get_gmail_service()

def get_unread_messages():
    try:
        # Calling the gmail API
        result = service.users().messages().list(userId='me', labelIds=["UNREAD"], maxResults=10).execute()

        messages = result.get("messages", [])

        if not messages:
            return "No messages found"
        
        # If messages are found
        msgs_list = []

        # Loop through each message to get the ID and a message snippet
        for message in messages:
            msg_id = message["id"]

            # Get the full message
            full_msg = service.users().messages().get(userId="me", id=msg_id).execute()
            headers = full_msg["payload"]["headers"]
            subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No subject")
            sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
            date = next((h["value"] for h in headers if h["name"] == "Date"), "Unknown date")

            # Place message snippet and Id in a dictionary
            msg = {"subject":subject,
                   "sender": sender,
                   "snippet":full_msg["snippet"],
                   "id":msg_id,
                   "date":date
                   }
            
            # Append the dictionary to the msg_list
            msgs_list.append(msg)
        return msgs_list
        
    except HttpError as e:
        print("No response")

def get_unread_count():
    result = service.users().messages().list(userId='me', labelIds=["UNREAD"], maxResults=10).execute()
    return result.get("resultSizeEstimate",0)


def search_email(query:str):
    try:
        result = service.users().messages().list(userId='me',q=query, maxResults=10).execute()

        messages = result.get("messages", [])

        if not messages:
            return "No messages found"
        
        found_messages = []

        for message in messages:
            msg_id = message["id"]

            # Get the full message
            full_msg = service.users().messages().get(userId="me", id=msg_id).execute()
            headers = full_msg["payload"]["headers"]
            subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No subject")
            sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
            date = next((h["value"] for h in headers if h["name"] == "Date"), "Unknown date")

            # Place message snippet and Id in a dictionary
            msg = {"subject":subject,
                "sender": sender,
                "snippet":full_msg["snippet"],
                "id":msg_id,
                "date":date
                }
            
            # Append the dictionary to the msg_list
            found_messages.append(msg)
        return found_messages
        
    except HttpError as e:
        return "No response"

def read_full_email(email_id:str):
    try:
        full_msg = service.users().messages().get(userId='me', id=email_id).execute()
        

        if not full_msg:
            return "Message not found!"
        
        headers = full_msg["payload"]["headers"]
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No subject")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
        date = next((h["value"] for h in headers if h["name"] == "Date"), "Unknown date")
        
        payload = full_msg["payload"]

        if "parts" in payload:
            # multipart email - body is in parts
            data = payload["parts"][0]["body"]["data"]
        else:
            # simple email - body is directly in payload
            data = payload["body"]["data"]

        body = base64.urlsafe_b64decode(data).decode("utf-8")
        clean_body = re.sub(r'<[^>]+>', '', body)


        message ={
            "subject":subject,
            "sender": sender,
            "body":clean_body,
            "date":date
                }

        
        return message
    except HttpError:
        return "No response"
    
def delete_email(email_id:str):
    try:
        service.users().messages().delete(userId="me", id=email_id).execute()
        return "Email deleted successfully"
    except Exception as e:
        return f"Error: {e}"

def send_email(to:str, subject:str, body:str):
    try:
        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject

        raw_mail = base64.urlsafe_b64encode(message.as_bytes()).decode()
        service.users().messages().send(userId="me", body={"raw":raw_mail}).execute()
        return f"Message sent to {to} successfully"
    except Exception as e:
        return f"Error: {e}"