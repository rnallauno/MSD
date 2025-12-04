from django import forms
from .models import HomeType, PriceRange, Neighborhood

class ContactForm(forms.Form):
    name = forms.CharField(
        label="Name",
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Your full name"}),
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "you@example.com"}),
    )
    phone = forms.CharField(
        label="Phone (optional)",
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "555-123-4567"}),
    )
    message = forms.CharField(
        label="Message",
        widget=forms.Textarea(attrs={"rows": 4, "placeholder": "How can we help?"}),
    )
class ListingSearchForm(forms.Form):
    home_type = forms.ModelChoiceField(
        queryset=HomeType.objects.all().order_by("type_name"),
        required=False,
        empty_label="Any home type",
        widget=forms.Select(attrs={"class": "ls-input"})
    )
    price_range = forms.ModelChoiceField(
        queryset=PriceRange.objects.all().order_by("min_price"),
        required=False,
        empty_label="Any price range",
        widget=forms.Select(attrs={"class": "ls-input"})
    )
    neighborhood = forms.ModelChoiceField(
        queryset=Neighborhood.objects.all().order_by("name"),
        required=False,
        empty_label="Any neighborhood",
        widget=forms.Select(attrs={"class": "ls-input"})
    )