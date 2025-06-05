# MAP Calculation in Retrieval Benchmarking

This document summarizes our findings about Mean Average Precision (MAP) calculation in the context of retrieval benchmarking, particularly when using SentenceTransformer's evaluator.

## Key Findings

1. **Different Ranking Methods**:
   - The SentenceTransformer evaluator uses its own tensor-based cosine similarity to rank documents
   - ChromaDB may use a different ranking method, leading to inconsistencies when comparing metrics

2. **MAP Calculation in SentenceTransformer Evaluator**:
   - For each query, Average Precision (AP) is calculated as:
     `AP = (sum of precision@i for each relevant doc i found) / min(k, total number of relevant docs)`
   - The overall MAP is the simple macro-average (mean) of per-query AP values:
     `MAP = sum(AP_i) / number_of_queries`

3. **Key Insights**:
   - The evaluator normalizes AP by `min(k, len(relevant_docs))`, not by `len(relevant_docs)`
   - It uses a simple macro-average, not a weighted average that considers the number of relevant docs
   - The tensor-based similarity calculation may produce different rankings than vector stores like ChromaDB

## Issues Resolved

1. **Discrepancy between evaluator and our MAP calculation**:
   - We updated our implementation to match the evaluator by:
     - Using the exact same tensor-based similarity calculation
     - Normalizing AP by `min(k, len(relevant_docs))`
     - Computing a simple macro-average of per-query AP values

2. **Inconsistency between summary and per-query metrics**:
   - We fixed the inconsistency by:
     - Using the evaluator's ranking method for both summary and per-query metrics
     - Ensuring all metrics are calculated on the same document rankings

## Implementation Details

### Exact Evaluator MAP Implementation

Our `exact_evaluator_map.py` implementation follows these steps:

1. Encode queries and corpus documents using the specified model
2. Calculate cosine similarity using `util.pytorch_cos_sim` (same as evaluator)
3. For each query:
   - Rank documents by similarity score
   - Calculate AP using the evaluator's formula
   - Normalize by `min(k, len(relevant_docs))`
4. Calculate MAP as the mean of per-query AP values

### Per-Query Analysis Fix

We updated the `analyze_per_query_performance` function to:

1. Use the same tensor-based ranking as the evaluator
2. Calculate metrics based on these rankings
3. Match the evaluator's normalization method for AP

## Lessons Learned

1. When benchmarking retrieval systems, be aware of differences in ranking methods between:
   - The evaluation framework (e.g., SentenceTransformer evaluator)
   - The production system (e.g., ChromaDB)

2. Document and standardize the MAP calculation method:
   - How AP is normalized (by total relevant docs or min(k, total relevant docs))
   - How MAP is averaged (macro-average or weighted average)

3. Ensure consistency in metrics throughout your benchmarking:
   - Use the same ranking method for all metrics
   - Document any differences between evaluation and production rankings
