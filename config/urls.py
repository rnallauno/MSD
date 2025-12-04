from listings.views import (
    public_home,
    public_listings,
    public_listing_detail,
    public_contact,
    omaha_info,
    omaha_info_detail,
)
from accounts.views import admin_login_redirect
from django.views.generic import TemplateView, RedirectView
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", public_home, name="public_home"),

    path("about/", TemplateView.as_view(
        template_name="site/about.html"), name="public_about"),

    # LISTINGS
    path("listings/", public_listings, name="public_listings"),
    path("listings/<int:pk>/", public_listing_detail, name="public_listing_detail"),

    # IMPORTANT: use the view, not TemplateView, so we get the form + email
    path("contact/", public_contact, name="public_contact"),

    # admin stuff
    path("admin/", RedirectView.as_view(url="/dashboard/")),
    path("dashboard/login/", admin_login_redirect, name="admin-login-override"),
    path("dashboard/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("omaha-info/", omaha_info, name="public_omaha_info"),
    path(
        "omaha-info/<int:pk>/",
        omaha_info_detail,
        name="omaha_info_detail",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
