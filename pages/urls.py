from django.urls import path
from. import views

urlpatterns = [
    # Маршрут для главной страницы
    path('', views.index, name='index'), 
    # Маршрут для страницы "О нас"
    path('about/', views.about, name='about'),
]