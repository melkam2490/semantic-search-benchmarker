
import re

from rank_bm25 import BM25Okapi

from src.indexer import DocumentIndexer
from src.reranker import DocumentReranker
from src.rewriter import rewrite_query
from src.web_search import search_web
from src.security import is_prompt_injection


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

        self.reranker = None

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

    def search_and_rerank(self, query, candidate_k=25, top_k=5):

        # Step 1: Save the original question
        original_query = query

        # Step 2: Rewrite the question
        rewritten_query = rewrite_query(query)

        # Step 3: Retrieve candidate documents
        candidates = self.search_dense(
            rewritten_query,
            top_k=candidate_k
        )

        # Step 4: Remove documents containing common
        # prompt injection phrases
        candidates = [
            document for document in candidates
            if not is_prompt_injection(document["content"])
        ]

        # Step 5: Use web search if no documents remain
        if not candidates:
            return {
                "original_query": original_query,
                "rewritten_query": rewritten_query,
                "results": [],
                "use_web": True,
                "web_results": search_web(rewritten_query)
            }

        # Step 6: Load the reranker
        if self.reranker is None:
            self.reranker = DocumentReranker()

        # Step 7: Rerank the documents
        results = self.reranker.rerank(
            rewritten_query,
            candidates,
            top_k=top_k
        )

        # Step 8: Check confidence
        use_web = self.reranker.should_use_web(results)

        # Step 9: Search the web if confidence is low
        web_results = []

        if use_web:
            web_results = search_web(rewritten_query)

        # Step 10: Return all results
        return {
            "original_query": original_query,
            "rewritten_query": rewritten_query,
            "results": results,
            "use_web": use_web,
            "web_results": web_results
        }
