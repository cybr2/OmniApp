from django.urls import path,include
from . import views

app_name = 'sms_feature'
urlpatterns = [
    path('create/', views.send_sms_view, name='send_sms'),
    path('', views.index, name='index'),
    path('inbox/', views.inbox_sms_view, name='inbox_sms'),
    path('inbox/<str:sender>/', views.view_sms, name='view_sms'),
]