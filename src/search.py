import re
from rank_bm25 import BM25Okapi
from src.indexer import DocumentIndexer


def tokenize(text):
    return re.findall(r"\b[a-zA-Z0-9_]+\b", text.lower())


class SearchEngine:

    def __init__(self, chunks, collection_name="technical_documents"):
        self.chunks = chunks

        documents = [chunk.content for chunk in chunks]
        tokenized_documents = [tokenize(doc) for doc in documents]
        self.bm25 = BM25Okapi(tokenized_documents)

        self.indexer = DocumentIndexer(
            collection_name=collection_name
        )
        self.indexer.add_chunks(chunks)

    def search_bm25(self, query, top_k=5):
        query_tokens = tokenize(query)
        scores = self.bm25.get_scores(query_tokens)

        ranked = sorted(
            enumerate(scores),
            key=lambda item: item[1],
            reverse=True
        )

        results = []

        for index, score in ranked[:top_k]:
            chunk = self.chunks[index]

            results.append({
                "chunk_id": chunk.chunk_id,
                "content": chunk.content,
                "score": float(score),
                "method": "BM25"
            })

        return results

    def search_dense(self, query, top_k=5):
        if self.indexer.collection.count() == 0:
            return []

        response = self.indexer.search(query, top_k)
        results = []

        for i, chunk_id in enumerate(response["ids"][0]):
            results.append({
                "chunk_id": chunk_id,
                "content": response["documents"][0][i],
                "score": float(response["distances"][0][i]),
                "method": "Dense"
            })

        return results
