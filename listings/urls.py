from django.urls import path
from. import views

app_name = 'listings' # Добавляем пространство имен
urlpatterns = [
    # /listings/
    path('', views.listings, name='listings'), 
    
    # /listings/1/ , /listings/2/ и т.д.
    path('<int:listing_id>/', views.listing, name='listing'),
]