from django.shortcuts import render, get_object_or_404
from .models import Listing


def public_home(request):
    # Featured listing – latest active & visible one
    featured = (
        Listing.objects
        .filter(is_featured=True, status="active", visibility="Y")
        .order_by("-updated_at")
        .first()
    )

    # Latest 6 visible listings
    latest_listings = (
        Listing.objects
        .filter(status="active", visibility="Y")
        .order_by("-created_at")[:6]
    )

    return render(request, "site/home.html", {
        "featured": featured,
        "latest_listings": latest_listings,
    })


def public_listings(request):
    listings = (
        Listing.objects
        .filter(status="active", visibility="Y")
        .order_by("-created_at")
    )
    return render(request, "site/listings.html", {"listings": listings})


# listings/views.py
def public_listing_detail(request, pk):
    listing = get_object_or_404(
        Listing.objects.select_related("neighborhood", "home_type", "price_range"),
        pk=pk,
        visibility="Y",
    )
    photos = listing.photos.all()
    return render(request, "listings/detail.html", {"listing": listing, "photos": photos})

