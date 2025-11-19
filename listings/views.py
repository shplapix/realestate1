from django.shortcuts import render, get_object_or_404
from.models import Listing
from django.core.paginator import Paginator # Для пагинации

# Страница со всеми объявлениями
def listings(request):
    listings_list = Listing.objects.order_by('-list_date').filter(is_published=True)
    
    # Пагинация: 6 объявлений на страницу
    paginator = Paginator(listings_list, 6)
    page = request.GET.get('page')
    paged_listings = paginator.get_page(page)
    
    context = {
        'listings': paged_listings
    }
    return render(request, 'listings/listings.html', context)

# Страница одного объявления
def listing(request, listing_id):
    # get_object_or_404 - лучший способ получить объект или вернуть ошибку 404
    listing_obj = get_object_or_404(Listing, pk=listing_id) 
    
    context = {
        'listing': listing_obj
    }
    # Рендерим шаблон 'listing_detail.html'
    return render(request, 'listings/listing_detail.html', context)