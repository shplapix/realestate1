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
    
    # Получаем все чаты пользователя
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

    # Проверка прав: только участник чата (покупатель) может его просматривать.
    if request.user != chat.user:
        # NOTE: Если нужно, чтобы риелтор тоже мог видеть чат, 
        # здесь нужно добавить проверку: or request.user.realtor == chat.realtor
        messages.error(request, "У вас нет доступа к этому чату.")
        return redirect('index') 
    
    messages_list = chat.messages.all()

    context = {
        'chat': chat,
        'messages': messages_list,
        'realtor_name': chat.realtor.name,
        'listing_title': chat.listing.title if chat.listing else "Общий чат",
    }
    return render(request, 'chat/chat_room.html', context)


@login_required
def send_message(request, chat_id):
    """Обрабатывает отправку нового сообщения (должна быть функцией POST)."""
    if request.method == 'POST':
        chat = get_object_or_404(Chat, pk=chat_id)
        content = request.POST.get('content', '').strip()
        
        if not content:
            messages.error(request, "Сообщение не может быть пустым.")
            return redirect('chat:room', chat_id=chat.id)

        # Логика определения отправителя
        is_realtor_sender = False 
        
        # Проверка, является ли текущий пользователь покупателем в этом чате
        if request.user == chat.user:
            is_realtor_sender = False 
        
        # Если пользователь не покупатель, это может быть риелтор.
        # В вашем текущем проекте модели Realtor и User не связаны напрямую, 
        # поэтому для простоты мы предполагаем, что сообщение отправлено покупателем (False).
        # Для корректной поддержки отправки сообщений риелтором, нужно связать Realtor с User.
        
        # Создание сообщения
        Message.objects.create(
            chat=chat,
            content=content,
            is_realtor_sender=is_realtor_sender # False для покупателя
        )
    
    # Перенаправляем обратно в комнату чата
    return redirect('chat:room', chat_id=chat.id)