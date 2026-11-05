
from sentence_transformers import CrossEncoder
import math


class DocumentReranker:

    def __init__(self):
        self.model = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2"
        )

    def rerank(self, query, documents, top_k=5):
        if not documents:
            return []

        pairs = [
            (query, document["content"])
            for document in documents
        ]

        scores = self.model.predict(pairs)

        results = []

        for document, score in zip(documents, scores):
            result = document.copy()

            # Convert raw score into confidence
            confidence = 1 / (1 + math.exp(-float(score)))

            result["rerank_score"] = float(score)
            result["confidence"] = confidence

            results.append(result)

        results.sort(
            key=lambda item: item["rerank_score"],
            reverse=True
        )

        return results[:top_k]

    def should_use_web(self, results, threshold=0.55):
        if not results:
            return True

        best_confidence = max(
            item["confidence"] for item in results
        )

        return best_confidence < threshold
