from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render

from .forms import ContactForm
from .models import Listing, ListingPhoto, OmahaInfo
from .forms import ListingSearchForm
from django.db.models import Q
from .models import Listing, SearchLog, HomeType, PriceRange, Neighborhood

def public_home(request):
    featured = (
        Listing.objects
        .filter(is_featured=True, status="active", visibility="Y")
        .order_by("-updated_at")
        .first()
    )

    latest_listings = (
        Listing.objects
        .filter(status="active", visibility="Y")
        .order_by("-created_at")[:4]
    )

    search_form = ListingSearchForm()  # empty form for the hero / home page

    context = {
        "featured": featured,
        "latest_listings": latest_listings,
        "search_form": search_form,
        "has_filters": False,
    }
    return render(request, "site/home.html", context)

def _get_client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def public_listings(request):
    qs = Listing.objects.filter(status="active", visibility="Y")

    # Bind form to GET data so it keeps selections on reload
    form = ListingSearchForm(request.GET or None)

    # Defaults for logging
    q = ""
    home_type = price_range = neighborhood = None

    if form.is_valid():
        q = (form.cleaned_data.get("q") or "").strip()
        home_type = form.cleaned_data.get("home_type")
        price_range = form.cleaned_data.get("price_range")
        neighborhood = form.cleaned_data.get("neighborhood")

        if q:
            qs = qs.filter(
                Q(street__icontains=q)
                | Q(city__icontains=q)
                | Q(description__icontains=q)
            )

        if home_type:
            qs = qs.filter(home_type=home_type)

        if price_range:
            qs = qs.filter(price_range=price_range)

        if neighborhood:
            qs = qs.filter(neighborhood=neighborhood)

    listings = qs.order_by("-created_at")

    # Log searches only when something was actually filtered
    if any([q, home_type, price_range, neighborhood]):
        SearchLog.objects.create(
            query=q,
            home_type=home_type,
            price_range=price_range,
            neighborhood=neighborhood,
            results_count=listings.count(),
            ip_address=_get_client_ip(request),
            user=request.user if request.user.is_authenticated else None,
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:255],
        )

    return render(
        request,
        "site/listings.html",
        {
            "listings": listings,
            "search_form": form,   # <-- same name as home page
        },
    )


# listings/views.py
def public_listing_detail(request, pk):
    listing = get_object_or_404(
        Listing.objects.select_related("neighborhood", "home_type", "price_range"),
        pk=pk,
        visibility="Y",
    )
    photos = listing.photos.all().order_by("sort_order", "id")

    sent = False

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            subject = f"[Listing inquiry] {listing.street}, {listing.city}"
            message_lines = [
                f"Listing: {listing} (ID {listing.pk})",
                f"URL: {request.build_absolute_uri()}",
                "",
                f"Name:  {cd.get('name')}",
                f"Email: {cd.get('email')}",
                f"Phone: {cd.get('phone') or '—'}",
                "",
                "Message:",
                cd.get("message", ""),
            ]
            message = "\n".join(message_lines)

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
            )

            sent = True
            form = ContactForm()  # reset form after send
    else:
        form = ContactForm()

    context = {
        "listing": listing,
        "photos": photos,
        "form": form,
        "sent": sent,
    }
    return render(request, "listings/detail.html", context)
def public_contact(request):
    sent = False

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            subject = f"AdVance Home contact form – {cd['name']}"
            body = (
                f"Name: {cd['name']}\n"
                f"Email: {cd['email']}\n"
                f"Phone: {cd.get('phone', '')}\n\n"
                f"Message:\n{cd['message']}"
            )

            # Where the email goes (your Gmail)
            to_email = getattr(
                settings,
                "CONTACT_FORM_RECIPIENT_EMAIL",
                settings.DEFAULT_FROM_EMAIL,
            )

            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,  # from
                [to_email],                   # to list
            )

            sent = True
            form = ContactForm()  # reset the form after sending
    else:
        form = ContactForm()

    return render(request, "site/contact.html", {"form": form, "sent": sent})

def omaha_info(request):
    items = (
        OmahaInfo.objects
        .filter(is_visible=True)
        .order_by("sort_order", "title")
    )
    return render(request, "site/omaha_info.html", {"items": items})


def omaha_info_detail(request, pk):
    item = get_object_or_404(OmahaInfo, pk=pk, is_visible=True)
    return render(request, "site/omaha_info_detail.html", {"item": item})