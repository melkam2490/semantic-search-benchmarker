import json
from pathlib import Path

import streamlit as st

from src.chunking import FixedSizeChunker, StructureAwareChunker
from src.search import SearchEngine
from src.benchmarker import run_benchmark


st.set_page_config(
    page_title="SearchWorkbench",
    page_icon="??",
    layout="wide"
)

st.title("?? SearchWorkbench")
st.write("Compare keyword search with semantic search.")


@st.cache_resource
def build_engines():
    # Load our technical document
    document_path = Path("corpus/api_spec_sample.md")
    text = document_path.read_text(encoding="utf-8")

    # Load our evaluation questions
    with open("data/eval_queries.json", encoding="utf-8") as file:
        queries = json.load(file)

    # Create three chunking strategies
    fixed_256 = FixedSizeChunker(256, 40).split(
        text, "api-document"
    )

    fixed_1024 = FixedSizeChunker(1024, 100).split(
        text, "api-document"
    )

    structured = StructureAwareChunker().split(
        text, "api-document"
    )

    # Create search engines with separate collections
    engines = {
        "BM25 Baseline": SearchEngine(
            structured, "bm25_baseline"
        ),
        "Dense 256": SearchEngine(
            fixed_256, "dense_256"
        ),
        "Dense 1024": SearchEngine(
            fixed_1024, "dense_1024"
        ),
        "Dense Structure-Aware": SearchEngine(
            structured, "dense_structure"
        )
    }

    return engines, queries


st.info(
    "The first load downloads the embedding model. "
    "Please wait while the search engines are prepared."
)

try:
    engines, queries = build_engines()
    st.success("Your search engines are ready!")

    st.header("Search documents")

    question = st.text_input(
        "Enter a technical question:",
        placeholder="How does API authentication work?"
    )

    k = st.slider("Number of results", 1, 10, 5)

    if st.button("Search") and question:
        left, right = st.columns(2)

        with left:
            st.subheader("BM25 Keyword Search")
            results = engines["BM25 Baseline"].search_bm25(
                question, k
            )

            for result in results:
                st.markdown(
                    f"**{result['chunk_id']}** "
                    f"(Score: {result['score']:.4f})"
                )
                st.write(result["content"])
                st.divider()

        with right:
            st.subheader("Dense Semantic Search")
            results = engines["Dense Structure-Aware"].search_dense(
                question, k
            )

            for result in results:
                st.markdown(
                    f"**{result['chunk_id']}** "
                    f"(Cosine distance: {result['score']:.4f})"
                )
                st.write(result["content"])
                st.divider()

    st.header("Retrieval Benchmark")

    if st.button("Run Benchmark"):
        benchmark_results = []

        for name, engine in engines.items():
            method = "bm25" if name == "BM25 Baseline" else "dense"

            metrics = run_benchmark(
                engine, queries, method=method, k=5
            )

            benchmark_results.append({
                "Configuration": name,
                "Hit Rate@5": metrics["hit_rate"],
                "MRR@5": metrics["mrr"],
                "Average Latency (ms)": metrics["average_latency_ms"]
            })

        st.dataframe(
            benchmark_results,
            width="stretch"
        )

        st.bar_chart(
            {
                item["Configuration"]: item["MRR@5"]
                for item in benchmark_results
            }
        )

except Exception as error:
    st.error(f"Something went wrong: {error}")
    st.info("Please send me the error so we can fix it.")


st.caption("SearchWorkbench - Technical Document Retrieval Benchmark")
