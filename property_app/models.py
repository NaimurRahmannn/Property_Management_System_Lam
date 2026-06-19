from django.contrib.gis.db import models

from pgvector.django import VectorField, HnswIndex


class Location(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)

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

    def __str__(self):
        return f"{self.name},{self.city},{self.country}"


# Create your models here.
