from django.shortcuts import render
from django.urls import path
from . import views

app_name = 'voice_feature'
urlpatterns = [
    path('', views.index, name='index'),
    path('initiate_call/', views.initiate_call_view, name='initiate_call'),
    path('call_logs/', views.call_logs_view, name='call_logs'),
]