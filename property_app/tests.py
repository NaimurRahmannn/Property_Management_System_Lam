from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from property_app.models import Location, Property

EMBED_DIM = 384


def make_location(name, slug, city, country, lat=10.0, lng=20.0, embedding=None):
    return Location.objects.create(
        name=name,
        slug=slug,
        city=city,
        country=country,
        latitude=Decimal(str(lat)),
        longitude=Decimal(str(lng)),
        embedding=embedding,
    )


def make_property(location, title, slug, price=100, embedding=None):
    return Property.objects.create(
        location=location,
        title=title,
        slug=slug,
        property_type=Property.PropertyType.VILLA,
        price=Decimal(str(price)),
        latitude=location.latitude,
        longitude=location.longitude,
        embedding=embedding,
    )


def unit_vector(index):
    vec = [0.0] * EMBED_DIM
    vec[index] = 1.0
    return vec


class PointSyncTests(TestCase):
    def test_point_is_synced_from_lat_lng_on_save(self):
        loc = make_location("Destin", "destin", "Destin", "USA", lat=30.39, lng=-86.49)
        self.assertIsNotNone(loc.point)
        self.assertAlmostEqual(loc.point.x, -86.49, places=2)
        self.assertAlmostEqual(loc.point.y, 30.39, places=2)


class PropertySearchViewTests(TestCase):
    def setUp(self):
        self.aspen = make_location("Aspen", "aspen", "Aspen", "USA")
        self.destin = make_location("Destin", "destin", "Destin", "USA")
        make_property(self.aspen, "Aspen Chalet", "aspen-chalet")
        make_property(self.destin, "Destin Villa", "destin-villa")

    def test_search_by_slug_returns_only_that_location(self):
        resp = self.client.get(reverse("property_app:search"), {"slug": "aspen"})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Aspen Chalet")
        self.assertNotContains(resp, "Destin Villa")

    def test_text_search_spans_all_matching_locations(self):
        resp = self.client.get(reverse("property_app:search"), {"q": "USA"})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Aspen Chalet")
        self.assertContains(resp, "Destin Villa")


class LocationAutocompleteSemanticTests(TestCase):
    def setUp(self):
        self.beach = make_location(
            "Beach Town", "beach-town", "Beach", "USA", embedding=unit_vector(0)
        )
        self.mountain = make_location(
            "Mountain City", "mountain-city", "Mountain", "USA", embedding=unit_vector(1)
        )

    def test_autocomplete_ranks_by_cosine_distance(self):
        with patch("property_app.views.embed_text", return_value=unit_vector(0)):
            resp = self.client.get(
                reverse("property_app:location_autocomplete"), {"q": "seaside"}
            )
        self.assertEqual(resp.status_code, 200)
        results = resp.json()["results"]
        self.assertEqual(results[0]["slug"], "beach-town")
        self.assertEqual(results[0]["label"], "Beach Town")

    def test_autocomplete_empty_query_returns_no_results(self):
        resp = self.client.get(reverse("property_app:location_autocomplete"), {"q": ""})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["results"], [])
