"""
Utility / helper functions.

Shared utility functions used across the application
for common tasks like text processing, file handling, etc.
"""


def clean_text(text: str) -> str:
    """
    Clean and normalize raw text extracted from documents.
    Future: Implement whitespace normalization, special char removal, etc.
    """
    return text.strip()


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """
    Split a large text into overlapping chunks for embedding.
    Future: Implement sliding-window chunking with configurable size/overlap.
    """
    pass