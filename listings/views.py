from django.shortcuts import render, get_object_or_404, redirect
from .models import Listing, Review
from django.core.paginator import Paginator
from .forms import ListingForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime
from chat.models import Chat, Message

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
        messages.error(request, 'Тільки рієлтори можуть додавати оголошення')
        return redirect('dashboard')

    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.realtor = request.user.realtor
            listing.save()
            messages.success(request, 'Оголошення успішно додано!')
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
        messages.success(request, 'Оголошення видалено з обраного')
    else:
        listing.favorites.add(request.user)
        messages.success(request, 'Оголошення додано до обраного')
    return redirect(request.META.get('HTTP_REFERER', 'listings:listings'))

@login_required
def purchase(request, listing_id):
    if request.method == 'POST':
        listing = get_object_or_404(Listing, pk=listing_id)
        
        # Check if already sold
        if listing.is_sold:
            messages.error(request, 'Цей об\'єкт вже продано!')
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
        # Note: Message model might need adjustment if it doesn't support system messages well, 
        # but we'll use is_realtor_sender=False and a specific format.
        Message.objects.create(
            chat=chat,
            is_realtor_sender=False, 
            content=f"SYSTEM: Ваш товар '{listing.title}' был куплен. Средства в размере ${listing.price} поступили на ваш аккаунт.",
            is_read=False
        )
        
        messages.success(request, 'Операція пройшла успішно')
        return redirect('dashboard')
        
    return redirect('listings:listings')

@login_required
def add_review(request, listing_id):
    if request.method == 'POST':
        listing = get_object_or_404(Listing, pk=listing_id)
        
        # Check if user is the buyer
        if listing.buyer != request.user:
            messages.error(request, 'Ви не можете залишити відгук на цей об\'єкт')
            return redirect('dashboard')
            
        rating = request.POST.get('rating')
        text = request.POST.get('text')
        
        Review.objects.create(
            listing=listing,
            seller=listing.realtor,
            buyer=request.user,
            rating=rating,
            text=text
        )
        
        messages.success(request, 'Відгук додано')
        return redirect('dashboard')
    return redirect('dashboard')

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    
    if review.buyer != request.user:
        messages.error(request, 'Ви не можете редагувати цей відгук')
        return redirect('dashboard')
        
    if request.method == 'POST':
        rating = request.POST.get('rating')
        text = request.POST.get('text')
        
        review.rating = rating
        review.text = text
        review.save()
        
        messages.success(request, 'Відгук оновлено')
        return redirect('dashboard')
        
    return redirect('dashboard')