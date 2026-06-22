
# shared embeding helper for property semantic search
_model = None

def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def embed_text(text):
    model = get_model()
    return model.encode(text).tolist()

def build_location_text(location):
    parts = [location.name, location.city, location.country]
    return ", ".join(p for p in parts if p).strip()