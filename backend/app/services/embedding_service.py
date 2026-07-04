"""
Embedding generation service.

Handles conversion of text chunks into vector embeddings
using Sentence Transformers or similar models.
"""


class EmbeddingService:
    """
    Generates vector embeddings for text chunks.
    Future: Load embedding model, implement embed() method.
    """

    def __init__(self):
        pass

    def embed_text(self, text: str) -> list[float]:
        """
        Convert a single text string into a vector embedding.
        Future: Call the embedding model and return the vector.
        """
        pass

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Convert a batch of text strings into vector embeddings.
        Future: Batch-encode texts for efficiency.
        """
        pass