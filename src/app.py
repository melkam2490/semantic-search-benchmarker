
import json
from pathlib import Path

import streamlit as st

from src.chunking import FixedSizeChunker, StructureAwareChunker
from src.search import SearchEngine
from src.benchmarker import run_benchmark


st.set_page_config(
    page_title="SearchWorkbench",
    page_icon="🔎",
    layout="wide"
)

st.title("🔎 SearchWorkbench")
st.write(
    "Compare keyword search, semantic search, "
    "and two-stage retrieval."
)


@st.cache_resource
def build_engines():
    document_path = Path("corpus/api_spec_sample.md")
    text = document_path.read_text(encoding="utf-8")

    with open("data/eval_queries.json", encoding="utf-8") as file:
        queries = json.load(file)

    fixed_256 = FixedSizeChunker(256, 40).split(
        text, "api-document"
    )

    fixed_1024 = FixedSizeChunker(1024, 100).split(
        text, "api-document"
    )

    structured = StructureAwareChunker().split(
        text, "api-document"
    )

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


st.info("Preparing your search engines. Please wait.")

try:
    engines, queries = build_engines()

    st.success("Your search engines are ready!")

    # --------------------------------
    # 1. Search documents
    # --------------------------------

    st.header("1. Search documents")

    question = st.text_input(
        "Enter a technical question:",
        placeholder="How does API authentication work?"
    )

    k = st.slider("Number of results", 1, 10, 5)

    if st.button("Search"):
        if question.strip():

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

                results = engines[
                    "Dense Structure-Aware"
                ].search_dense(question, k)

                for result in results:
                    st.markdown(
                        f"**{result['chunk_id']}** "
                        f"(Cosine distance: {result['score']:.4f})"
                    )
                    st.write(result["content"])
                    st.divider()

        else:
            st.warning("Please enter a question.")

    st.divider()

    # --------------------------------
    # 2. Two-Stage Search Pipeline
    # --------------------------------

    st.header("2. Two-Stage Search Pipeline")

    st.write(
        "Stage 1 retrieves 25 candidate documents. "
        "Stage 2 uses a cross-encoder to rank the best 5."
    )

    if st.button("Run Two-Stage Search"):

        if question.strip():

            pipeline = engines["Dense Structure-Aware"]

            with st.spinner(
                "Retrieving and reranking documents..."
            ):
                output = pipeline.search_and_rerank(
                    question,
                    candidate_k=25,
                    top_k=5
                )

            results = output["results"]
            use_web = output["use_web"]

            st.subheader("Pipeline Results")

            st.write(
                "**Original question:** "
                + output.get("original_query", question)
            )

            st.write(
                "**Rewritten question:** "
                + output.get("rewritten_query", question)
            )

            # Web fallback
            if use_web:

                st.warning(
                    "Low confidence. Searching the web "
                    "for additional information."
                )

                web_results = output.get("web_results", [])

                if web_results:

                    st.subheader("Web Search Results")

                    for item in web_results:

                        st.markdown(f"### {item['title']}")
                        st.write(item["snippet"])

                        if item["url"]:
                            st.markdown(
                                f"[Open source]({item['url']})"
                            )

                        st.caption(
                            f"Source: {item['source']}"
                        )

                        st.divider()

                else:
                    st.info(
                        "No web results were returned. "
                        "Please try again."
                    )

            else:

                st.success(
                    "Internal documents passed the confidence check."
                )

            # Internal search results
            if results:

                st.subheader("Internal Document Results")

                for index, result in enumerate(results, start=1):

                    st.markdown(
                        f"**Rank {index}: {result['chunk_id']}**"
                    )

                    st.write(result["content"])

                    st.write(
                        f"Reranker score: "
                        f"{result['rerank_score']:.4f}"
                    )

                    st.write(
                        f"Confidence: "
                        f"{result['confidence']:.4f}"
                    )

                    st.progress(
                        min(
                            max(result["confidence"], 0.0),
                            1.0
                        )
                    )

                    st.divider()

            else:

                st.info("No internal documents were found.")

            with st.expander("How the pipeline works"):

                st.write(
                    "1. Query rewriting prepares the question."
                )

                st.write(
                    "2. Stage 1: Dense retrieval finds up to "
                    "25 candidate documents."
                )

                st.write(
                    "3. Stage 2: Cross-encoder reranks the candidates."
                )

                st.write(
                    "4. The top 5 internal results are displayed."
                )

                st.write(
                    "5. Confidence below 0.55 triggers web fallback."
                )

    st.divider()

    # --------------------------------
    # 3. Retrieval Benchmark
    # --------------------------------

    st.header("3. Retrieval Benchmark")

    st.write(
        "The benchmark system evaluates retrieval quality."
    )

    st.write(
        "Hit Rate at K measures whether at least one relevant "
        "result appears in the top K results."
    )

    st.write(
        "Mean Reciprocal Rank measures the position of "
        "the first relevant result."
    )

    st.write(
        "Average latency measures the time required to "
        "complete a search."
    )

    if st.button("Run Benchmark"):

        benchmark_results = []

        with st.spinner("Running benchmark..."):

            for name, engine in engines.items():

                method = (
                    "bm25"
                    if name == "BM25 Baseline"
                    else "dense"
                )

                metrics = run_benchmark(
                    engine,
                    queries,
                    method=method,
                    k=5
                )

                benchmark_results.append({
                    "Configuration": name,
                    "Hit Rate@5": metrics["hit_rate"],
                    "MRR@5": metrics["mrr"],
                    "Average Latency (ms)": (
                        metrics["average_latency_ms"]
                    )
                })

        st.subheader("Benchmark Results")

        st.dataframe(
            benchmark_results,
            width="stretch"
        )

        st.subheader("MRR Comparison")

        st.bar_chart({
            item["Configuration"]: item["MRR@5"]
            for item in benchmark_results
        })

except Exception as error:

    st.error(f"Something went wrong: {error}")

    st.info(
        "Please send me the error so we can fix it."
    )


st.caption(
    "SearchWorkbench - Technical Document Retrieval Benchmark"
)
