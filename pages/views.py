from django.shortcuts import render
from listings.models import Listing
from realtors.models import Realtor

# Главная страница
def index(request):
    # Получаем 3 последних опубликованных объявления
    listings = Listing.objects.order_by('-list_date').filter(is_published=True)[:3]
    context = {
        'listings': listings
    }
    # Рендерим шаблон 'index.html' с этими данными
    return render(request, 'pages/index.html', context)

# Страница "О нас"
def about(request):
    realtors = Realtor.objects.order_by('hire_date')
    mvp_realtors = Realtor.objects.filter(is_mvp=True)
    context = {
        'realtors': realtors,
        'mvp_realtors': mvp_realtors
    }
    return render(request, 'pages/about.html', context)