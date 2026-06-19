from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin

from .models import Location,Property

@admin.register(Location)
class LocationAdmin(GISModelAdmin):
    list_display = ("name", "city", "country", "is_active", "created_at")
    list_filter = ("country", "is_active")
    search_fields = ("name", "city", "country")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")
    exclude = ("embedding",)

@admin.register(Property)
class PropertyAdmin(GISModelAdmin):
    list_display=(
        "title",
        "location",
        "property_type",
        "status",
        "price",
        "is_active"
    )
    list_filter=("property_type","status","is_active")
    search_fields=("title","description")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    list_select_related=("location",)
    exclude=("embedding",)

