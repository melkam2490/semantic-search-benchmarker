
from src.benchmarker import (
    calculate_hit_rate,
    calculate_reciprocal_rank
)


def test_hit_rate_when_result_is_found():
    results = [
        {"content": "Authentication uses a token."},
        {"content": "Database uses PostgreSQL."}
    ]

    score = calculate_hit_rate(
        results, ["Authentication"], k=5
    )

    assert score == 1.0


def test_hit_rate_when_result_is_missing():
    results = [
        {"content": "Database uses PostgreSQL."}
    ]

    score = calculate_hit_rate(
        results, ["Authentication"], k=5
    )

    assert score == 0.0


def test_reciprocal_rank():
    results = [
        {"content": "Database uses PostgreSQL."},
        {"content": "Authentication uses a token."}
    ]

    score = calculate_reciprocal_rank(
        results, ["Authentication"], k=5
    )

    assert score == 0.5


def test_reciprocal_rank_when_result_is_missing():
    results = [
        {"content": "Database uses PostgreSQL."}
    ]

    score = calculate_reciprocal_rank(
        results, ["Authentication"], k=5
    )

    assert score == 0.0
