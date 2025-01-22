from django.shortcuts import render
from .twilio_service import send_sms, get_all_sms, get_message_by_sender
from phonenumbers import parse, is_valid_number, format_number, PhoneNumberFormat

def sanitize_phone_number(phone_number, default_country='PH'):
    """
    Sanitize a phone number and convert it to E.164 format.
    """
    try:
        parsed_number = parse(phone_number, default_country)  # Parse the phone number with default country
        if is_valid_number(parsed_number):  # Check if the number is valid
            return format_number(parsed_number, PhoneNumberFormat.E164)  # Return E.164 format
        else:
            raise ValueError(f"Invalid phone number: {phone_number}")
    except Exception as e:
        raise ValueError(f"Error processing phone number: {e}")

def send_sms_view(request):
    if request.method == 'POST':
        to_number = request.POST.get('to_number', '').strip()
        message = request.POST.get('message', '').strip()

        if not to_number or not message:
            return render(request, 'send_sms.html', {'error': 'Please provide both a phone number and a message.'})
        
        try:
            # Sanitize the phone number
            sanitized_number = sanitize_phone_number(to_number)
            send_sms(sanitized_number, message)
            success_message = f"SMS successfully sent to {sanitized_number}!"
            return render(request, 'success.html', {'success_message': success_message})
        except ValueError as ve:
            return render(request, 'send_sms.html', {'error': str(ve)})
        except Exception as e:
                return render(request, 'send_sms.html', {'error': f'Error sending SMS: {e}'})
    return render(request, 'send_sms.html', {'error': None})

def index(request):
    return render(request, 'index.html')

def inbox_sms_view(request):
    try:
        sender_messages = get_all_sms()
        return render(request, 'inbox_sms.html', {'sender_messages': sender_messages, 'error': None})
    except Exception as e:
        return render(request, 'inbox_sms.html', {'error': f'Error fetching SMS: {e}', 'sender_messages': None})
    
def view_sms(request, sender):
    try:
        # Fetch the messages sent by the given sender
        messages = get_message_by_sender(sender)

        # Pass the messages to the template
        return render(request, 'view_sms.html', {'messages': messages, 'error': None})

    except Exception as e:
        # Handle errors fetching the messages
        return render(request, 'view_sms.html', {'error': str(e), 'messages': None})