from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.forms.widgets import ClearableFileInput

from .models import Listing, ListingPhoto, Neighborhood, PriceRange, HomeType


# ---------- Inline for existing photos ---------- #

class ListingPhotoInline(admin.TabularInline):
    model = ListingPhoto
    extra = 0
    fields = ("preview", "image", "caption", "sort_order")
    readonly_fields = ("preview",)

    def preview(self, obj):
        if not obj or not obj.image:
            return ""
        return format_html(
            '<img src="{}" style="height:70px;border-radius:6px;">', obj.image.url
        )


# ---------- Widget that supports multiple file selection ---------- #

class MultiFileInput(ClearableFileInput):
    """File input that supports selecting multiple files in one field."""
    allow_multiple_selected = True

    def value_from_datadict(self, data, files, name):
        # We don't really use this cleaned value, but this keeps Django happy
        if hasattr(files, "getlist"):
            return files.getlist(name)
        file = files.get(name)
        if file is None:
            return []
        return [file]


# ---------- Custom form with multi-photo upload ---------- #

class ListingAdminForm(forms.ModelForm):
    # Not a model field: just for uploading multiple images at once
    new_photos = forms.CharField(
        required=False,
        widget=MultiFileInput(attrs={"multiple": True}),
        label="Add photos",
        help_text=(
            "You can select multiple image files here; "
            "they will be added as listing photos when you save."
        ),
    )

    class Meta:
        model = Listing
        fields = "__all__"


# ---------- Listing admin ---------- #

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    form = ListingAdminForm
    inlines = [ListingPhotoInline]

    list_display = (
        "__str__",
        "status",
        "visibility",
        "is_featured",
        "price",
        "beds",
        "baths",
        "created_at",
    )
    list_filter = (
        "status",
        "visibility",
        "is_featured",
        "city",
        "state",
        "home_type",
        "neighborhood",
    )
    search_fields = ("street", "city", "zipcode", "description")
    autocomplete_fields = ("neighborhood", "price_range", "home_type")
    fieldsets = (
        ("Basics", {"fields": ("status", "visibility", "is_featured", "description")}),
        ("Address", {"fields": ("street", "city", "state", "zipcode")}),
        (
            "Attributes",
            {
                "fields": (
                    "sqft",
                    "beds",
                    "baths",
                    "price",
                    "year_built",
                    "garage_spaces",
                    "lot_size_sqft",
                    "hoa_fee",
                )
            },
        ),
        (
            "Relations",
            {
                "fields": (
                    "home_type",
                    "neighborhood",
                    "price_range",
                    "created_by",
                )
            },
        ),
        ("Photos (upload new)", {"fields": ("new_photos",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
    readonly_fields = ("created_at", "updated_at")

    def save_model(self, request, obj, form, change):
        # set created_by once
        if not obj.created_by:
            obj.created_by = request.user

        # first save the Listing (so it has a PK)
        super().save_model(request, obj, form, change)

        # THEN create ListingPhoto objects for any newly uploaded files
        files = request.FILES.getlist("new_photos")
        if files:
            existing_count = obj.photos.count()
            for i, f in enumerate(files):
                ListingPhoto.objects.create(
                    listing=obj,
                    image=f,
                    sort_order=existing_count + i,
                )


# ---------- Other admin models ---------- #

@admin.register(Neighborhood)
class NeighborhoodAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(HomeType)
class HomeTypeAdmin(admin.ModelAdmin):
    search_fields = ("type_name",)


@admin.register(PriceRange)
class PriceRangeAdmin(admin.ModelAdmin):
    list_display = ("min_price", "max_price")
    ordering = ("min_price",)
    search_fields = ("min_price", "max_price")
