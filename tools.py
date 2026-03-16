from gmail_auth import get_gmail_service
from googleapiclient.errors import HttpError

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

            # Place message snippet and Id in a dictionary
            msg = {"subject":subject,
                   "sender": sender,
                   "snippet":full_msg["snippet"],
                   "id":msg_id
                   }
            
            # Append the dictionary to the msg_list
            msgs_list.append(msg)
        return msgs_list
        
    except HttpError as e:
        print("No response")

def get_unread_count():
    result = service.users().messages().list(userId='me', labelIds=["UNREAD"], maxResults=10).execute()
    return result.get("resultSizeEstimate",0)

