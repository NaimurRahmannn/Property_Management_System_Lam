from django.core.management.base import BaseCommand

from property_app.embeddings import get_model, build_location_text
from property_app.models import Location


class Command(BaseCommand):
    help = "Generate and store semantic embeddings for locations using all-MiniLM-L6-v2."

    def add_arguments(self, parser):
        parser.add_argument(
            "--all",
            action="store_true",
            help="Re-generate embeddings for every location, not just those missing one.",
        )

    def handle(self, *args, **options):
        regenerate_all = options["all"]

        queryset = Location.objects.all()
        if not regenerate_all:
            queryset = queryset.filter(embedding__isnull=True)

        locations = list(queryset)
        if not locations:
            self.stdout.write(self.style.SUCCESS(
                "No locations need embeddings. Use --all to regenerate."
            ))
            return

        self.stdout.write("Loading model all-MiniLM-L6-v2 …")
        model = get_model()

        texts = [build_location_text(loc) for loc in locations]
        self.stdout.write(f"Encoding {len(texts)} locations …")
        vectors = model.encode(texts, show_progress_bar=False)

        for loc, vec in zip(locations, vectors):
            loc.embedding = vec.tolist()
            loc.save(update_fields=["embedding"])

        self.stdout.write(self.style.SUCCESS(
            f"Generated embeddings for {len(locations)} locations."
        ))