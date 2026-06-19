from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin

from .models import Location

@admin.register(Location)
class LocationAdmin(GISModelAdmin):
    list_display = ("name", "city", "country", "is_active", "created_at")
    list_filter = ("country", "is_active")
    search_fields = ("name", "city", "country")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")
    exclude = ("embedding",)