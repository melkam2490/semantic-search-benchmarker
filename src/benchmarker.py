import time


def calculate_hit_rate(results, relevant_sections, k=5):
    """Check whether at least one correct result is in the top K."""

    top_results = results[:k]

    for result in top_results:
        content = result["content"].lower()

        for section in relevant_sections:
            if section.lower() in content:
                return 1.0

    return 0.0


def calculate_reciprocal_rank(results, relevant_sections, k=5):
    """Give a higher score when the first correct result ranks higher."""

    for position, result in enumerate(results[:k], start=1):
        content = result["content"].lower()

        for section in relevant_sections:
            if section.lower() in content:
                return 1.0 / position

    # No correct result means zero
    return 0.0


def run_benchmark(search_engine, queries, method="bm25", k=5):
    """Measure search quality and average search time."""

    hit_scores = []
    reciprocal_ranks = []
    latencies = []

    for item in queries:
        query = item["query"]
        relevant_sections = item["relevant_sections"]

        start_time = time.perf_counter()

        if method == "bm25":
            results = search_engine.search_bm25(query, top_k=k)
        else:
            results = search_engine.search_dense(query, top_k=k)

        elapsed = time.perf_counter() - start_time

        latencies.append(elapsed)

        hit_scores.append(
            calculate_hit_rate(results, relevant_sections, k)
        )

        reciprocal_ranks.append(
            calculate_reciprocal_rank(results, relevant_sections, k)
        )

    total = len(queries)

    if total == 0:
        return {
            "hit_rate": 0.0,
            "mrr": 0.0,
            "average_latency_ms": 0.0
        }

    return {
        "hit_rate": sum(hit_scores) / total,
        "mrr": sum(reciprocal_ranks) / total,
        "average_latency_ms": (
            sum(latencies) / total
        ) * 1000
    }
