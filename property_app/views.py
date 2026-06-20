from django.db.models import Q
from django.shortcuts import render
from django.http import JsonResponse
from .models import Property,Location
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import LocationAutocompleteSerializer
from django.core.paginator import Paginator
def home(request):
    featured = (
        Property.objects.filter(is_active=True)
        .select_related("location")
        .prefetch_related("images")
        .order_by("-created_at")[:6]
    )
    return render(request, "property_app/home.html", {"featured": featured})

@api_view(["GET"])
def location_autocomplete(request):
    q = request.GET.get("q", "").strip()
    results = []
    if q:
        matches = Location.objects.filter(
            Q(name__icontains=q)
            | Q(city__icontains=q)
            | Q(country__icontains=q),
            is_active=True,
        ).order_by("name")[:10]
        results = LocationAutocompleteSerializer(matches, many=True).data
    return Response({"results": results})

def property_search(request):
    slug = request.GET.get("slug", "").strip()
    q = request.GET.get("q", "").strip()

    location = None
    properties = Property.objects.none()

    if slug:
        location = Location.objects.filter(slug=slug, is_active=True).first()
    elif q:
        location = (
            Location.objects.filter(
                Q(name__icontains=q)
                | Q(city__icontains=q)
                | Q(country__icontains=q),
                is_active=True,
            )
            .order_by("name")
            .first()
        )

    if location:
        properties = (
            Property.objects.filter(location=location, is_active=True)
            .select_related("location")
            .prefetch_related("images")
            .order_by("-created_at")
        )

    paginator = Paginator(properties, 6)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "location": location,
        "query": q,
        "page_obj": page_obj,
        "total": paginator.count,
    }
    return render(request, "property_app/search.html", context)

