from django.db import models
from datetime import datetime
from realtors.models import Realtor
from django.contrib.auth.models import User

class Listing(models.Model):
    realtor = models.ForeignKey(Realtor, on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    price = models.IntegerField()
    bedrooms = models.IntegerField()
    bathrooms = models.DecimalField(max_digits=2, decimal_places=1)
    garage = models.IntegerField(default=0)
    sqft = models.IntegerField()
    lot_size = models.DecimalField(max_digits=5, decimal_places=1)
    
    photo_main = models.ImageField(upload_to='photos/%Y/%m/%d/')
    photo_1 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_2 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    
    is_published = models.BooleanField(default=True)
    list_date = models.DateTimeField(default=datetime.now, blank=True)
    
    # Purchase fields
    buyer = models.ForeignKey(User, related_name='purchased_listings', on_delete=models.DO_NOTHING, null=True, blank=True)
    is_sold = models.BooleanField(default=False)
    sold_date = models.DateTimeField(null=True, blank=True)

    # Favorites
    favorites = models.ManyToManyField(User, related_name='favorite_listings', blank=True)

    def __str__(self):
        return self.title

class Review(models.Model):
    listing = models.OneToOneField(Listing, on_delete=models.CASCADE)
    seller = models.ForeignKey(Realtor, on_delete=models.CASCADE, related_name='reviews')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    rating = models.IntegerField(default=5)
    text = models.TextField()
    created_at = models.DateTimeField(default=datetime.now, blank=True)

    def __str__(self):
        return f"Review for {self.listing.title} by {self.buyer.username}"