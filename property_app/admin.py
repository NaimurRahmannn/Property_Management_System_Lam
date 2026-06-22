from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from django.utils.html import format_html
from .models import Location,Property,PropertyImage

class PropertyImageInline(admin.TabularInline):
    model=PropertyImage
    extra=1
    fields=("thumbnail","image","alt_text")
    readonly_fields=("thumbnail",)
    def thumbnail(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" style="height:60px;border-radius:4px;" />',
                obj.image.url,
            )
        return "—"
    thumbnail.short_description = "Preview"
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
    search_fields=("title","description","amenities")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    list_select_related=("location",)
    inlines=[PropertyImageInline]
    exclude=("embedding",)

@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ("thumbnail", "property", "alt_text", "created_at")
    list_display_links = ("property",)
    readonly_fields = ("thumbnail", "created_at")
    search_fields = ("property__title", "alt_text")
 
    def thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:50px;border-radius:4px;" />',
                obj.image.url,
            )
        return "—"
    thumbnail.short_description = "Preview"

