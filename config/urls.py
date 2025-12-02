from listings.views import public_home, public_listings, public_listing_detail
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

    path("omaha-info/", TemplateView.as_view(
        template_name="site/omaha_info.html"), name="public_omaha_info"),

    path("contact/", TemplateView.as_view(
        template_name="site/contact.html"), name="public_contact"),

    # admin stuff
    path("admin/", RedirectView.as_view(url="/dashboard/")),
    path("dashboard/login/", admin_login_redirect, name="admin-login-override"),
    path("dashboard/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
