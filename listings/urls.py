from django.urls import path
from . import views

app_name = 'listings' # Добавляем пространство имен
urlpatterns = [
    # /listings/
    path('', views.listings, name='listings'), 
    
    # /listings/1/ , /listings/2/ и т.д.
    path('<int:listing_id>/', views.listing, name='listing'),
    path('create/', views.create_listing, name='create'),
    path('favorite/<int:listing_id>/', views.toggle_favorite, name='favorite'),
    path('purchase/<int:listing_id>/', views.purchase, name='purchase'),
    path('add_review/<int:listing_id>/', views.add_review, name='add_review'),
    path('edit_review/<int:review_id>/', views.edit_review, name='edit_review'),
]