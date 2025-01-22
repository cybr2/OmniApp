from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Message
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.cache import cache
from datetime import datetime
from django.utils import timezone

@login_required
def chat_index(request):
    # Get unique pairs of users (rooms) by combining sender and receiver
    users = User.objects.exclude(id=request.user.id)

    # rooms = Message.objects.values_list('sender', 'receiver').distinct()
    # print(rooms)
    # # Flatten the list and eliminate duplicates
    # rooms = set([room[0] for room in rooms] + [room[1] for room in rooms])
    
    return render(request, 'chat_feature/index.html', {'users': users})

@login_required
def chat_room(request, room_name):
    search_query = request.GET.get('search', '')  # Search query
    cache_key = f"chat_room_{room_name}_{search_query}"  # Cache key based on room and search query
    chats = cache.get(cache_key)  # Try to get cached chats

    if not chats:
        chats = Message.objects.filter((Q(sender=request.user) & Q(receiver__username=room_name)) | (Q(sender__username=room_name) & Q(receiver=request.user)) | (Q(sender__username=room_name) & Q(receiver__username=room_name))).order_by('timestamp')

        if search_query:
            chats = chats.filter(content__icontains=search_query)

        cache.set(cache_key, chats, timeout=60*15)  # Cache for 15 minutes

    # Apply pagination
    paginator = Paginator(chats, 10)  # Show 10 messages per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    users = User.objects.exclude(id=request.user.id)  # Get all users except the logged-in user

    # Get the last message for each user
    user_last_messages = []
    for user in users:
        last_message = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=user)) |
            (Q(receiver=request.user) & Q(sender=user))
        ).order_by('-timestamp').first()

        user_last_messages.append({
            'user': user,
            'last_message': last_message
        })

    # Sort user_last_messages by the timestamp of the last message in descending order
    # user_last_messages = []
    # for user in users:
    #     last_message = Message.objects.filter((Q(sender=request.user) & Q(receiver=user)) | (Q(receiver=request.user) & Q(sender=user))).order_by('-timestamp').first()

    #     user_last_messages.append({
    #         'user': user,
    #         'last_message': last_message
    #     })

    return render(request, 'chat_feature/chat_room.html', {
        'room_name': room_name,
        'chats': page_obj,  # Use paginated chats
        'users': users,
        'user_last_messages': user_last_messages,
        'search_query': search_query,
    })