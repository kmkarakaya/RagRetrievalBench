"""
Shared helpers for the re-analysis workstream (reviewer-driven revision).

Design rules (do NOT violate):
- This package is read-only with respect to the frozen snapshot. It only opens
  and queries the already-persisted ChromaDB collections; it NEVER initializes,
  creates, or deletes a collection (that path re-embeds and would destroy the
  frozen index because config.reinitialize_collections is True).
- All new artifacts are written under datasets/<name>/analysis/, never into the
  frozen datasets/<name>/reports/ (that dir is scanned by the paper tooling via a
  "latest raw_results_*.json" glob and must stay untouched).

Per-query metric formulas below reproduce the semantics of
sentence_transformers.evaluation.InformationRetrievalEvaluator for binary
relevance at a single cutoff k, so that mean(per-query) == the published
dataset-level aggregate (verified by the consistency gate in query_level_eval).
"""
import os
import sys
import json
import re

# Ensure repo root is importable so `import config` and `from utils...` resolve
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import config as cfg  # noqa: E402

# The metric, label and IO helpers below now live in the pipeline, in
# utils/bootstrap_utils.py, and are re-exported here so the snapshot scripts in this
# folder keep working without duplicating the implementations.
from utils.bootstrap_utils import (  # noqa: E402,F401
    METRICS,
    analysis_dir,
    label_for,
    per_query_metrics,
    read_jsonl,
    write_jsonl,
)

SEED = 42

# Datasets in the frozen snapshot
DATASETS = ["education_eng", "education_tr", "law_tr"]

# Canonical M1..M5 ordering, captured from config before any dataset prefixing.
# configure_for_dataset() only prefixes collection_name; model_name/order are stable.
MODEL_NAMES = [m["model_name"] for m in cfg.embedding_models]


def rng(seed=SEED):
    import numpy as np
    return np.random.default_rng(seed)


def open_collection(client, name):
    """Open an EXISTING collection. Raises if missing; never creates one."""
    return client.get_collection(name)


def load_expected_means(dataset):
    """Parse the frozen raw_results_*.json for a dataset -> {model_name: {metric: mean}}.

    Uses config.get_latest_raw_results so we read exactly what the paper reports.
    """
    path = cfg.get_latest_raw_results(dataset)
    if path is None:
        raise FileNotFoundError(f"No frozen raw_results for {dataset}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return path, {name: blob["metrics"] for name, blob in data["models"].items()}


_ST_CACHE = {}


def get_st_model(model_name):
    """Load (and cache) a SentenceTransformer. Deterministic CPU encoding."""
    from sentence_transformers import SentenceTransformer
    if model_name not in _ST_CACHE:
        _ST_CACHE[model_name] = SentenceTransformer(model_name)
    return _ST_CACHE[model_name]


def embed_texts(model, texts, batch_size=32):
    """Encode texts with default (non-normalized) settings, matching how the
    frozen pipeline's ChromaDB SentenceTransformerEmbeddingFunction embedded
    corpus and queries. Returns a float32 (N, d) array."""
    import numpy as np
    vecs = model.encode(list(texts), convert_to_numpy=True,
                        batch_size=batch_size, show_progress_bar=False)
    return np.asarray(vecs, dtype=np.float32)


def knn_rank(corpus_emb, corpus_ids, q_vec, topn=100):
    """Exact squared-L2 nearest neighbours (ChromaDB default space is L2).

    Ranking is invariant to the monotonic similarity=1/(1+d) transform the
    pipeline applies, so ordering by ascending squared-L2 reproduces it.
    """
    import numpy as np
    d = ((corpus_emb - q_vec) ** 2).sum(axis=1)
    order = np.argsort(d, kind="stable")[:topn]
    return [corpus_ids[j] for j in order], [float(d[j]) for j in order]


def parse_relevance_score(text):
    """Parse the LLM judge JSON {"relevance": 0|1}; return 0 on any failure.
    Copied verbatim from rag_benchmark.parse_relevance_score for label parity."""
    if not text:
        return 0
    try:
        m = re.search(r"({[\s\S]*?})", text)
        j = json.loads(m.group(1)) if m else json.loads(text)
        s = int(j.get("relevance", 0))
        return s if s > 0 else 0
    except Exception:
        return 0


def extract_response_text(batch_result):
    """Extract generated text from a Gemini Batch API result item.
    Copied verbatim from rag_benchmark.extract_response_text."""
    try:
        response = batch_result.get("response", {})
        candidates = response.get("candidates", [])
        if not candidates:
            candidates = response.get("body", {}).get("candidates", [])
        if candidates:
            return candidates[0].get("content", {}).get("parts", [])[0].get("text", "")
    except Exception:
        pass
    return ""


def judge_with_retry(system_prompt, user_prompt, max_retries=5, base_delay=2.0):
    """Synchronous LLM judge with exponential backoff.

    Fallback for the Batch API path in pooled_qrels; utils.llm.generate_content
    has no retry of its own, which is unsafe for a multi-thousand-call job.
    """
    import time
    from utils.llm import generate_content
    last = None
    for attempt in range(max_retries):
        try:
            return generate_content(system_prompt, user_prompt)
        except Exception as e:  # noqa: BLE001
            last = e
            if attempt == max_retries - 1:
                break
            time.sleep(base_delay * (2 ** attempt))
    raise RuntimeError(f"judge_with_retry exhausted retries: {last}")
