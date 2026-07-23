"""
Build model-INDEPENDENT pooled qrels to correct the M5 candidate-pool bias.

Protocol (TREC-style pooling):
  1. For each query, take the top-`candidate_pool_size` chunks retrieved by EVERY
     model (from the persisted rankings) and union them (dedup) -> the pooled
     candidate set. No single evaluated model privileges the ground truth.
  2. Judge the FULL union fresh with the same Gemini judge + prompt the frozen run
     used, via the Batch API (free-tier RPM/RPD make synchronous judging infeasible).
  3. Assemble two qrels files storing BOTH positive and explicit negative labels:
       - qrels_pooled.tsv        : union judged normally (source chunk NOT forced) -- primary/unbiased
       - qrels_pooled_forced.tsv : union + seed/source chunk forced to 1 (apples-to-apples with frozen method)
     The frozen datasets/<name>/qrels.tsv is the untouched third comparison point.

All artifacts live under datasets/<name>/analysis/ (incl. the BatchManager history
and batch files, by redirecting cfg.reports_dir). The frozen reports/ dir is untouched.

Subcommands:
  --plan     size the pooled union + judging budget (NO LLM spend)
  --submit   submit one Batch API job per dataset (spends LLM budget)
  --status   poll submitted batch jobs
  --fetch    download results, judge-parse, write pooled qrels variants
"""
import os
import sys
import json
import argparse

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (_ROOT, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import common as C  # noqa: E402
import config as cfg  # noqa: E402
from utils.document_loader import load_corpus, load_queries  # noqa: E402
from query_level_eval import load_rankings  # noqa: E402
from reconstruct_negatives import source_chunk_id, frozen_judged_labels  # noqa: E402


def build_union(dataset):
    """Return (corpus, queries, pool) where pool[qid][docid] = best rank across models.
    The union uses each model's top candidate_pool_size chunks from persisted rankings.
    """
    cfg.configure_for_dataset(dataset)
    corpus = load_corpus(cfg.corpus_file)
    queries = load_queries(cfg.queries_file)
    pool = {}
    for m in cfg.embedding_models:
        label = C.label_for(m["model_name"])
        for row in load_rankings(dataset, label):
            qid = row["query_id"]
            dd = pool.setdefault(qid, {})
            for rank, docid in enumerate(row["ranked_ids"][:cfg.candidate_pool_size], start=1):
                if docid not in dd or rank < dd[docid]:
                    dd[docid] = rank
    return corpus, queries, pool


def union_pairs_in_order(queries, pool):
    """(qid, docid, best_rank) ordered by query then ascending best rank."""
    out = []
    for qid in queries:
        for docid, rank in sorted(pool.get(qid, {}).items(), key=lambda kv: (kv[1], kv[0])):
            out.append((qid, docid, rank))
    return out


def plan(dataset):
    corpus, queries, pool = build_union(dataset)
    pairs = union_pairs_in_order(queries, pool)
    frozen = frozen_judged_labels(dataset)  # M5-pool pairs already judged in frozen run
    overlap = sum(1 for (q, d, _) in pairs if (q, d) in frozen)
    adir = C.analysis_dir(dataset)
    rows = [{"query_id": qid,
             "candidates": [{"doc_id": d, "best_rank": r}
                            for (q, d, r) in pairs if q == qid]}
            for qid in queries]
    C.write_jsonl(os.path.join(adir, "pool_union.jsonl"), rows)
    sizes = [len(pool.get(qid, {})) for qid in queries]
    info = {
        "dataset": dataset,
        "n_queries": len(queries),
        "union_pairs_total": len(pairs),
        "avg_union_per_query": round(sum(sizes) / len(sizes), 2),
        "min_union_per_query": min(sizes),
        "max_union_per_query": max(sizes),
        "already_judged_by_frozen_M5_pool": overlap,
        "new_if_reusing_frozen": len(pairs) - overlap,
    }
    with open(os.path.join(adir, "pool_plan.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2)
    return info


def submit(dataset):
    corpus, queries, pool = build_union(dataset)
    pairs = union_pairs_in_order(queries, pool)
    adir = C.analysis_dir(dataset)
    cfg.reports_dir = adir  # redirect BatchManager history/batch files into analysis/
    from utils.batch_manager import BatchManager
    bm = BatchManager()
    requests = []
    for qid, docid, rank in pairs:
        text = corpus.get(docid, "")
        prompt = f'Question: {queries[qid]}\n{rank}. [{docid}] "{text}"\n\n'
        requests.append(bm.prepare_request(f"{qid}|||{docid}", prompt,
                                           cfg.generate_qrels_system_instruction, cfg.temperature))
    print(f"[submit] {dataset}: {len(requests)} judgments")
    job = bm.submit_batch(requests, "pooled_qrels_gen")
    if not job:
        print(f"[submit] {dataset}: submission FAILED")
        return None
    with open(os.path.join(adir, "pooled_job.json"), "w", encoding="utf-8") as f:
        json.dump({"dataset": dataset, "job": job, "n_requests": len(requests)}, f, indent=2)
    print(f"[submit] {dataset}: job={job}")
    return job


def _job_for(dataset):
    p = os.path.join(C.analysis_dir(dataset), "pooled_job.json")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def status(dataset):
    rec = _job_for(dataset)
    if not rec:
        print(f"[status] {dataset}: no submitted job")
        return None
    cfg.configure_for_dataset(dataset)
    cfg.reports_dir = C.analysis_dir(dataset)
    from utils.batch_manager import BatchManager
    st = BatchManager().check_status(rec["job"])
    print(f"[status] {dataset}: {st}  ({rec['job']})")
    return st


def fetch(dataset):
    rec = _job_for(dataset)
    if not rec:
        print(f"[fetch] {dataset}: no submitted job")
        return False
    corpus, queries, pool = build_union(dataset)
    adir = C.analysis_dir(dataset)
    cfg.reports_dir = adir
    from utils.batch_manager import BatchManager
    results = BatchManager().download_results(rec["job"])
    if not results:
        print(f"[fetch] {dataset}: results not ready")
        return False

    labels = {}
    for res in results:
        key = res.get("custom_id") or res.get("key")
        if not key or "|||" not in key:
            continue
        qid, docid = key.split("|||", 1)
        labels[(qid, docid)] = C.parse_relevance_score(C.extract_response_text(res))

    pairs = union_pairs_in_order(queries, pool)
    for qid, docid, _ in pairs:
        labels.setdefault((qid, docid), 0)  # any missing judgment defaults to non-relevant

    # qrels_pooled.tsv : union, judged normally, explicit 0/1
    pooled_path = os.path.join(adir, "qrels_pooled.tsv")
    n_pos = 0
    with open(pooled_path, "w", encoding="utf-8") as f:
        for qid, docid, _ in pairs:
            lab = labels[(qid, docid)]
            n_pos += 1 if lab > 0 else 0
            f.write(f"{qid}\t{docid}\t{lab}\n")

    # qrels_pooled_forced.tsv : same + seed/source chunk forced to 1
    forced = {(qid, docid): labels[(qid, docid)] for qid, docid, _ in pairs}
    for qid in queries:
        src = source_chunk_id(qid)
        if src:
            forced[(qid, src)] = 1
    forced_path = os.path.join(adir, "qrels_pooled_forced.tsv")
    n_pos_forced = 0
    with open(forced_path, "w", encoding="utf-8") as f:
        for (qid, docid) in sorted(forced.keys()):
            lab = forced[(qid, docid)]
            n_pos_forced += 1 if lab > 0 else 0
            f.write(f"{qid}\t{docid}\t{lab}\n")

    summary = {
        "dataset": dataset,
        "job": rec["job"],
        "union_pairs": len(pairs),
        "pooled_positives": n_pos,
        "pooled_negatives": len(pairs) - n_pos,
        "forced_positives": n_pos_forced,
        "qrels_pooled": os.path.relpath(pooled_path, C.REPO_ROOT),
        "qrels_pooled_forced": os.path.relpath(forced_path, C.REPO_ROOT),
    }
    with open(os.path.join(adir, "pooled_qrels_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"[fetch] {dataset}: union={len(pairs)} pooled_pos={n_pos} "
          f"pooled_neg={len(pairs) - n_pos} forced_pos={n_pos_forced}")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--dataset", default=None)
    args = ap.parse_args()
    targets = [args.dataset] if args.dataset else C.DATASETS

    if args.plan:
        infos = [plan(ds) for ds in targets]
        print("\n=== POOLED-QRELS PLAN (no LLM spend) ===")
        print(f"{'dataset':16s} {'queries':>7s} {'union':>6s} {'avg/q':>6s} "
              f"{'min':>4s} {'max':>4s} {'frozenM5':>9s} {'new_if_reuse':>12s}")
        tot = 0
        for i in infos:
            tot += i["union_pairs_total"]
            print(f"{i['dataset']:16s} {i['n_queries']:7d} {i['union_pairs_total']:6d} "
                  f"{i['avg_union_per_query']:6.1f} {i['min_union_per_query']:4d} "
                  f"{i['max_union_per_query']:4d} {i['already_judged_by_frozen_M5_pool']:9d} "
                  f"{i['new_if_reusing_frozen']:12d}")
        print(f"TOTAL union pairs to judge fresh: {tot}")
    if args.submit:
        for ds in targets:
            submit(ds)
    if args.status:
        for ds in targets:
            status(ds)
    if args.fetch:
        for ds in targets:
            fetch(ds)


if __name__ == "__main__":
    main()
