# chat/urls.py

from django.urls import path
from . import views

app_name = 'chat' # Пространство имен для удобства

urlpatterns = [
    # Список всех чатов пользователя
    path('', views.chat_index, name='index'), 
    
    # Создание или переход в чат с риелтором по объекту
    path('start/<int:realtor_id>/<int:listing_id>/', views.start_chat, name='start_chat'), 
    path('send/<int:chat_id>/', views.send_message, name='send_message'),
    # Конкретный чат по ID
    path('room/<int:chat_id>/', views.chat_room, name='room'), 
]