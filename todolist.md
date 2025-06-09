1. Suggestions to Improve Embedding Model Comparison
    - Per-Query Analysis
    - Add More Comprehensive Testing
    - Add Model Size/Parameters Report
    - Latency Measurements
    - Visualizations in Report
    - Better Statistical Testing
    - Improved Error Handling and Logging
2. Automated Query & Qrels Generation Sub-Flows with Gemini
   - **A. Seed-Chunk → Query → Retrieval → Label**
     1. Randomly sample `cfg.n_queries` chunks as seed inputs.
     2. Prompt Gemini to generate a user-style question answered exactly by each seed.
     3. Retrieve top-`cfg.candidate_pool_size` chunks via ChromaDB.
     4. Prompt Gemini to label which of those candidates are relevant.
     5. Save outputs to [queries.jsonl](http://_vscodecontentref_/1) and [qrels.tsv](http://_vscodecontentref_/2).
   - **B. Cluster-by-Topic → End-to-End Question & Qrels**
     1. Cluster chunk embeddings (e.g., KMeans) into topic groups.
     2. Provide representative chunks per cluster to Gemini to craft a composite question.
     3. Ask Gemini to list all chunk IDs in that cluster that fully answer the question.
   - **C. Manual Seed + LLM Auto-Expand**
     1. Manually author a small seed set of queries and relevance judgments.
     2. Few-shot prompt or fine-tune Gemini on the seed examples.
     3. Use the tuned LLM to auto-label relevant chunks for new queries across the corpus.
   - Summary
    1. (seed→retrieve→label) is easiest to keep “comprehensive” qrels.
    . (cluster→one-shot) scales to very large corpora but needs good clustering.
    3. (few manual → auto-expand) yields highest fidelity but needs seed curation.
    Choose based on your corpus size, API budget, and required qrels quality.
