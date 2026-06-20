from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from pgvector.django import VectorField, HnswIndex


class Location(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)

    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    point = models.PointField(geography=True, srid=4326, null=True, blank=True)

    boundary = models.MultiPolygonField(srid=4326, null=True, blank=True)

    embedding = VectorField(dimensions=1536, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            HnswIndex(
                name="location_embedding_idx",
                fields=["embedding"],
                m=16,
                ef_construction=64,
                opclasses=["vector_cosine_ops"],
            ),
        ]

    def save(self, *args, **kwargs):
        if self.latitude is not None and self.longitude is not None:
            self.point = Point(float(self.longitude), float(self.latitude), srid=4326)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name},{self.city},{self.country}"


class Property(models.Model):
    class PropertyType(models.TextChoices):
        APARTMENT = "apartment", "Apartment"
        HOUSE = "house", "House"
        VILLA = "villa", "Villa"
        CONDO = "condo", "Condo"
        STUDIO = "studio", "Studio"
        CABIN = "cabin", "Cabin"

    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        BOOKED = "booked", "Booked"
        UNAVAILABLE = "unavailable", "Unavailable"

    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name="properties"
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    property_type = models.CharField(
        max_length=50, choices=PropertyType.choices
    )
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    status = models.CharField(
        max_length=50, choices=Status.choices, default=Status.AVAILABLE
    )
    price = models.DecimalField(max_digits=14, decimal_places=2)
    point = models.PointField(geography=True, srid=4326, null=True, blank=True)
    embedding = VectorField(dimensions=1536, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural="Properties"
        indexes = [
            HnswIndex(
                name="property_embedding_idx",
                fields=["embedding"],
                m=16,
                ef_construction=64,
                opclasses=["vector_cosine_ops"],
            ),
        ]
    def save(self, *args, **kwargs):
        if self.latitude is not None and self.longitude is not None:
            self.point = Point(float(self.longitude), float(self.latitude), srid=4326)
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.title},{self.status},{self.price}"
    
class PropertyImage(models.Model):
    property=models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name="images"
    )
    image=models.ImageField(upload_to="properties/%y/%m")
    alt_text=models.CharField(max_length=255,blank=True)
    created_at=models.DateField(auto_now_add=True)

    class Meta:
        ordering=["created_at"]

    def __str__(self):
        return f"{self.property.title}"
