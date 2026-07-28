"""
Query-level uncertainty estimation: the pipeline's statistical decision-support stage.

The benchmark ranks embedding models by point estimates, but a point estimate does not
say whether a corpus actually separates two candidates. This module resamples the
per-query metric values to answer that, and it is what makes the dataset report carry
uncertainty rather than only the cross-dataset aggregate.

Two kinds of interval are produced, and they answer different questions:

  * marginal - how much one model's score moves under query resampling. These are wide
    and overlap heavily, because every model on a corpus shares that corpus's query
    difficulty.
  * paired   - resamples the per-query *differences* against the corpus's own leading
    model, which cancels that shared variation. This is the interval that discriminates.
    Overlap between two marginal intervals is not evidence that the models perform alike.

Determinism. Every (dataset, model, metric) cell draws from its own SeedSequence stream
derived from cfg.random_seed, so a corpus's intervals never depend on how many datasets
were evaluated, in what order, or which metrics were enabled. Re-running one dataset
alone reproduces the same numbers as running all of them.

Inputs are artifacts the pipeline already writes: datasets/<name>/analysis/rankings_<Mn>.jsonl
(persisted during evaluation) and the qrels TSV. Nothing is re-embedded and no LLM is called.

The per-query metric formulas reproduce the semantics of
sentence_transformers.evaluation.InformationRetrievalEvaluator for binary relevance at a
single cutoff k, so mean(per-query) equals the published dataset-level aggregate. This is
enforced by the consistency gate in analysis/query_level_eval.py.
"""
import os
import math
import json

import numpy as np

import config as cfg

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Metric keys in the same stable order the pipeline reports them.
METRICS = ["map", "recall", "precision", "ndcg", "mrr", "hit_rate"]

# Metric used to pick each corpus's leading model and to pair against.
PRIMARY_METRIC = "map"


# --------------------------------------------------------------------------------------
# Model labels
# --------------------------------------------------------------------------------------

def model_names():
    """Full sentence-transformers model names in configured order."""
    return [m["model_name"] for m in cfg.embedding_models]


def label_for(model_name):
    """Return the M1..M5 label for a full sentence-transformers model name."""
    return "M%d" % (model_names().index(model_name) + 1)


def label_map():
    """{full model name: M1..M5}."""
    return {name: "M%d" % (i + 1) for i, name in enumerate(model_names())}


# --------------------------------------------------------------------------------------
# Deterministic per-cell seeding
# --------------------------------------------------------------------------------------

def cell_rng(seed, *keys):
    """A generator whose stream depends only on (seed, keys), not on call order.

    Every bootstrap cell derives its own stream this way, which is what makes the
    output independent of how many datasets/metrics were processed in this run.
    Keys must be small non-negative ints that are stable across runs.
    """
    entropy = 0 if seed is None else int(seed)
    return np.random.default_rng(np.random.SeedSequence(entropy=entropy,
                                                        spawn_key=tuple(int(k) for k in keys)))


def _dataset_key(dataset):
    """Stable small int for a dataset name, independent of discovery order."""
    h = 0
    for ch in dataset:
        h = (h * 131 + ord(ch)) % 1000003
    return h


def _metric_key(metric):
    return METRICS.index(metric) if metric in METRICS else len(METRICS)


def _model_key(label):
    try:
        return int(label[1:])
    except (ValueError, IndexError):
        return 0


# --------------------------------------------------------------------------------------
# Per-query metrics (ST-matching)
# --------------------------------------------------------------------------------------

