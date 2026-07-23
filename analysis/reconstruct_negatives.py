"""
Reconstruct the implicit NEGATIVE relevance judgments that the frozen pipeline
discarded (it stored positives only).

The frozen qrels were judged over M5's top-20 candidate pool per query. Every
judged (qid, docid) pair is recorded in the qrels-generation batch REQUEST file
(datasets/<name>/reports/batches/batch_req_qrels_gen_*.jsonl, keyed "qid|||docid").
A judged pair that is NOT a positive in qrels.tsv was labeled 0 -> an implicit
negative. This is zero-LLM-cost (reads frozen artifacts only) and:
  - provides explicit negatives for the error analysis / paper disclosure, and
  - gives the frozen M5 labels so pooled_qrels can avoid re-judging M5's pool.

Outputs (never into reports/): datasets/<name>/analysis/implicit_negatives.tsv
and datasets/<name>/analysis/qrels_reconstruction_summary.json.
"""
import os
import sys
import glob
import json

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (_ROOT, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import common as C  # noqa: E402


def _dataset_file(dataset, *parts):
    return os.path.join(C.REPO_ROOT, "datasets", dataset, *parts)


def source_chunk_id(qid):
    """q{n}_for_{Seed}_chunk{m} -> {Seed}_chunk{m} (the seed chunk of the query)."""
    return qid.split("_for_", 1)[1] if "_for_" in qid else None


def latest_qrels_batch(dataset):
    files = sorted(glob.glob(_dataset_file(dataset, "reports", "batches",
                                           "batch_req_qrels_gen_*.jsonl")))
    return files[-1] if files else None


def judged_pairs(dataset):
    """List of (qid, docid) the LLM judged in the frozen (M5-pool) qrels run."""
    path = latest_qrels_batch(dataset)
    if path is None:
        raise FileNotFoundError(f"No qrels batch request file for {dataset}")
    pairs = []
    for row in C.read_jsonl(path):
        qid, docid = row["key"].split("|||", 1)
        pairs.append((qid, docid))
    return path, pairs


def positives(dataset):
    """Set of (qid, docid) positives from the frozen qrels.tsv (incl. forced source)."""
    pos = set()
    with open(_dataset_file(dataset, "qrels.tsv"), encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            qid, docid, rel = line.split("\t")
            if int(rel) > 0:
                pos.add((qid, docid))
    return pos


def frozen_judged_labels(dataset):
    """dict[(qid, docid)] -> 0/1 for every candidate the frozen run judged.

    A judged pair is 1 if it is a positive in qrels.tsv, else 0. (Forced-source
    positives that were never judged are NOT included here -- this is strictly the
    LLM-judged set, so pooled_qrels can reuse it to avoid duplicate judging.)
    """
    _, pairs = judged_pairs(dataset)
    pos = positives(dataset)
    return {(qid, docid): (1 if (qid, docid) in pos else 0) for (qid, docid) in pairs}


def build(dataset):
    bpath, pairs = judged_pairs(dataset)
    judged = set(pairs)
    pos = positives(dataset)

    negatives = sorted(judged - pos)          # judged, labeled 0
    pos_in_pool = judged & pos                # judged, labeled 1
    pos_not_judged = pos - judged             # positives absent from judged pool (forced source, etc.)

    # How many positives are the forced seed/source chunk of their query?
    forced_source = {(q, d) for (q, d) in pos if source_chunk_id(q) == d}

    adir = C.analysis_dir(dataset)
    neg_path = os.path.join(adir, "implicit_negatives.tsv")
    with open(neg_path, "w", encoding="utf-8") as f:
        for qid, docid in negatives:
            f.write(f"{qid}\t{docid}\t0\n")

    summary = {
        "dataset": dataset,
        "batch_request_file": os.path.relpath(bpath, C.REPO_ROOT),
        "n_queries": len({q for q, _ in pairs}),
        "judged_candidates": len(judged),
        "positives_total": len(pos),
        "positives_in_judged_pool": len(pos_in_pool),
        "positives_not_in_pool": len(pos_not_judged),
        "implicit_negatives": len(negatives),
        "forced_source_positives": len(forced_source),
        "implicit_negatives_file": os.path.relpath(neg_path, C.REPO_ROOT),
    }
    with open(os.path.join(adir, "qrels_reconstruction_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    return summary


def main():
    rows = []
    for ds in C.DATASETS:
        s = build(ds)
        rows.append(s)
        print(f"[reconstruct] {ds}: judged={s['judged_candidates']} "
              f"pos={s['positives_total']} (in-pool={s['positives_in_judged_pool']}, "
              f"forced_source={s['forced_source_positives']}) "
              f"neg={s['implicit_negatives']} -> {s['implicit_negatives_file']}")
    print("\n=== reconstruction summary ===")
    print(f"{'dataset':16s} {'judged':>7s} {'pos':>5s} {'neg':>5s} {'forced_src':>11s}")
    for s in rows:
        print(f"{s['dataset']:16s} {s['judged_candidates']:7d} {s['positives_total']:5d} "
              f"{s['implicit_negatives']:5d} {s['forced_source_positives']:11d}")


if __name__ == "__main__":
    main()
