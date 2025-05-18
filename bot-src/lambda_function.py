import json
import os
import requests

# Get the Telegram Bot Token from environment variables
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/"

def send_message(chat_id, text):
    """Sends a message to a specific chat_id via the Telegram Bot API."""
    url = f"{TELEGRAM_API_URL}sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes
        print(f"Message sent successfully to {chat_id}: {text}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending message: {e}")
        # In a real application, you might want to handle this more gracefully
        # or re-raise to let Lambda know something went wrong.

def lambda_handler(event, context):
    """
    AWS Lambda handler function.
    Receives an event from API Gateway (which is triggered by Telegram webhook).
    """
    print(f"Received event: {json.dumps(event)}")

    try:
        # Telegram sends the update as a JSON string in the body of the HTTP request
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body') # Already a dict if testing directly or from some API Gateway configs

        if not body or 'message' not in body:
            print("Not a message update or body is empty/missing.")
            return {'statusCode': 200, 'body': json.dumps('Not a message update or body is empty.')}

        message = body['message']
        chat_id = message['chat']['id']
        
        # Check if the message contains text and if it's the /start command
        if 'text' in message and message['text'].strip().lower() == '/start':
            user_first_name = message.get('from', {}).get('first_name', 'User')
            welcome_text = f"Hello {user_first_name}! Welcome to the bot. How can I help you today?"
            send_message(chat_id, welcome_text)
        else:
            # Optionally, handle other messages or ignore them
            print(f"Received non-start command or non-text message from {chat_id}")
            # send_message(chat_id, "I can only understand /start for now.")

        return {
            'statusCode': 200,
            'body': json.dumps('Message processed')
        }

    except Exception as e:
        print(f"Error processing update: {e}")
        # Important: Return a 200 OK to Telegram even if an error occurs in your processing
        # to prevent Telegram from resending the update. Log the error for debugging.
        return {
            'statusCode': 200, # Or 500 if you want to signal an internal error, but Telegram might retry
            'body': json.dumps(f'Error: {str(e)}')
        }

# For local testing (optional)
if __name__ == "__main__":
    # Simulate a Telegram /start update event (as API Gateway would send it)
    test_event = {
        "body": json.dumps({
            "update_id": 123456789,
            "message": {
                "message_id": 1365,
                "from": {
                    "id": 123456789,
                    "is_bot": False,
                    "first_name": "Test",
                    "last_name": "User",
                    "username": "testuser",
                    "language_code": "en"
                },
                "chat": {
                    "id": 123456789, # Same as user_id for private chat
                    "first_name": "Test",
                    "last_name": "User",
                    "username": "testuser",
                    "type": "private"
                },
                "date": 1589912678,
                "text": "/start"
            }
        })
    }
    # You would need to set TELEGRAM_BOT_TOKEN environment variable locally to test send_message
    # For example: os.environ['TELEGRAM_BOT_TOKEN'] = "YOUR_ACTUAL_BOT_TOKEN" 
    # if TELEGRAM_BOT_TOKEN:
    #    lambda_handler(test_event, None)
    # else:
    #    print("TELEGRAM_BOT_TOKEN not set. Skipping local test execution.")
    print("Local test setup complete. Set TELEGRAM_BOT_TOKEN and uncomment call to test.") 