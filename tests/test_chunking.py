
from src.chunking import FixedSizeChunker, StructureAwareChunker


def test_fixed_chunks_have_overlap():
    text = " ".join(["python"] * 700)

    chunker = FixedSizeChunker(chunk_size=100, overlap=20)
    chunks = chunker.split(text)

    assert len(chunks) > 1

    assert chunks[1].metadata["start_token"] == (
        chunks[0].metadata["end_token"] - 20
    )


def test_structure_chunker_preserves_code_fence():
    text = """# API Guide

## Authentication

Use a token to authenticate.

```python
def login():
    return True
```

## Database

Use PostgreSQL.
"""

    chunks = StructureAwareChunker().split(text)

    authentication_chunk = next(
        chunk for chunk in chunks
        if "Authentication" in chunk.content
    )

    assert "```python" in authentication_chunk.content
    assert "def login():" in authentication_chunk.content
    assert "```" in authentication_chunk.content


def test_structure_chunker_finds_headings():
    text = """# Guide

## Authentication
Use a token.

## Database
Use PostgreSQL.
"""

    chunks = StructureAwareChunker().split(text)

    headings = [chunk.metadata["heading"] for chunk in chunks]

    assert "Guide" in headings
    assert "Guide > Authentication" in headings
    assert "Guide > Database" in headings