def per_query_metrics(ranked_ids, relevant_set, k):
    """Binary-relevance IR metrics for ONE query at cutoff k.

    ranked_ids   : doc_ids ordered best-first.
    relevant_set : set of relevant doc_ids for this query.
    Returns a dict over METRICS, or None when the query has no relevant docs
    (matching InformationRetrievalEvaluator, which drops such queries).
    """
    R = len(relevant_set)
    if R == 0:
        return None

    topk = ranked_ids[:k]
    rel_flags = [1 if d in relevant_set else 0 for d in topk]
    num_in_topk = sum(rel_flags)

    # Success@k / accuracy@k: 1 if any relevant retrieved in top-k
    hit_rate = 1.0 if num_in_topk > 0 else 0.0

    # Precision@k (denominator = k) and Recall@k (denominator = |R|)
    precision = num_in_topk / k
    recall = num_in_topk / R

    # MRR@k: reciprocal rank of first relevant hit within top-k
    mrr = 0.0
    for rank, flag in enumerate(rel_flags):
        if flag:
            mrr = 1.0 / (rank + 1)
            break

    # NDCG@k: binary gains, ideal DCG over min(|R|, k) relevant docs
    dcg = sum(rel_flags[i] / math.log2(i + 2) for i in range(len(rel_flags)))
    idcg = sum(1.0 / math.log2(i + 2) for i in range(min(R, k)))
    ndcg = (dcg / idcg) if idcg > 0 else 0.0

    # MAP@k (average precision at k): sum of precision-at-hit / min(k, |R|)
    num_correct = 0
    ap = 0.0
    for rank, flag in enumerate(rel_flags):
        if flag:
            num_correct += 1
            ap += num_correct / (rank + 1)
    ap = ap / min(k, R)

    return {
        "map": ap,
        "recall": recall,
        "precision": precision,
        "ndcg": ndcg,
        "mrr": mrr,
        "hit_rate": hit_rate,
    }


# --------------------------------------------------------------------------------------
# Loading stored rankings
# --------------------------------------------------------------------------------------

def analysis_dir(dataset):
    """datasets/<dataset>/analysis/ (created if missing). Never reports/."""
    d = os.path.join(REPO_ROOT, "datasets", dataset, "analysis")
    os.makedirs(d, exist_ok=True)
    return d


def rankings_path(dataset, label):
    return os.path.join(analysis_dir(dataset), "rankings_%s.jsonl" % label)


def read_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_rankings(dataset, label):
    return read_jsonl(rankings_path(dataset, label))


def score_dataset(dataset, qrels_path=None, k=None):
    """Per-query and aggregate metrics for each model, from stored rankings + qrels.

    Returns {label: {"per_query": {metric: [...]}, "qids": [...], "aggregate": {metric: mean}}}.
    Raises FileNotFoundError if the rankings for a model have not been persisted yet.
    """
    from utils.document_loader import load_ground_truth

    cfg.configure_for_dataset(dataset)
    k = cfg.k if k is None else k
    qrels_path = cfg.qrels_file if qrels_path is None else qrels_path
    _, _, relevant = load_ground_truth(cfg.corpus_file, cfg.queries_file, qrels_path)

    out = {}
    for m in cfg.embedding_models:
        label = label_for(m["model_name"])
        path = rankings_path(dataset, label)
        if not os.path.exists(path):
            raise FileNotFoundError(
                "Missing per-query rankings: %s. Run the evaluation stage first "
                "(python rag_benchmark.py --initialize --evaluate --dataset %s)." % (path, dataset)
            )
        per_q = {metric: [] for metric in METRICS}
        qids = []
        for row in load_rankings(dataset, label):
            rel = relevant.get(row["query_id"])
            if not rel:
                continue  # evaluator drops queries with no relevant docs
            pm = per_query_metrics(row["ranked_ids"], rel, k)
            for metric in METRICS:
                per_q[metric].append(pm[metric])
            qids.append(row["query_id"])
        agg = {metric: (sum(v) / len(v) if v else 0.0) for metric, v in per_q.items()}
        out[label] = {"per_query": per_q, "qids": qids, "aggregate": agg}
    return out


# --------------------------------------------------------------------------------------
# Bootstrap primitives
# --------------------------------------------------------------------------------------

