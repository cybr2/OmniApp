import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define the scopes you need. These are the most common scopes for Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_credentials(user):
    """Handles the OAuth2 authentication and returns Gmail API service."""
    
    creds = None
    token_path = f'./tokens/{user.id}_token.json'  # Store each user's token separately

    # If token exists, load it
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path)
    
    # If credentials are not available or expired, initiate OAuth2 flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Make sure the path is relative to your project directory
            credentials_file_path = os.path.join(os.path.dirname(__file__), '../config/client_secret.json')

            # Check if the credentials file exists
            if not os.path.exists(credentials_file_path):
                raise FileNotFoundError(f"Credentials file not found at {credentials_file_path}")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file_path,  # Corrected path to credentials.json
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next session
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    # Use the credentials to build the Gmail service
    service = build('gmail', 'v1', credentials=creds)
    return service
