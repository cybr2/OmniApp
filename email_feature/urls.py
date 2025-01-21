from django.urls import path
from . import views

app_name = 'email_feature'
urlpatterns = [
    path('compose/', views.send_email_view, name='send_email'),
    path('inbox/', views.receive_email_view, name='receive_emails')

]