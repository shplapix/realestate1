from django import forms
from .models import Listing

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        exclude = ('realtor', 'list_date', 'is_published')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
