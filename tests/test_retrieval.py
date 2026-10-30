
from rank_bm25 import BM25Okapi
from src.search import tokenize


def test_exact_identifier_ranks_first():
    documents = [
        "The application uses PostgreSQL for storage.",
        "The custom setting CUSTOM_CONFIG_FLAG_XYZ enables indexing.",
        "The API requires token authentication."
    ]

    tokenized_documents = [tokenize(doc) for doc in documents]
    bm25 = BM25Okapi(tokenized_documents)

    query = "CUSTOM_CONFIG_FLAG_XYZ"
    scores = bm25.get_scores(tokenize(query))

    best_document_index = max(
        range(len(scores)),
        key=lambda index: scores[index]
    )

    assert best_document_index == 1


def test_tokenizer_handles_uppercase_identifiers():
    result = tokenize("CUSTOM_CONFIG_FLAG_XYZ")

    assert result == ["custom_config_flag_xyz"]
