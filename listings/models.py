from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class Neighborhood(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class HomeType(models.Model):
    type_name = models.CharField(max_length=40, unique=True)

    class Meta:
        verbose_name = "Home Type"
        verbose_name_plural = "Home Types"
        ordering = ["type_name"]

    def __str__(self):
        return self.type_name


class PriceRange(models.Model):
    min_price = models.IntegerField()
    max_price = models.IntegerField()

    class Meta:
        ordering = ["min_price"]

    def __str__(self):
        return f"${self.min_price:,.0f} – ${self.max_price:,.0f}"


class Listing(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("pending", "Pending"),
        ("sold", "Sold"),
        ("off_market", "Off Market"),
    ]
    VISIBILITY_CHOICES = [
        ("Y", "Visible"),
        ("N", "Hidden"),
    ]

    # core
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    visibility = models.CharField(max_length=1, choices=VISIBILITY_CHOICES, default="Y")
    is_featured = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    # address
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)  # e.g. NE
    zipcode = models.CharField(max_length=10)

    # attributes
    sqft = models.PositiveIntegerField(null=True, blank=True)
    beds = models.DecimalField(
        max_digits=2, decimal_places=0, null=True, blank=True
    )  # up to 99
    baths = models.DecimalField(
        max_digits=3, decimal_places=1, null=True, blank=True
    )  # e.g., 2.5
    price = models.IntegerField()
    year_built = models.PositiveIntegerField(null=True, blank=True)
    garage_spaces = models.PositiveIntegerField(null=True, blank=True)
    lot_size_sqft = models.PositiveIntegerField(null=True, blank=True)
    hoa_fee = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    # relationships
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="listings_created",
    )
    neighborhood = models.ForeignKey(
        Neighborhood, on_delete=models.SET_NULL, null=True, blank=True
    )
    price_range = models.ForeignKey(
        PriceRange, on_delete=models.SET_NULL, null=True, blank=True
    )
    home_type = models.ForeignKey(
        HomeType, on_delete=models.SET_NULL, null=True, blank=True
    )

    # timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.street}, {self.city}, {self.state} {self.zipcode}"

    # --- photos helpers ---
    def main_photo(self):
        p = self.photos.order_by("sort_order", "id").first()
        return p.image.url if p else ""

    @property
    def main_photo_url(self):
        return self.main_photo()

    # --- URL for public detail page ---
    def get_absolute_url(self):
        return reverse("public_listing_detail", args=[self.pk])

    # --- ensure only one listing is featured at a time ---
    def save(self, *args, **kwargs):
        super_result = super().save(*args, **kwargs)
        if self.is_featured:
            Listing.objects.exclude(pk=self.pk).update(is_featured=False)
        return super_result


def listing_upload_path(instance, filename):
    # photos stored under listing_photos/<listing_id>/<filename>
    return f"listing_photos/{instance.listing_id}/{filename}"


class ListingPhoto(models.Model):
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="photos"
    )
    image = models.ImageField(upload_to=listing_upload_path)
    caption = models.CharField(max_length=255, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    mime_type = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ["sort_order", "id"]

    def save(self, *args, **kwargs):
        if self.image and not self.mime_type:
            f = getattr(self.image, "file", None)
            self.mime_type = getattr(f, "content_type", "") if f else ""
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Photo {self.id} for {self.listing}"
