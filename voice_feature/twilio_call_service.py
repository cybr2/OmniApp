from twilio.rest import Client
from django.conf import settings


client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


def make_call(to_number):
    try:
        call = client.calls.create(
            # record=True,
            url="https://2af3-112-206-75-24.ngrok-free.app/voice/",
            to=to_number,
            from_=settings.TWILIO_PHONE_NUMBER
        )
        print(f"Call SID: {call.sid}, Status: {call.status}")
        return call.sid
    except Exception as e:
        print(f"Error making call: {e}")
        raise e

def get_call_logs(start_date=None, end_date=None, to_number=None, from_number=None):
    """
    Fetch the call logs from Twilio.
    Optionally, filter by date range and phone numbers.

    :param start_date: Optional; start date to filter calls.
    :param end_date: Optional; end date to filter calls.
    :param to_number: Optional; phone number the call was made to.
    :param from_number: Optional; phone number the call was made from.
    :return: List of call logs.
    """
    try:
        calls = client.calls.list(
            start_time_after=start_date,
            start_time_before=end_date,
            to=to_number,
            from_=from_number
        )

        # Create a list to hold call logs
        call_logs = []
        for call in calls:
            call_logs.append({
                "sid": call.sid,
                "status": call.status,
                "to": call.to,
                "from": call.from_,
                "start_time": call.start_time,
                "end_time": call.end_time,
                "duration": call.duration,
                "price": call.price,
                "price_unit": call.price_unit,
            })
        
        return call_logs

    except Exception as e:
        print(f"Error fetching call logs: {e}")
        raise e
