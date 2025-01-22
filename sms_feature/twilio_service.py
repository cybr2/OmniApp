from twilio.rest import Client
from django.conf import settings

client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
def send_sms(to_number, message):
    try:
        sms_message = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=to_number
        )
        print(f"Message SID: {sms_message.sid}, Status: {sms_message.status}")
        return sms_message.sid
    except Exception as e:
        print(f"Error sending SMS: {e}")
        raise e
    
def get_all_sms():
    try:
        # Fetch all messages (both inbound and outbound)
        messages = client.messages.list(limit=10)

        # Process and group messages by sender (from)
        sender_messages = {}
        for message in messages:
            sender = message.from_
            if sender not in sender_messages:
                sender_messages[sender] = []
            sender_messages[sender].append(message)

        # Return the grouped messages
        return sender_messages

    except Exception as e:
        print(f"Error fetching SMS: {e}")
        raise Exception(f"Error fetching SMS: {e}")

def get_message_by_sender(sender):
    try:
        # Fetch all messages and filter by the sender
        all_messages = client.messages.list(from_=sender)

        return all_messages
    except Exception as e:
        raise Exception(f"Error fetching messages for sender {sender}: {e}")


