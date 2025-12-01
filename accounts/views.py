from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.models import User
from realtors.models import Realtor

def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        # role could be 'buyer' or 'realtor'
        role = request.POST.get('role', 'buyer')

        # Validation
        if password != confirm_password:
            messages.error(request, 'Паролі не співпадають')
            return redirect('register')
        
        if User.objects.filter(email=email).exists():
            # "почта уже используется,перейти к входу?(и ссылку на окно входа в слово "вход")"
            # We can use HTML in messages if safe, or just text. 
            # Django messages usually escape HTML. We might need to handle this in template or use mark_safe.
            # For now, I will put the text.
            messages.error(request, 'Пошта вже використовується, перейти до <a href="/accounts/login">входу</a>?')
            return redirect('register')
        
        if User.objects.filter(username=email).exists():
             messages.error(request, 'Користувач з таким email вже існує')
             return redirect('register')

        # Create User
        # We use email as username or just set username to email
        user = User.objects.create_user(username=email, email=email, password=password, first_name=first_name, last_name=last_name)
        user.save()

        if role == 'realtor':
            # Create Realtor object
            # We need to fill required fields. 
            # Realtor model: name, photo, description, phone, email, is_mvp, hire_date
            # We can set defaults.
            Realtor.objects.create(
                user=user,
                name=f"{first_name} {last_name}",
                email=email,
                phone="", # User can update later
                description="",
                photo="photos/default.jpg" # Placeholder
            )

        messages.success(request, 'Ви успішно зареєструвалися. Тепер ви можете увійти.')
        return redirect('login')

    else:
        return render(request, 'accounts/register.html')

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(username=email, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Невірні облікові дані')
            return redirect('login')
    else:
        return render(request, 'accounts/login.html')

def logout(request):
    auth.logout(request)
    return redirect('index')

from chat.models import Chat

def dashboard(request):
    user = request.user
    chats = []
    listings = []
    purchased_listings = []
    sold_listings = []
    reviews = []

    if hasattr(user, 'realtor'):
        # User is a realtor
        chats = Chat.objects.filter(realtor=user.realtor)
        from listings.models import Listing, Review
        listings = Listing.objects.filter(realtor=user.realtor, is_published=True).order_by('-list_date')
        sold_listings = Listing.objects.filter(realtor=user.realtor, is_sold=True).order_by('-sold_date')
        reviews = Review.objects.filter(seller=user.realtor).order_by('-created_at')
    else:
        # User is a buyer
        chats = Chat.objects.filter(user=user)
        from listings.models import Listing
        purchased_listings = Listing.objects.filter(buyer=user).order_by('-sold_date')
        # Check for reviews
        for listing in purchased_listings:
            try:
                listing.user_review = listing.review
            except:
                listing.user_review = None
        
    # Get favorite listings for all users
    favorite_listings = user.favorite_listings.all()
        
    context = {
        'chats': chats,
        'listings': listings,
        'purchased_listings': purchased_listings,
        'sold_listings': sold_listings,
        'reviews': reviews,
        'favorite_listings': favorite_listings
    }
    return render(request, 'accounts/dashboard.html', context)
