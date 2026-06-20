import os
from decimal import Decimal, InvalidOperation

import pandas as pd
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from property_app.models import Location, Property, PropertyImage


class Command(BaseCommand):
    help = "Import vacation rental properties from a CSV file using pandas."

    VALID_TYPES = {c.value for c in Property.PropertyType}
    VALID_STATUS = {c.value for c in Property.Status}

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_path",
            type=str,
            help="Path to the CSV file to import.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse and validate the file without writing to the database.",
        )
        parser.add_argument(
            "--skip-images",
            action="store_true",
            help="Import properties but do not attach images.",
        )
        parser.add_argument(
            "--images-dir",
            type=str,
            default=None,
            help=(
                "Folder containing the image files referenced in the CSV. "
                "Defaults to an 'images' subfolder next to the CSV."
            ),
        )

    def handle(self, *args, **options):
        csv_path = options["csv_path"]
        dry_run = options["dry_run"]
        skip_images = options["skip_images"]

        if options["images_dir"]:
            self.images_dir = options["images_dir"]
        else:
            self.images_dir = os.path.join(
                os.path.dirname(os.path.abspath(csv_path)),
                "images",
            )

        try:
            df = pd.read_csv(csv_path)
        except FileNotFoundError:
            raise CommandError(f"File not found: {csv_path}")
        except Exception as exc:
            raise CommandError(f"Could not read CSV: {exc}")

        required = {
            "title",
            "property_type",
            "status",
            "price",
            "prop_latitude",
            "prop_longitude",
            "location_name",
            "city",
            "country",
            "loc_latitude",
            "loc_longitude",
        }

        missing = required - set(df.columns)
        if missing:
            raise CommandError(f"CSV is missing required columns: {sorted(missing)}")

        created_locations = 0
        created_properties = 0
        created_images = 0
        skipped = 0

        location_cache = {}

        for i, row in df.iterrows():
            line = i + 2

            try:
                with transaction.atomic():
                    location, loc_created = self._get_or_create_location(
                        row,
                        location_cache,
                    )

                    if loc_created:
                        created_locations += 1

                    if dry_run:
                        self._clean_property_fields(row)
                        created_properties += 1
                        continue

                    prop = self._create_property(row, location)
                    created_properties += 1

                    if not skip_images:
                        created_images += self._attach_images(row, prop)

            except (ValueError, InvalidOperation) as exc:
                skipped += 1
                self.stderr.write(
                    self.style.WARNING(f"Row {line} skipped: {exc}")
                )

        verb = "Would import" if dry_run else "Imported"

        self.stdout.write(
            self.style.SUCCESS(
                f"{verb} {created_properties} properties "
                f"({created_locations} new locations created, "
                f"{created_images} images attached, {skipped} rows skipped)."
            )
        )

    def _get_or_create_location(self, row, cache):
        name = str(row["location_name"]).strip()

        if name in cache:
            return cache[name], False

        slug = slugify(name)

        defaults = {
            "name": name,
            "city": str(row["city"]).strip(),
            "country": str(row["country"]).strip(),
            "latitude": self._to_decimal(row["loc_latitude"], "loc_latitude"),
            "longitude": self._to_decimal(row["loc_longitude"], "loc_longitude"),
        }

        location, created = Location.objects.get_or_create(
            slug=slug,
            defaults=defaults,
        )

        cache[name] = location
        return location, created

    def _clean_property_fields(self, row):
        property_type = str(row["property_type"]).strip().lower()

        if property_type not in self.VALID_TYPES:
            raise ValueError(
                f"invalid property_type '{property_type}' "
                f"(allowed: {sorted(self.VALID_TYPES)})"
            )

        status = str(row["status"]).strip().lower()

        if status not in self.VALID_STATUS:
            raise ValueError(
                f"invalid status '{status}' "
                f"(allowed: {sorted(self.VALID_STATUS)})"
            )

        price = self._to_decimal(row["price"], "price")
        lat = self._to_decimal(row["prop_latitude"], "prop_latitude")
        lng = self._to_decimal(row["prop_longitude"], "prop_longitude")
        title = str(row["title"]).strip()

        if not title:
            raise ValueError("title is empty")

        return {
            "title": title,
            "property_type": property_type,
            "status": status,
            "price": price,
            "latitude": lat,
            "longitude": lng,
            "description": str(row.get("description", "") or "").strip(),
        }

    def _create_property(self, row, location):
        fields = self._clean_property_fields(row)

        base_slug = slugify(fields["title"])
        slug = base_slug
        n = 1

        while Property.objects.filter(slug=slug).exists():
            n += 1
            slug = f"{base_slug}-{n}"

        return Property.objects.create(
            location=location,
            slug=slug,
            **fields,
        )

    @staticmethod
    def _to_decimal(value, field_name):
        if value is None or (isinstance(value, float) and pd.isna(value)):
            raise ValueError(f"{field_name} is missing")

        try:
            return Decimal(str(value).strip())
        except (InvalidOperation, ValueError):
            raise ValueError(f"{field_name} is not a valid number: '{value}'")

    def _attach_images(self, row, prop):
        raw = row.get("image_files")

        if raw is None or (isinstance(raw, float) and pd.isna(raw)):
            return 0

        names = [name.strip() for name in str(raw).split(";") if name.strip()]
        count = 0

        for idx, name in enumerate(names):
            path = os.path.join(self.images_dir, name)

            if not os.path.isfile(path):
                self.stderr.write(
                    self.style.WARNING(
                        f"  image not found for '{prop.title}': {path}"
                    )
                )
                continue

            img = PropertyImage(
                property=prop,
                alt_text=prop.title if idx == 0 else "",
            )

            with open(path, "rb") as fh:
                img.image.save(name, File(fh), save=True)

            count += 1

        return count