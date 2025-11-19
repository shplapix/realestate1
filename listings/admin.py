from django.contrib import admin
from.models import Listing

# Расширенная настройка для модели Listing
class ListingAdmin(admin.ModelAdmin):
    # Поля, отображаемые в списке 
    list_display = ('id', 'title', 'is_published', 'price', 'list_date', 'realtor')
    
    # Поля, которые являются ссылками на страницу редактирования
    list_display_links = ('id', 'title')
    
    # Фильтры в боковой панели
    list_filter = ('realtor', 'state', 'city')
    
    # Поля, которые можно редактировать прямо из списка
    list_editable = ('is_published',)
    
    # Поля, по которым будет работать поиск
    search_fields = ('title', 'description', 'address', 'city', 'state', 'zipcode')
    
    list_per_page = 25

# Регистрируем Listing с кастомными настройками ListingAdmin
admin.site.register(Listing, ListingAdmin)