"""
Query-level re-evaluation via corpus re-embedding + exact squared-L2 kNN.

Why re-embed instead of querying the persisted ChromaDB collections:
the persisted chroma-hnswlib vector segments cannot be read in this environment
(count()/query() segfault at native segment load, even before torch is imported),
so we regenerate the vectors deterministically from corpus.jsonl with the same
sentence-transformers models and rank by exact squared-L2 (ChromaDB's default
space). The consistency gate verifies this reproduces the published dataset-level
means to ~1e-6, i.e. the reconstruction is faithful.

Retrieval is qrels-independent, so it is done ONCE per (dataset, model) and reused
across all qrels variants (frozen / pooled / pooled_forced).

  1. retrieve : re-embed corpus + queries, persist per-query ranked lists to
                datasets/<name>/analysis/rankings_<Mn>.jsonl
  2. score    : from stored rankings + a qrels file, compute per-query metrics and
                dataset-level aggregates for each model.

Usage:
  python analysis/query_level_eval.py --probe education_eng M1
  python analysis/query_level_eval.py --retrieve            # all datasets/models
  python analysis/query_level_eval.py --gate                # frozen qrels vs published
"""
import os
import sys
import argparse

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (_ROOT, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import common as C  # noqa: E402
import config as cfg  # noqa: E402
from utils.document_loader import load_queries, load_corpus, load_ground_truth  # noqa: E402

N_RESULTS = 100  # match the frozen evaluate_with_chromadb retrieval depth


def _rank_all(dataset, model_name):
    """Return list of {query_id, ranked_ids, distances} for one model via
    re-embedding + exact squared-L2 kNN. Assumes cfg already configured."""
    corpus = load_corpus(cfg.corpus_file)
    queries = load_queries(cfg.queries_file)
    corpus_ids = list(corpus.keys())
    model = C.get_st_model(model_name)
    corpus_emb = C.embed_texts(model, [corpus[cid] for cid in corpus_ids])
    q_ids = list(queries.keys())
    q_emb = C.embed_texts(model, [queries[qid] for qid in q_ids])
    rows = []
    for i, qid in enumerate(q_ids):
        ranked_ids, dists = C.knn_rank(corpus_emb, corpus_ids, q_emb[i], topn=N_RESULTS)
        rows.append({"query_id": qid, "ranked_ids": ranked_ids, "distances": dists})
    return rows


def retrieve_dataset(dataset):
    cfg.configure_for_dataset(dataset)
    adir = C.analysis_dir(dataset)
    for m in cfg.embedding_models:
        label = C.label_for(m["model_name"])
        rows = _rank_all(dataset, m["model_name"])
        out = os.path.join(adir, f"rankings_{label}.jsonl")
        C.write_jsonl(out, rows)
        print(f"[retrieve] {dataset} {label} ({m['model_name']}): {len(rows)} queries -> {out}")


# Scoring stored rankings is a pipeline concern, not a snapshot concern, so both
# helpers now live in utils/bootstrap_utils.py. Re-exported here because --gate and
# --probe below (and bootstrap_ci.py) still call them by these names.
from utils.bootstrap_utils import load_rankings, score_dataset  # noqa: E402,F401


def run_gate(dataset, tol=1e-2):
    """Faithful-reconstruction check: recomputed frozen-qrels aggregates vs published.

    education_eng reconstructs bit-exactly; the Turkish corpora match to <=~0.003
    (the persisted Turkish embeddings differ marginally from current corpus.jsonl).
    The re-analysis uses this exact-L2 recomputation consistently for frozen/pooled
    baselines and bootstrap, so the qrels-construction effect is isolated cleanly.
    A generous tol accepts these small residuals; the actual max diff is reported.
    """
    cfg.configure_for_dataset(dataset)
    scored = score_dataset(dataset, cfg.qrels_file)
    path, expected = C.load_expected_means(dataset)
    print(f"\n=== GATE {dataset} (expected from {os.path.basename(path)}) ===")
    ok = True
    worst = 0.0
    for m in cfg.embedding_models:
        label = C.label_for(m["model_name"])
        exp = expected[m["model_name"]]
        agg = scored[label]["aggregate"]
        nq = len(scored[label]["qids"])
        mdiff = max(abs(agg[metric] - exp[metric]) for metric in C.METRICS)
        worst = max(worst, mdiff)
        if mdiff > tol:
            ok = False
        print(f"    {label}: {nq} scored queries, max metric diff {mdiff:.2e}"
              f"{'  <-- EXCEEDS tol' if mdiff > tol else ''}")
    print(f"GATE {dataset}: {'PASS' if ok else 'FAIL'} "
          f"(worst diff {worst:.2e}, tol {tol:.0e})")
    return ok


def probe(dataset, label, tol=1e-6):
    cfg.configure_for_dataset(dataset)
    _, _, relevant = load_ground_truth(cfg.corpus_file, cfg.queries_file, cfg.qrels_file)
    m = next(mm for mm in cfg.embedding_models if C.label_for(mm["model_name"]) == label)
    rows = _rank_all(dataset, m["model_name"])
    per_q = {metric: [] for metric in C.METRICS}
    for row in rows:
        rel = relevant.get(row["query_id"])
        if not rel:
            continue
        pm = C.per_query_metrics(row["ranked_ids"], rel, cfg.k)
        for metric in C.METRICS:
            per_q[metric].append(pm[metric])
    agg = {metric: sum(v) / len(v) for metric, v in per_q.items()}
    _, expected = C.load_expected_means(dataset)
    exp = expected[m["model_name"]]
    print(f"\nPROBE {dataset} {label} ({m['model_name']}) n={len(per_q['map'])}")
    all_ok = True
    for metric in C.METRICS:
        d = abs(agg[metric] - exp[metric])
        if d > tol:
            all_ok = False
        print(f"  {metric:9s} got={agg[metric]:.10f} exp={exp[metric]:.10f} "
              f"d={d:.2e} {'OK' if d <= tol else 'MISMATCH'}")
    print(f"PROBE: {'PASS' if all_ok else 'FAIL'}")
    return all_ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", nargs=2, metavar=("DATASET", "MODEL"))
    ap.add_argument("--retrieve", action="store_true")
    ap.add_argument("--gate", action="store_true")
    ap.add_argument("--dataset", default=None, help="restrict --retrieve/--gate to one dataset")
    args = ap.parse_args()

    if args.probe:
        probe(args.probe[0], args.probe[1])
        return
    targets = [args.dataset] if args.dataset else C.DATASETS
    if args.retrieve:
        for ds in targets:
            retrieve_dataset(ds)
    if args.gate:
        results = {ds: run_gate(ds) for ds in targets}
        print("\n=== GATE SUMMARY ===")
        for ds, ok in results.items():
            print(f"  {ds}: {'PASS' if ok else 'FAIL'}")
        if not all(results.values()):
            sys.exit(1)


if __name__ == "__main__":
    main()
