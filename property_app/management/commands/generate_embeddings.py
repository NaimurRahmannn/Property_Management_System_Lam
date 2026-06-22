from django.core.management.base import BaseCommand

from property_app.models import Property


def build_property_text(prop):
    parts = [
        prop.title,
        prop.description or "",
        f"{prop.get_property_type_display()} in {prop.location.name}",
    ]
    return ". ".join(p for p in parts if p).strip()


class Command(BaseCommand):
    help = "Generate and store semantic embeddings for properties using all-MiniLM-L6-v2."

    def add_arguments(self, parser):
        parser.add_argument(
            "--all",
            action="store_true",
            help="Re-generate embeddings for every property, not just those missing one.",
        )

    def handle(self, *args, **options):
        from sentence_transformers import SentenceTransformer

        regenerate_all = options["all"]

        queryset = Property.objects.select_related("location")
        if not regenerate_all:
            queryset = queryset.filter(embedding__isnull=True)

        properties = list(queryset)
        if not properties:
            self.stdout.write(self.style.SUCCESS(
                "No properties need embeddings. Use --all to regenerate."
            ))
            return

        self.stdout.write(f"Loading model all-MiniLM-L6-v2 …")
        model = SentenceTransformer("all-MiniLM-L6-v2")

        texts = [build_property_text(p) for p in properties]
        self.stdout.write(f"Encoding {len(texts)} properties …")
        vectors = model.encode(texts, show_progress_bar=False)

        for prop, vec in zip(properties, vectors):
            prop.embedding = vec.tolist()
            prop.save(update_fields=["embedding"])

        self.stdout.write(self.style.SUCCESS(
            f"Generated embeddings for {len(properties)} properties."
        ))