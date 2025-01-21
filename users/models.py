from django.db import models
from django.contrib.auth.models import User

class GmailCredentials(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255)  # Store the Gmail access token
    refresh_token = models.CharField(max_length=255)  # Store the Gmail refresh token
    is_authorized = models.BooleanField(default=False)  # Track whether the Gmail account is authorized
    
    def __str__(self):
        return f"Gmail credentials for {self.user.username}"