def percentile_ci(values, rng, B, alpha):
    """Percentile bootstrap interval for the mean of `values`."""
    v = np.asarray(values, dtype=float)
    n = len(v)
    if n == 0:
        return 0.0, 0.0, 0.0
    idx = rng.integers(0, n, size=(B, n))
    means = v[idx].mean(axis=1)
    lo, hi = np.percentile(means, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return float(v.mean()), float(lo), float(hi)


def paired_ci(a, b, rng, B, alpha):
    """Paired bootstrap of mean(a - b), with a two-sided bootstrap p-value.

    Pairing at the query level cancels the shared query-difficulty variation that
    makes the two marginal intervals overlap.
    """
    d = np.asarray(a, dtype=float) - np.asarray(b, dtype=float)
    n = len(d)
    if n == 0:
        return 0.0, 0.0, 0.0, 1.0
    idx = rng.integers(0, n, size=(B, n))
    md = d[idx].mean(axis=1)
    lo, hi = np.percentile(md, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    p = 2.0 * min((md <= 0).mean(), (md >= 0).mean())
    return float(d.mean()), float(lo), float(hi), float(min(p, 1.0))


def excludes_zero(entry):
    return entry["lo"] > 0 or entry["hi"] < 0


# --------------------------------------------------------------------------------------
# Stage entry points
# --------------------------------------------------------------------------------------

def _settings(B=None, alpha=None, seed=None):
    B = int(getattr(cfg, "bootstrap_resamples", 10000)) if B is None else int(B)
    if alpha is None:
        alpha = 1.0 - float(getattr(cfg, "bootstrap_confidence", 0.95))
    seed = getattr(cfg, "random_seed", 42) if seed is None else seed
    return B, float(alpha), seed


def compute_dataset_bootstrap(dataset, scored=None, qrels_path=None,
                              B=None, alpha=None, seed=None, reference="M5"):
    """Per-corpus uncertainty block for one dataset.

    Schema (unchanged from the re-analysis layer so existing consumers keep working):
        {n_queries, leader, ci, paired_map_vs_<reference>, paired_map_vs_leader}
    """
    B, alpha, seed = _settings(B, alpha, seed)
    if scored is None:
        scored = score_dataset(dataset, qrels_path)

    labels = sorted(scored.keys())
    ds_key = _dataset_key(dataset)
    out = {
        "n_queries": len(scored[labels[0]]["qids"]) if labels else 0,
        "ci": {},
        "paired_map_vs_%s" % reference: {},
        "paired_map_vs_leader": {},
    }

    # marginal intervals: one independent stream per (dataset, model, metric)
    for lab in labels:
        out["ci"][lab] = {}
        for metric in METRICS:
            rng = cell_rng(seed, ds_key, _model_key(lab), _metric_key(metric), 0)
            mean, lo, hi = percentile_ci(scored[lab]["per_query"][metric], rng, B, alpha)
            out["ci"][lab][metric] = {"mean": mean, "lo": lo, "hi": hi}

    prim = {lab: scored[lab]["per_query"][PRIMARY_METRIC] for lab in labels}

    # paired against a fixed reference model, kept for cross-corpus comparability
    if reference in prim:
        for lab in labels:
            if lab == reference:
                continue
            rng = cell_rng(seed, ds_key, _model_key(lab), _metric_key(PRIMARY_METRIC), 1)
            delta, lo, hi, p = paired_ci(prim[reference], prim[lab], rng, B, alpha)
            out["paired_map_vs_%s" % reference][lab] = {
                "delta": delta, "lo": lo, "hi": hi, "p": p}

    # paired against this corpus's own leader: the decision-support column
    leader = max(prim, key=lambda k: float(np.mean(prim[k]))) if prim else None
    out["leader"] = leader
    if leader is not None:
        for lab in labels:
            if lab == leader:
                continue
            rng = cell_rng(seed, ds_key, _model_key(lab), _metric_key(PRIMARY_METRIC), 2)
            delta, lo, hi, p = paired_ci(prim[leader], prim[lab], rng, B, alpha)
            out["paired_map_vs_leader"][lab] = {"delta": delta, "lo": lo, "hi": hi, "p": p}

    return out


def compute_pooled_bootstrap(per_dataset_vectors, B=None, alpha=None, seed=None,
                             reference="M5"):
    """Aggregate uncertainty over every scored query of every dataset.

    per_dataset_vectors: {dataset: {label: [per-query primary-metric values]}}

    This estimator is UNSTRATIFIED - it resamples uniformly from the flat concatenated
    vector and does not preserve each corpus's share of the queries, so between-corpus
    composition variance is folded into the interval widths. It is also a pooled mean
    over all queries, which is not the same as the unweighted macro mean of the three
    corpus means used elsewhere in the reports.
    """
    B, alpha, seed = _settings(B, alpha, seed)

    pooled = {}
    for dataset in sorted(per_dataset_vectors):
        for lab, vals in per_dataset_vectors[dataset].items():
            pooled.setdefault(lab, []).extend(vals)

    out = {
        "n_queries": max((len(v) for v in pooled.values()), default=0),
        "stratified": False,
        "estimator": "pooled_mean_over_all_scored_queries",
        "ci_map": {},
        "paired_map_vs_%s" % reference: {},
        "paired_map_vs_leader": {},
    }

    for lab in sorted(pooled):
        rng = cell_rng(seed, 0, _model_key(lab), _metric_key(PRIMARY_METRIC), 3)
        mean, lo, hi = percentile_ci(pooled[lab], rng, B, alpha)
        out["ci_map"][lab] = {"mean": mean, "lo": lo, "hi": hi}

    if reference in pooled:
        for lab in sorted(pooled):
            if lab == reference:
                continue
            rng = cell_rng(seed, 0, _model_key(lab), _metric_key(PRIMARY_METRIC), 4)
            delta, lo, hi, p = paired_ci(pooled[reference], pooled[lab], rng, B, alpha)
            out["paired_map_vs_%s" % reference][lab] = {
                "delta": delta, "lo": lo, "hi": hi, "p": p}

    leader = max(pooled, key=lambda k: float(np.mean(pooled[k]))) if pooled else None
    out["leader"] = leader
    if leader is not None:
        for lab in sorted(pooled):
            if lab == leader:
                continue
            rng = cell_rng(seed, 0, _model_key(lab), _metric_key(PRIMARY_METRIC), 5)
            delta, lo, hi, p = paired_ci(pooled[leader], pooled[lab], rng, B, alpha)
            out["paired_map_vs_leader"][lab] = {"delta": delta, "lo": lo, "hi": hi, "p": p}

    return out


def pooled_over_datasets(datasets, qrels_paths=None, B=None, alpha=None, seed=None):
    """Score each dataset from its stored rankings, then pool. Returns (block, vectors).

    Shared by the aggregate report and the forest-plot figure so both read the same
    numbers without either depending on a file the other happens to have written.
    """
    qrels_paths = qrels_paths or {}
    vectors = {}
    for dataset in datasets:
        scored = score_dataset(dataset, qrels_paths.get(dataset))
        vectors[dataset] = {lab: scored[lab]["per_query"][PRIMARY_METRIC] for lab in scored}
    return compute_pooled_bootstrap(vectors, B=B, alpha=alpha, seed=seed), vectors


def bootstrap_output_path(dataset, variant="frozen"):
    """datasets/<dataset>/analysis/bootstrap_<variant>.json.

    `variant` names the qrels construction, not the snapshot: "frozen" is the
    dataset's own qrels.tsv as written by the qrels stage.
    """
    return os.path.join(analysis_dir(dataset), "bootstrap_%s.json" % variant)


def run_dataset_stage(dataset, qrels_path=None, variant="frozen", verbose=True):
    """Compute and persist the per-corpus uncertainty block. Returns the block."""
    B, alpha, seed = _settings()
    scored = score_dataset(dataset, qrels_path)
    block = compute_dataset_bootstrap(dataset, scored=scored, B=B, alpha=alpha, seed=seed)
    block["B"] = B
    block["confidence"] = round(1.0 - alpha, 4)
    block["seed"] = seed

    path = bootstrap_output_path(dataset, variant)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(block, f, indent=2)

    if verbose:
        leader = block.get("leader")
        print("Query-level uncertainty: %d scored queries, B=%d, leader %s -> %s"
              % (block["n_queries"], B, leader, path))
        for lab in sorted(block["ci"]):
            m = block["ci"][lab][PRIMARY_METRIC]
            line = "  %s: %.4f [%.4f, %.4f]" % (lab, m["mean"], m["lo"], m["hi"])
            pr = block["paired_map_vs_leader"].get(lab)
            if pr:
                line += "   %s-%s %+.4f [%+.4f, %+.4f] %s" % (
                    leader, lab, pr["delta"], pr["lo"], pr["hi"],
                    "separated" if excludes_zero(pr) else "NOT separated")
            print(line)
    return block, scored
