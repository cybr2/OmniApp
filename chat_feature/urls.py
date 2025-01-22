from django.urls import path
from . import views

app_name = 'chat_feature'
urlpatterns = [
    path('chat/', views.chat_index, name='chat_index'),
    path('chat/<str:room_name>/', views.chat_room, name='chat_room'),
]