from rest_framework import serializers

from .models import Location


class LocationAutocompleteSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source="name")

    class Meta:
        model = Location
        fields = ["label", "slug"]