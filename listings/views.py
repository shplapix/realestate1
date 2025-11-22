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
    # Рендерим шаблон 'listing_detail.html'
    return render(request, 'listings/listing_detail.html', context)

from .forms import ListingForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect

@login_required
def create_listing(request):
    if not hasattr(request.user, 'realtor'):
        messages.error(request, 'Только риелторы могут добавлять объявления')
        return redirect('dashboard')

    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.realtor = request.user.realtor
            listing.save()
            messages.success(request, 'Объявление успешно добавлено!')
            return redirect('dashboard')
    else:
        form = ListingForm()

    context = {
        'form': form
    }
    return render(request, 'listings/create_listing.html', context)