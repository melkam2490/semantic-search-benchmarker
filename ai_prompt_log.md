# AI Prompt and Code Audit Log

## 1. Initial AI Prompt

I asked AI to help build a production-style two-stage RAG search pipeline using Python.

The requested features included:

- Query rewriting
- Dense retrieval using ChromaDB
- Cross-Encoder reranking
- Confidence scoring using sigmoid
- A confidence threshold of 0.55
- DuckDuckGo web fallback
- Streamlit user interface
- Automated tests
- Prompt injection protection

## 2. Problems Found and Fixed

### Problem 1: Syntax Error in Search Pipeline

**Problem:**

The document-filtering code was accidentally placed inside the
`search_dense()` function call. This caused a Python SyntaxError.

**Fix:**

I moved the filtering logic after the document retrieval step.

The corrected code filters the retrieved documents before reranking.

**Verification:**

`python -m py_compile .\src\search.py` completed successfully.

### Problem 2: Prompt Injection Protection Was Not Connected

**Problem:**

The security detection functions existed, but retrieved documents
were not being checked by the search pipeline.

**Fix:**

I imported `is_prompt_injection` into `search.py` and added a filter
to remove documents containing known prompt injection phrases.

**Verification:**

I added security tests and ran the full test suite.

All 13 tests passed.

## 3. Additional Security Limitation

The current prompt injection detector uses a list of known phrases.
It is a basic defense, not complete protection against every attack.

A production system would need stronger security controls.

## 4. Final Test Results

Command:

`pytest -q`

Result:

13 passed.

## 5. Summary

I reviewed and tested the AI-assisted code instead of accepting it
without checking.

I corrected a syntax error, connected the security filter to the
search pipeline, and verified the project with automated tests.
