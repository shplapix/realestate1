# chat/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Chat, Message
from realtors.models import Realtor
from listings.models import Listing
from django.db.models import Max

@login_required 
def chat_index(request):
    """Отображает список всех чатов пользователя, отсортированный по последнему сообщению."""
    
    # Получаем все чаты пользователя (как покупателя или как риелтора)
    if hasattr(request.user, 'realtor'):
        user_chats = Chat.objects.filter(realtor=request.user.realtor)
    else:
        user_chats = Chat.objects.filter(user=request.user)
    
    # Получаем ID последнего сообщения и его временную метку для сортировки
    chats_with_last_message = user_chats.annotate(
        last_message_time=Max('messages__timestamp')
    ).order_by('-last_message_time', '-created_at')

    context = {
        'chats': chats_with_last_message,
    }
    return render(request, 'chat/chat_index.html', context)

@login_required
def start_chat(request, realtor_id, listing_id):
    """Создает или находит чат и перенаправляет на него."""
    
    realtor = get_object_or_404(Realtor, pk=realtor_id)
    listing = get_object_or_404(Listing, pk=listing_id)
    user = request.user

    # 1. Попытка найти или создать чат
    # get_or_create возвращает (объект, created_bool)
    chat, created = Chat.objects.get_or_create(
        user=user, 
        realtor=realtor,
        listing=listing, 
        defaults={
            'user': user,
            'realtor': realtor,
            'listing': listing,
        }
    )

    # 2. Перенаправляем на страницу чата
    return redirect('chat:room', chat_id=chat.id)

@login_required
def chat_room(request, chat_id):
    """Отображает конкретный чат и его сообщения."""
    
    chat = get_object_or_404(Chat, pk=chat_id)

    # Проверка прав: покупатель или риелтор
    is_buyer = request.user == chat.user
    is_realtor = False
    if hasattr(request.user, 'realtor'):
        is_realtor = request.user.realtor == chat.realtor

    if not is_buyer and not is_realtor:
        messages.error(request, "У вас немає доступу до цього чату.")
        return redirect('index') 
    
    messages_list = chat.messages.all()

    # Mark messages as read
    if is_buyer:
        # If buyer, mark messages from realtor as read
        chat.messages.filter(is_realtor_sender=True, is_read=False).update(is_read=True)
    elif is_realtor:
        # If realtor, mark messages from buyer as read
        chat.messages.filter(is_realtor_sender=False, is_read=False).update(is_read=True)

    # Get all chats for sidebar
    if hasattr(request.user, 'realtor'):
        all_chats = Chat.objects.filter(realtor=request.user.realtor).annotate(
            last_message_time=Max('messages__timestamp')
        ).order_by('-last_message_time', '-created_at')
    else:
        all_chats = Chat.objects.filter(user=request.user).annotate(
            last_message_time=Max('messages__timestamp')
        ).order_by('-last_message_time', '-created_at')

    context = {
        'chat': chat,
        'chat_messages': messages_list,
        'all_chats': all_chats,
        'realtor_name': chat.realtor.name,
        'listing_title': chat.listing.title if chat.listing else "Загальний чат",
    }
    return render(request, 'chat/chat_room.html', context)


@login_required
def send_message(request, chat_id):
    """Обрабатывает отправку нового сообщения (должна быть функцией POST)."""
    if request.method == 'POST':
        chat = get_object_or_404(Chat, pk=chat_id)
        content = request.POST.get('content', '').strip()
        
        if not content:
            messages.error(request, "Повідомлення не може бути порожнім.")
            return redirect('chat:room', chat_id=chat.id)

        # Логика определения отправителя
        is_realtor_sender = False 
        
        if hasattr(request.user, 'realtor') and request.user.realtor == chat.realtor:
             is_realtor_sender = True
        elif request.user == chat.user:
             is_realtor_sender = False
        else:
             messages.error(request, "Ви не можете відправляти повідомлення в цей чат.")
             return redirect('chat:room', chat_id=chat.id)
        
        # Создание сообщения
        Message.objects.create(
            chat=chat,
            content=content,
            is_realtor_sender=is_realtor_sender
        )
    
    # Перенаправляем обратно в комнату чата
    return redirect('chat:room', chat_id=chat.id)