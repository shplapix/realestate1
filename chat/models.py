# chat/models.py

from django.db import models
from django.contrib.auth import get_user_model
from realtors.models import Realtor
from listings.models import Listing

User = get_user_model()

class Chat(models.Model):
    """
    Модель чата, связывающая одного Пользователя (Покупателя) с одним Риелтором.
    """
    # Пользователь, который инициировал чат (покупатель)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats_as_user')
    
    # Риелтор, с которым ведется чат
    realtor = models.ForeignKey(Realtor, on_delete=models.CASCADE, related_name='chats_as_realtor')
    
    # Объект, по которому идет обсуждение (необязательно, но полезно для контекста)
    listing = models.ForeignKey(Listing, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Гарантируем, что между одним Пользователем и одним Риелтором 
        # может быть только один активный чат по одному объекту.
        unique_together = ('user', 'realtor', 'listing') 
        # Если не привязывать к объекту, то unique_together = ('user', 'realtor')

    def __str__(self):
        return f"Чат {self.user.username} с {self.realtor.name}"

class Message(models.Model):
    """
    Модель отдельного сообщения.
    """
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    
    # Отправитель: может быть как User (покупатель), так и Realtor
    # В реальной системе это должно быть расширено (например, через GenericForeignKey)
    # Для простоты, оставим это поле для текста.
    # В реальной реализации вам нужно будет отслеживать отправителя. 
    # Предположим, что sender_id - это id пользователя (User) или риелтора (Realtor)
    
    # Для простоты пока используем булево поле для определения отправителя
    # True = Отправил Риелтор, False = Отправил Покупатель
    is_realtor_sender = models.BooleanField(default=False) 
    
    is_read = models.BooleanField(default=False)

    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('timestamp',)