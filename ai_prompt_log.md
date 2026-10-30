# AI Prompt Log and Human Audit

## Project: SearchWorkbench

### AI assistance

AI assistance was used to help create the document chunkers, BM25 keyword search, dense semantic search, benchmark calculations, and Streamlit dashboard.

The generated code was reviewed and tested during development.

## Human Audit: Problems Found

### Issue 1: Chunk IDs can change between chunking methods

**Problem:**

Fixed-size chunks and structure-aware chunks create different chunk IDs. Using chunk IDs as the only ground truth would make benchmark comparisons unreliable.

**Correction:**

The evaluation questions use meaningful section names, such as Authentication and Database Configuration, instead of relying only on chunk IDs.

**Before:**

```python
relevant_sections = ["api-document-fixed-1"]
```

**After:**

```python
relevant_sections = ["Authentication"]
```

### Issue 2: Cosine distance and cosine similarity

**Problem:**

ChromaDB returns cosine distance. A smaller distance means a closer match.

It would be incorrect to sort these results from highest to lowest.

**Correction:**

The search system keeps ChromaDB's returned ranking, where the closest result comes first.

**Before:**

```python
results.sort(
    key=lambda result: result["score"],
    reverse=True
)
```

**After:**

```python
# ChromaDB already returns the closest results first.
# Lower cosine distance means a better match.
return results
```

### Issue 3: BM25 tokenization

**Problem:**

The document text and search questions must use the same tokenization rules.

**Correction:**

The same tokenize() function is used for both documents and questions.

### Issue 4: Fixed-size chunking

**Problem:**

Fixed-size chunking can split Markdown headings or code examples between chunks.

**Correction:**

The project also includes structure-aware chunking, which divides documents by Markdown headings.

## Final Review

The project includes keyword search, semantic search, multiple chunking methods, benchmark calculations, and automated tests.

The benchmark results must be measured by running the application and tests. No benchmark scores are assumed or invented.
