from django.shortcuts import render
from datetime import datetime, timedelta
from .twilio_call_service import get_call_logs, make_call
from phonenumbers import parse, is_valid_number, format_number, PhoneNumberFormat
from django.http import HttpResponse
from twilio.twiml.voice_response import VoiceResponse


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

# Create your views here.
def index(request):
    return render(request, 'voice_feature/index.html')

def initiate_call_view(request):
    call_sid = None
    error_message = None
    
    if request.method == "POST":
        to_number = request.POST.get('to_number')  # Get the phone number from the form
        if to_number:
            try:
                sanitize_number = sanitize_phone_number(to_number)
                # Call the service to initiate the call
                call_sid = make_call(sanitize_number)
            except Exception as e:
                error_message = f"Error initiating call: {str(e)}"
    
    return render(request, 'voice_feature/initiate_call.html', {
        'call_sid': call_sid,
        'error_message': error_message
    })

def voice_response(request):
    """Generate a TwiML response for the call."""
    resp = VoiceResponse()
    resp.say("Hello, this is a test call from Twilio.", voice="alice")
    resp.record(max_length=30, play_beep=True)
    resp.hangup()
    return HttpResponse(str(resp), content_type="text/xml")



def call_logs_view(request):
    # Fetch call logs for the past 30 days as an example
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    try:
        # Get call logs for the date range
        call_logs = get_call_logs(start_date=start_date, end_date=end_date)
    except Exception as e:
        call_logs = []
        error_message = f"Error fetching call logs: {str(e)}"
    
    # Pass the call logs and any error message to the template
    return render(request, 'voice_feature/call_logs.html', {
        'call_logs': call_logs,
        'error_message': error_message if 'error_message' in locals() else None
    })
