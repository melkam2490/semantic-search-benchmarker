# SearchWorkbench

## Semantic Document Search Engine & Empirical Retrieval Benchmarking

### Project Overview

SearchWorkbench is a technical document search engine that compares keyword search with semantic search.

The project uses BM25 for keyword retrieval and Sentence Transformers with ChromaDB for dense vector search.

### Technologies

- Python 3.13
- Streamlit
- ChromaDB
- Sentence Transformers
- all-MiniLM-L6-v2
- rank-bm25
- Pydantic
- tiktoken
- pytest

### Chunking Methods

1. Fixed-size chunks of 256 tokens.
2. Fixed-size chunks of 1024 tokens.
3. Structure-aware Markdown chunks.

### Search Methods

**BM25:** Finds documents using matching keywords.

**Dense Search:** Finds documents using semantic similarity and vector embeddings.

### Benchmark Results

| Configuration         | Hit Rate@5 |  MRR@5 |
| --------------------- | ---------: | -----: |
| BM25 Baseline         |     1.0000 | 0.9222 |
| Dense 256             |     1.0000 | 0.8556 |
| Dense 1024            |     1.0000 | 1.0000 |
| Dense Structure-Aware |     1.0000 | 0.9111 |

All results were measured using the project's current evaluation questions and section-name matching method.

### Testing

Run the tests:

```bash
python -m pytest -v
```

Result: 9 tests passed.

### Run the Application

```bash
python -m streamlit run src/app.py
```

### Project Limitations

The current demonstration uses a small sample API document rather than a full 20–30-page technical corpus. The evaluation uses section-name matching rather than manually verified source spans. These limitations should be considered when interpreting the benchmark results.

### Conclusion

The experiment demonstrates how keyword and semantic search can retrieve technical information. Dense 1024 achieved the highest MRR in this sample evaluation, while BM25 also performed well on exact keyword searches.
