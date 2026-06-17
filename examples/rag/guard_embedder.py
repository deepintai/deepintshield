"""Pre-embedding input screening: check text for PII / injection / toxicity
*before* it is vectorised. Complements guard_retriever (which filters the
results). Raises on a blocking verdict instead of embedding the text."""
from deepintshield import DeepintShield, DeepintShieldBlockedError


shield = DeepintShield.from_env()

# Route embeddings through the gateway, then screen input before embedding.
embedder = shield.langgraph().embedder("text-embedding-3-small")
embedder = shield.rag.guard_embedder(embedder)

try:
    vec = embedder.embed_query("My SSN is 123-45-6789")
    print("embedded, dims:", len(vec))
except DeepintShieldBlockedError as exc:
    print(f"blocked before embedding: {exc.reason}")
