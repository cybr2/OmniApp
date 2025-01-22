from django.shortcuts import render, redirect
from social_django.models import UserSocialAuth
from .gmail_service import GoogleApiService
import os
import requests
from django.core.files.storage import default_storage

CLIENT_SECRET_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config/client_secret.json')
API_NAME = 'gmail'
API_VERSION = 'v1'
SCOPES = ['https://mail.google.com/']

# Initialize GmailService (assuming you have set up this service)
gmail_service = GoogleApiService(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
gmail_service.create_service()

def send_email_view(request):
    if request.method == "POST":
        recipient = request.POST.get("recipient")
        subject = request.POST.get("subject")
        body = request.POST.get("body")

        # Authenticate and get user email
        try:
            social_auth = UserSocialAuth.objects.get(user=request.user, provider="google-oauth2")
            access_token = social_auth.extra_data.get('access_token')
            user_info_url = 'https://www.googleapis.com/oauth2/v1/userinfo?alt=json'
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get(user_info_url, headers=headers)
            sender_email = response.json().get('email')
        except Exception as e:
            return render(request, "email_feature/error.html", {"error_code": 500, "error_message": f"Error fetching user email: {e}"})

        # Process attachments
        attachments = []
        for attachment in request.FILES.getlist('attachment'):
            temp_path = default_storage.save(attachment.name, attachment)
            attachments.append(default_storage.path(temp_path))

        try:
            response = gmail_service.send_email_with_attachments(
                recipient=recipient,
                subject=subject,
                body=body,
                sender_email=sender_email,
                attachments=attachments,
            )
            # Clean up temporary files
            for attachment in attachments:
                default_storage.delete(attachment)
            return render(request, "email_feature/success.html", {"message_id": response['id']})
        except Exception as e:
            return render(request, "email_feature/error.html", {"error_code": 500, "error_message": f"Error sending email: {e}"})
    
    return render(request, "email_feature/send_email.html")

def receive_email_view(request):
    try:
        # Get the authenticated user's Google credentials
        social_auth = UserSocialAuth.objects.get(user=request.user, provider="google-oauth2")
    except UserSocialAuth.DoesNotExist:
        return render(request, "email_feature/error.html", {
            "error_code": 403,
            "error_message": "Google authentication not found for the user."
        })

    # Fetch the access token from social_auth extra_data
    access_token = social_auth.extra_data.get('access_token')

    if not access_token:
        return render(request, "email_feature/error.html", {
            "error_code": 403,
            "error_message": "Google OAuth token not available."
        })

    try:

        # Fetch received emails using the `get_received_emails` method
        email_data = gmail_service.get_received_emails(max_results=5)

        if email_data:
            return render(request, "email_feature/receive_emails.html", {'emails': email_data})
        else:
            return render(request, "email_feature/receive_emails.html", {'emails': [], 'message': "No emails found."})

    except Exception as e:
        return render(request, "email_feature/email_feature/error.html", {
            "error_code": 500,
            "error_message": str(e)
        })