from django.db.models import Q
from django.shortcuts import render
from django.http import JsonResponse
from .models import Property,Location
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import LocationAutocompleteSerializer

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
    q = request.GET.get("q", "")
    slug = request.GET.get("slug", "")
    return render(request, "property_app/search.html", {"q": q, "slug": slug})

