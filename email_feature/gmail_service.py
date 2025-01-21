from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pickle
import os
from google_auth_oauthlib.flow import InstalledAppFlow
import mimetypes

class GoogleApiService:
    def __init__(self, client_secret_file, api_name, api_version, *scopes):
        self.client_secret_file = client_secret_file
        self.api_name = api_name
        self.api_version = api_version
        self.scopes = [scope for scope in scopes[0]]
        self.credentials = None
        self.service = None

    def _load_credentials(self):
        pickle_file = f"token_{self.api_name}_{self.api_version}.pickle"
        if os.path.exists(pickle_file):
            with open(pickle_file, "rb") as token:
                self.credentials = pickle.load(token)

    def _authenticate(self):
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.client_secret_file, self.scopes)
                self.credentials = flow.run_local_server()
            
            pickle_file = f'token_{self.api_name}_{self.api_version}.pickle'
            with open(pickle_file, 'wb') as token:
                pickle.dump(self.credentials, token)

    def create_service(self):
        """Create and return the Google API service."""
        self._load_credentials()
        self._authenticate()
        
        if not self.credentials or not self.credentials.valid:
            raise Exception("Failed to authenticate or obtain valid credentials.")

        self.service = build(self.api_name, self.api_version, credentials=self.credentials)
        
        if not self.service:
            raise Exception("Failed to create the Gmail service.")
        
        return self.service

    def send_email_with_attachments(self, recipient, subject, body, sender_email, attachments):
        mime_message = MIMEMultipart()
        mime_message['to'] = recipient
        mime_message['subject'] = subject
        mime_message['from'] = sender_email
        mime_message.attach(MIMEText(body, 'plain'))

        # Attach files
        for attachment in attachments:
            content_type, encoding = mimetypes.guess_type(attachment)
            if content_type is None:
                content_type = 'application/octet-stream'
            main_type, sub_type = content_type.split('/', 1)
            file_name = os.path.basename(attachment)

            try:
                with open(attachment, 'rb') as f:
                    file_data = f.read()
                    my_file = MIMEBase(main_type, sub_type)
                    my_file.set_payload(file_data)
                    encoders.encode_base64(my_file)
                    my_file.add_header('Content-Disposition', 'attachment', filename=file_name)
                    mime_message.attach(my_file)
            except FileNotFoundError:
                raise Exception(f"Attachment not found: {attachment}")


        # Encode and send the email
        raw_string = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()

        # Send the email using Gmail API
        message = self.service.users().messages().send(userId='me', body={'raw': raw_string}).execute()
        return message

    def get_received_emails(self, max_results=10):
        """Fetch emails received from others using the Gmail API."""
        try:
            # Create the Gmail API service
            service = self.create_service()

            # Use the Gmail query to exclude sent emails and drafts
            query = '-from:me'  # Only retrieve emails not sent by the user
            response = service.users().messages().list(
                userId='me',
                maxResults=max_results,
                q=query
            ).execute()

            messages = response.get('messages', [])
            email_data = []

            for message in messages:
                # Fetch each email details
                msg = service.users().messages().get(userId='me', id=message['id']).execute()

                # Extract snippet
                snippet = msg.get('snippet', '')

                # Extract headers for 'From' and 'Subject'
                headers = msg.get('payload', {}).get('headers', [])
                sender_email = None
                subject = None

                for header in headers:
                    if header['name'] == 'From':
                        sender_email = header['value']
                    if header['name'] == 'Subject':
                        subject = header['value']

                # Extract only the email address from 'From' if it contains a name
                if sender_email:
                    import re
                    match = re.search(r'<(.+?)>', sender_email)
                    if match:
                        sender_email = match.group(1)  # Extract the email address only

                # Prepare email data
                email_info = {
                    'id': msg['id'],
                    'subject': subject or 'No Subject',  # Handle emails with no subject
                    'from': sender_email or 'Unknown Sender',
                    'snippet': snippet or 'No Snippet',
                }

                # Append email to the list
                email_data.append(email_info)

            return email_data

        except Exception as e:
            print(f"An error occurred: {e}")
            return []
                