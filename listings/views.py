from django.shortcuts import render, get_object_or_404, redirect
from .models import Listing
from django.core.paginator import Paginator
from .forms import ListingForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Страница со всеми объявлениями
def listings(request):
    listings_list = Listing.objects.order_by('-list_date').filter(is_published=True)
    
    # Favorites logic
    if request.user.is_authenticated:
        # Annotate with is_favorite
        for listing in listings_list:
            listing.is_favorite = listing.favorites.filter(id=request.user.id).exists()
        
        # Sort: Favorites first
        listings_list = sorted(listings_list, key=lambda x: x.is_favorite, reverse=True)
    
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
    listing_obj = get_object_or_404(Listing, pk=listing_id) 
    
    context = {
        'listing': listing_obj
    }
    return render(request, 'listings/listing_detail.html', context)

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

@login_required
def toggle_favorite(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    if listing.favorites.filter(id=request.user.id).exists():
        listing.favorites.remove(request.user)
        messages.success(request, 'Объявление удалено из избранного')
    else:
        listing.favorites.add(request.user)
        messages.success(request, 'Объявление добавлено в избранное')
    return redirect(request.META.get('HTTP_REFERER', 'listings:listings'))

from datetime import datetime
from chat.models import Chat, Message

@login_required
def purchase_listing(request, listing_id):
    if request.method == 'POST':
        listing = get_object_or_404(Listing, pk=listing_id)
        
        # Check if already sold
        if listing.is_sold:
            messages.error(request, 'Этот объект уже продан!')
            return redirect('listings:listing', listing_id=listing.id)

        # Mark as sold
        listing.is_sold = True
        listing.buyer = request.user
        listing.sold_date = datetime.now()
        listing.is_published = False # Hide from main listings
        listing.save()
        
        # Create/Get Chat and Send Notification to Realtor
        # We need to find or create a chat between Buyer (request.user) and Realtor (listing.realtor)
        
        chat, created = Chat.objects.get_or_create(
            user=request.user,
            realtor=listing.realtor,
            listing=listing
        )
        
        # Create System Message
        Message.objects.create(
            chat=chat,
            is_realtor_sender=False, # System message
            content=f"SYSTEM: Ваш товар '{listing.title}' был куплен. Средства в размере ${listing.price} поступили на ваш аккаунт.",
            is_read=False
        )
        
        messages.success(request, 'Оплата прошла успешно!')
        return redirect('dashboard')
        
    return redirect('listings:listings')

from datetime import datetime
from chat.models import Chat, Message

@login_required
def purchase_listing(request, listing_id):
    if request.method == 'POST':
        listing = get_object_or_404(Listing, pk=listing_id)
        
        # Check if already sold
        if listing.is_sold:
            messages.error(request, 'Этот объект уже продан!')
            return redirect('listings:listing', listing_id=listing.id)

        # Mark as sold
        listing.is_sold = True
        listing.buyer = request.user
        listing.sold_date = datetime.now()
        listing.is_published = False # Hide from main listings
        listing.save()
        
        # Create/Get Chat and Send Notification to Realtor
        realtor_user = listing.realtor.user # Assuming Realtor model has OneToOneField to User called 'user'
        # Wait, Realtor model in realtors/models.py usually has 'user' field? 
        # Let's check realtors/models.py if needed, but assuming standard structure.
        # Actually, let's check if Realtor has a user field.
        # Based on previous context, Realtor has a user field.
        
        # We need to find or create a chat between Buyer (request.user) and Realtor (listing.realtor)
        # The Chat model uses 'realtor' field which is a Realtor instance.
        
        chat, created = Chat.objects.get_or_create(
            user=request.user,
            realtor=listing.realtor,
            listing=listing
        )
        
        # Create System Message
        Message.objects.create(
            chat=chat,
            is_realtor_sender=False, # System message, but we can attribute to buyer or handle differently. 
            # Requirement: "from RealEstate" message to seller.
            # Let's say it's a message in the chat.
            content=f"SYSTEM: Ваш товар '{listing.title}' был куплен. Средства в размере ${listing.price} поступили на ваш аккаунт.",
            is_read=False
        )
        
        messages.success(request, 'Оплата прошла успешно!')
        return redirect('dashboard')
        
    return redirect('listings:listings')