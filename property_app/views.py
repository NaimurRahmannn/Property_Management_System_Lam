from django.shortcuts import render

from .models import Property


def home(request):
    featured = (
        Property.objects.filter(is_active=True)
        .select_related("location")
        .prefetch_related("images")
        .order_by("-created_at")[:6]
    )
    return render(request, "property_app/home.html", {"featured": featured})
